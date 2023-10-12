#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script records and stores hourly LiDAR scans using the paraview
Python library and a cron job

Created on Tue Oct  3 11:27:12 2023

@author: argus_user
"""

from Functions.LidarSurvey import LidarSurvey

import datetime as dt
import os

##############################################################################

def main():
    """
    Run the program
    """
    
    # Set the current time
    current_time = dt.datetime.now().strftime('%Y%m%d%H')
    
    # Set parameters for the Lidar and initialize the LidarSurvey object
    PROJECT_DIR = os.path.join('..', 'Projects', 'Office_Scan')
    fname = os.path.join(PROJECT_DIR, f'Office Scan {current_time}.pcap')
    survey_time = 10  # Seconds
    ls = LidarSurvey(fname, survey_time)


    # Do the recording
    ls.record_stream()
   

if __name__ == '__main__':
    
    # These lines actually start and run the cron job. The '*/1' argument
    # passed to add_job() tells the schedule to run take_survey() every
    # hour at the top of the hour
    # scheduler = BackgroundScheduler(daemon=False)
    # scheduler.start()
    # scheduler.add_job(main, trigger='cron', minute='*')
    
    main()
