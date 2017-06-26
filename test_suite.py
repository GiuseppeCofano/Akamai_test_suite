#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os
import shutil
from time import sleep

BW1 = [4000/8, 1000/8]
BW2 = [4000/8, 400/8]
BW3 = [2500/8, 1000/8]
BW = [BW1, BW2, BW3]
#bandwidth in KB/s
for i in range(0,len(BW)):
    if not BW[i][0] or not BW[i][1]:
        print "Missing bandwidth value..."
    else:
        DIR="Step" + "Down_" + str(BW[i][0]) + "-" + str(BW[i][1])
        os.mkdir(DIR)
        DMP="akamai_log_new.py"
        RUN="run_test"
        CHR="chrome_test.py"
        FIL="file"
        shutil.copy(DMP, DIR + "/" + DMP)
        shutil.copy(RUN, DIR + "/" + RUN)
        shutil.copy(CHR, DIR + "/" + CHR)
        shutil.copy(FIL, DIR + "/" + FIL)
        os.chdir(DIR)
        print "Starting test..."
        CMD="./run_test " + str(BW[i][0]) + " " + str(BW[i][1])
        os.system(CMD)
        sleep(5)
        CMD2="./akamai_log_new.py akamai.dump step"
        os.system(CMD2)
        os.chdir("..")


