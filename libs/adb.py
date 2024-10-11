#!/usr/bin/env python
# coding=utf-8

"""ADB"""

import subprocess
    
    
class adbKit(object):
    def __init__(self,serialNumber=None):
        self.serialNumber = serialNumber
        
    def screenshots(self):
        self.command(' exec-out screencap -p > ./screencap.png')



    def command(self, cmd):
        cmdstr = 'adb '
        if self.serialNumber:
            cmdstr = cmdstr + '-s ' + self.serialNumber + ' '
        cmdstr += cmd

        try:
            result = subprocess.run(cmdstr, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return [result.returncode, result.stdout]
        except subprocess.CalledProcessError as e:
            return [e.returncode, e.stderr]
        
    def click(self, point):
        return self.command('shell input tap '+str(point[0])+' '+str(point[1]))
    
    def swip(self, a,b,speed):
        return self.command(f'shell input swipe {a[0]} {a[1]} {b[0]} {b[1]} {speed}')
    
    def send_key_event(self, keycode):
        return self.command(f'shell input keyevent {keycode}',)