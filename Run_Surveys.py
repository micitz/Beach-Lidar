#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script sets the lidar to take a survey at the top of the hour
and save the .pcap file to the desired project directory

Created on Wed Sep 14 18:26:38 2022

@author: argus
"""

from apscheduler.schedulers.background import BackgroundScheduler
from paraview.simple import *

import datetime as dt
import time
import os

# Set the save directory
SAVE_DIR = os.path.join(r'/home', 'argus', 'Documents', 
                        'Lidar_Scans', 'Projects', 'Office_Testing')


def take_survey(name, survey_time):
    """
    This function is called by the cron job to take
    a LiDAR survey and perform any analysis that 
    can/should be done automatically after the survey(s)
    
    name: String with the name of the project for the survey files
    survey_time: Int with the number of seconds to run the scan for
    """
    
    # Make the survey. The time.sleep(N) dictates how long the
    # survey will be (in seconds). Note that a 10 second survey
    # produces a 20mb .pcap file.
    curr_time = dt.datetime.now()
    vv.recordFile(os.path.join(SAVE_DIR, '{} {}.pcap').format(name, curr_time))
    time.sleep(survey_time)
    vv.stopRecording()


def main():
    
    # Set these variables before running the script
    name = 'Office Scan'
    survey_time = 10    # Seconds!
    
    # These lines actually start and run the cron job. The '*/1' argument
    # passed to add_job() tells the schedule to run take_survey() every
    # hour at the top of the hour
    scheduler = BackgroundScheduler(daemon=False)
    scheduler.start()
    scheduler.add_job(take_survey, trigger='cron', minute='*/1',
                      args=(name, survey_time))
    
    # This try except keeps the scheduler running. Leave it here and don't modify!
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

if __name__ == '__main__':
    main()