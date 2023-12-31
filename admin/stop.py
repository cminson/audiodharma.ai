#!/usr/bin/python
import psutil

process_name = "sophia.py"  
for proc in psutil.process_iter(['pid', 'name']):
    if proc.info['name'] == process_name:
        proc.terminate()
        print("Sophia terminated")
        break

print("Sophia not running")
