#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script goes through the "un-processed" .pcap files
from the hourly cron jobs and processes them.

Created on Fri Sep 16 15:50:36 2022

@author: Michael Itzkin
"""

from Functions.LidarScan import LidarScan

from apscheduler.schedulers.background import BackgroundScheduler

import shutil
import tqdm
import glob
import os


"""
Run the program
"""

def main():
    """
    Run the program
    """
    
    # Identify any un-processed lidar scans in the project directory
    project_name = 'Office_Scan'
    project_folder = os.path.join('Projects', project_name)
    lidar_scans = glob.glob(os.path.join(project_folder, '*.pcap'))
    
    # Loop over the lidar scans
    print(f'Starting Processing: There are {len(lidar_scans)} scans to work on...')
    for scan in tqdm.tqdm(lidar_scans):
        
        # Setup the LidarScan object
        data = LidarScan(filename=scan, DATA_DIR=None)
        
        # Make a folder with the current scan's
        # datetime value as the folder name
        scan_folder = os.path.join(project_folder, str(data.date_time))
        if not os.path.isdir(scan_folder):
            os.makedirs(scan_folder)
        
        # Open the .pcap file and store it as a series of .csv files in
        # a folder that is specific to the current scan
        data.analyze_pcap(verbose=0)
        csv_files = glob.glob(os.path.join(project_folder, '*.csv'))
        [shutil.move(file, os.path.join(scan_folder)) for file in csv_files]
        
        # Move the .pcap file into the scan_folder too
        shutil.move(scan, scan_folder)
        
        
if __name__ == '__main__':
    
    # These lines actually start and run the cron job. The '*/1' argument
    # passed to add_job() tells the schedule to run take_survey() every
    # hour at the top of the hour
    scheduler = BackgroundScheduler(daemon=False)
    scheduler.start()
    scheduler.add_job(main, trigger='cron', hour=00, minute=30)
    
    # Need this to keep the interpreter from shutting down
    while True:
        pass

