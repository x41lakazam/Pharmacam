## IPCCAP 
IPCCAP is the OPGAL program that reads data from the ThermAppMD Camera, the program normally outputs frames to /home/debian/opgal/dump, but I wrote a wrapper called `fifo_ccap` that outputs into a named pipe `/opt/eyerop/bin/camera_out`

### How to launch fifo_ccap:

To capture from ccap, you need to run `erop_proxy_cam` (Look at the exact command in `fire_proxy.sh`), and then you can launch `fifo_ccap` (look at the command in `fire_ccap.sh`)

## Scripts
In the `eyerop/scripts` folder, you will find a bunch of python scripts, see scripts/README.md for more information.
The main gui is called gui.py

## Troubleshoot


*`erop_proxy_cam` cannot run (Transfer timeout (1): 2):*
This error occurs when you launch `erop_proxy_cam` twice, if you close this program, you need to disconnect the camera and reconnect it.
