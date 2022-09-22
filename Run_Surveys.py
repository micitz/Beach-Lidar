#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script sets the lidar to take a survey at the top of the hour
and save the .pcap file to the desired project directory

Created on Wed Sep 14 18:26:38 2022

@author: Michael Itzkin
"""

from apscheduler.schedulers.background import BackgroundScheduler
from paraview.simple import *

import datetime as dt
import os
import time

import logging
logging.basicConfig()


"""
Code to run the survey
"""


def take_survey(name, survey_time):
    """
    This function is called by the cron job to take
    a LiDAR survey and perform any analysis that 
    can/should be done automatically after the survey(s)
    
    name: String with the name of the project for the survey files
    survey_time: Int with the number of seconds to run the scan for
    """
    
    # Set the name of the project and make a new folder to store the data in
    project_name = name.replace(' ', '_')
    SAVE_DIR = os.path.join(r'/home', 'argus', 'Documents', 
                            'Lidar_Scans', 'Projects', project_name)
    if not(os.path.exists(SAVE_DIR)):
        os.makedirs(SAVE_DIR)
    
    # Make the survey. The time.sleep(N) dictates how long the
    # survey will be (in seconds). Note that a 10 second survey
    # produces a 20mb .pcap file.
    scan_filename = os.path.join(SAVE_DIR, '{}_{}.pcap'.format(project_name, dt.datetime.now()))
    vv.recordFile(scan_filename)
    time.sleep(survey_time)
    vv.stopRecording()


def main():
    """
    Run the surveying program
    """
    
    # Set these variables before running the script
    name = 'Office Scan'
    survey_time = 10    # Seconds!
    
    # These lines actually start and run the cron job. The '*/1' argument
    # passed to add_job() tells the schedule to run take_survey() every
    # hour at the top of the hour
    scheduler = BackgroundScheduler(daemon=False)
    scheduler.start()
    scheduler.add_job(take_survey, trigger='cron', hour='*/1',
                      args=(name, survey_time))
    
    # This try except keeps the scheduler running. Leave it here and don't modify!
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

# Run the program. "if __name__ == '__main__'" doesn't
# seem to work with VeloView's Python shell...
main()