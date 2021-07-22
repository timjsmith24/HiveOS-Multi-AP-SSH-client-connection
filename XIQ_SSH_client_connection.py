#!/usr/bin/python3
import time
import datetime
import sys
import logging
import os
import argparse
import paramiko
import multiprocessing

from paramiko.ssh_exception import AuthenticationException, SSHException, BadHostKeyException

logging.getLogger("paramiko").setLevel(logging.WARNING)

username = 'admin'
password = 'Extreme123!'

device_list = [
    ('34.202.197.48','20087'),
    ('34.202.197.48','20171')
]

parser = argparse.ArgumentParser()
parser.add_argument('clientmac', help = 'The mac address of the client you want to show connection info')
args = parser.parse_args()
clientmac = args.clientmac

#clientmac = '0E6C82A1787E'

cmd = 'show station '

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

today = time.strftime("%Y-%m-%d")


#-------------------------
# logging file and info
PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename='{}/{}--({}).log'.format(PATH,clientmac,today),
    filemode='a',
    level=os.environ.get("LOGLEVEL", "INFO"),
    #format= '%(asctime)s: %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    format= '%(name)s - %(levelname)s - %(message)s'
)

def debug_print(msg, status):
    if status == "error":
        #print("ERROR: " + msg)
        logging.error(msg)
    elif status == "warning":
        #print("WARNING: " + msg)
        logging.warning(msg)
    elif status == 'info':
        #print("INFO: " + msg)
        logging.info(msg)



def ap_ssh(ip,port,mp_queue):
    capturing = True
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print (f"Establishing Connection with {ip}:{port}")
        ssh.connect(ip,port = port, username = username , password = password ,timeout=10)
        chan = ssh.invoke_shell()
    except AuthenticationException:
        sys.stdout.write(RED)
        sys.stdout.write("Authentication failed on " + ip + ", please verify your credentials:")
        sys.stdout.write(RESET)
    except SSHException as sshException:
        sys.stdout.write(RED)
        sys.stdout.write("Unable to establish SSH connection on " + ip + ": %s" % sshException)
        sys.stdout.write(RESET)
    except BadHostKeyException as badHostKeyException:
        sys.stdout.write(RED)
        sys.stdout.write("Unable to verify server's host key on " + ip + ": %s" % badHostKeyException)
        sys.stdout.write(RESET)
    except Exception as e:
        sys.stdout.write(RED)
        sys.stdout.write("Operation error on " + ip + ": %s\n" % e)	
        sys.stdout.write(RESET)
    else:
        time.sleep(1)
        x = chan.recv(9999)
        resp = x.decode("utf-8").splitlines()
        devicename = resp[-1].replace('#', '')
        chan.send('console page 0\n')
        time.sleep(1)
        resp = chan.recv(9999)
        chan.send(cmd+clientmac+'\n')
        x = chan.recv(1024)
        clientfound = False
        msg = ''
        firstRun = True
        try:
            while capturing:            
                x = chan.recv(64)
                if b'\r\n' == x:
                    continue
                if 'request station information failed because of station leave' in str(x):
                    if clientfound == True:
                        output = x.decode("utf-8") 
                        now = datetime.datetime.now()
                        mp_queue.put(f'{now.strftime("%Y-%m-%d %H:%M:%S")}: Roaming from {devicename}\t[{msg}]')
                    clientfound = False
                elif clientfound == False and 'request station information failed because of station leave' not in str(x) and len(x) > 50:
                    if not firstRun:
                        sys.stdout.write(GREEN)
                        sys.stdout.write(f"### Client roamed to {devicename} ###\n")
                        sys.stdout.write(RESET)
                        sys.stdout.flush()
                        output = x.decode("utf-8") 
                        now = datetime.datetime.now()
                        mp_queue.put(f'{now.strftime("%Y-%m-%d %H:%M:%S")}: Roaming to {devicename}\t[{output.rstrip()}]')
                    clientfound = True
                #print(f"LENGTH - {len(x)}", end= ' ')
                if len(x) == 0:
                    capturing = False
                if clientfound:
                    output = x.decode("utf-8") 
                    msg = output
                    sys.stdout.write(BLUE)
                    sys.stdout.write(f"{devicename}")
                    sys.stdout.write(RESET)
                    sys.stdout.write(f" {output}")
                    sys.stdout.flush()
                if firstRun:
                    firstRun = False
            sys.stdout.write(RED)
            sys.stdout.write(f"#### Lost connection to {devicename} ####\n")
            sys.stdout.write(RESET)
        except KeyboardInterrupt:
            print(f"\n\nExiting session on {ip}:{port}")
            return
        ssh.close()



def main():
    sizeofbatch = 10
    batch = device_list[0:sizeofbatch]
    mp_queue = multiprocessing.Queue()
    processes = []
    for ip_address, port in batch:
        p = multiprocessing.Process(target=ap_ssh,args=(ip_address,port, mp_queue))
        processes.append(p)
        p.start()
    for p in processes:
        try:
            p.join()
            p.terminate()
        except:
            print("\n\n#### Sessions disconnected ####")
    mp_queue.put('STOP')
    for line in iter(mp_queue.get, 'STOP'):
        debug_print(line, 'info')
    print("\n\nClosing Script")


if __name__ == '__main__':
    main()