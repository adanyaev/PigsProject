import subprocess
import sys
import time

command = [sys.executable, 'pigEvaluator.py', '-c', 'rtsp://vshec:Vs759153E@92.50.147.106:3082/live/main', '-d', 'Up', '--pig_detection_line_place', '0.4', '--pig_detection_line_width', '30', '--detection_model', '../best150']
command2 = [sys.executable, 'pigEvaluator.py', '-c', 'rtsp://vshec:Vs759153E@92.50.147.106:3082/live/main', '-d', 'Left', '--pig_detection_line_place', '0.8', '--pig_detection_line_width', '50', '--detection_model', '../best150']
sf = subprocess.Popen(command)
sf2 = subprocess.Popen(command2)
print(sf.pid)
print(sf2.pid)