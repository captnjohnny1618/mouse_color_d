#!/usr/bin/env python3

import sys
import os
import random
import daemon
import time
import psutil

import rivalcfg
from rivalcfg import cli
from rivalcfg import debug
from rivalcfg import list_supported_mice, list_available_mice, get_mouse


def GetColour(v,vmin,vmax):
    c = {}
    c["r"] = 1.0
    c["g"] = 1.0
    c["b"] = 1.0

    if (v < vmin):
        v = vmin
    if (v > vmax):
        v = vmax
        
    dv = vmax - vmin;

    if (v < (vmin + 0.25 * dv)):
        c["r"] = 0.0;
        c["g"] = 4.0 * (v - vmin) / dv;
    elif (v < (vmin + 0.5 * dv)):
        c["r"] = 0.0
        c["b"] = 1.0 + 4.0 * (vmin + 0.25 * dv - v) / dv;
    elif (v < (vmin + 0.75 * dv)):
        c["r"] = 4.0 * (v - vmin - 0.5 * dv) / dv;
        c["b"] = 0.0;
    else:
        c["g"] = 1.0 + 4.0 * (vmin + 0.75 * dv - v) / dv;
        c["b"] = 0.0;

    c["r"] = int(255*c["r"]);
    c["g"] = int(255*c["g"]);
    c["b"] = int(255*c["b"]);
    
    c = '#%02x%02x%02x' % (c["r"],c["g"],c["b"])

    return(c)

def main():
    update_interval = 0.5 #seconds
    secure_random = random.SystemRandom()

    available_mice = list(list_available_mice())
    if not available_mice:
        return None
    mouse = available_mice[0]
    try:
        mouse =  get_mouse(mouse.vendor_id,mouse.product_id)
    except IOError as error:
        print("W: The following mouse was found but rivalcfg was not able to open it:")  # noqa
        print("  * mouse: %s (%4X:%4X)" % mouse)
        print("  * error: %s" % error)
        print("\nPlease check that no other application is controlling this mouse and try to:")  # noqa
        print("  * unplug the mouse from the USB port,")
        print("  * wait few seconds,")
        print("  * and plug the mouse to the USB port again.\n")

    profile = mouse.profile
    option  = "set_color"

    buffer_size = 20;
    pointer = 0;
    usage_tally = [0.0]*buffer_size
    
    while(True):

        pointer = pointer%buffer_size
        usage_tally[pointer] = psutil.cpu_percent()/100.0

        pct = sum(usage_tally)/float(len(usage_tally))
        if pct > 0.25:
            update_interval = 0.05
        else:
            update_interval = 0.5
    
        c = GetColour(pct,0.0,1.0);
        value = [c]
        count = getattr(mouse, option)(*value)
        if count < 0:
            print("error occured")

        #cmd = "rivalcfg --color={}".format(secure_random.choice(colors))
        #cmd = "rivalcfg --color={}".format(c)
        count = mouse.save()
        if count < 0:
            print("error occured while saving config")

        pointer+=1
        time.sleep(update_interval)

with daemon.DaemonContext(stdout=sys.stdout,stderr=sys.stderr):
#with daemon.DaemonContext():
    main()
























    
