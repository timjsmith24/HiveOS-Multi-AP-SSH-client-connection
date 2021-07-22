# HiveOS Multi AP SSH client connection
## XIQ_SSH_client_connection.py
### Purpose
This script will open a SSH session with multiple APs (up to 10), and run the command 'show station [MAC ADDRESS]' on each AP. The output of the AP the client is currently connected will be shown on the screen. When the client roams to a new AP the script will display a message about the roam and continue to show the statistics from the newly connected AP. This script should help provide information about client roaming. 

## User Input Data
#### SSH login info
The username and password for the SSH session will need to be entered.
###### lines 15-16
```
username = 'admin'
password = 'Extreme123!'
```
#### AP info
The IP addresses and ports of the APs to be connected to. Each set should be placed in ()'s and all but the last should be followed by a ,. 
>###### NOTE:
>if more than 10 APs are added to this list, SSH sessions will only be connected to the first 10
###### lines 18-20+
```
device_list = [
    ('34.202.197.48','20106'),
    ('34.202.197.48','20059')
]
```
#### client mac address
When running the script from terminal add the mac address after the script name
```
python3 XIQ_SSH_client_connection.py 0E6C82A1787E
```

## Script Outputs
#### Terminal Window

<p align="center">
<img scr="../master/images/XIQ_SSH_client_connection_output.png" alt="XIQ client connection output" height="400px">
</p>

#### Log file
All roams will be logged to a file [MAC ADDRESS]--([DATE]).log

> 0E6C82A1787E--(2021-07-22).log

This will include the last info of the client before the roam and the first info from the new AP after the roam.


## Requirements
This script was written for Python 3. The Paramiko module will need to be installed in order for the script to function. Paramiko is listed in the requirements.txt file.
