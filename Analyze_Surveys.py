#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script opens and analyzes data from the .pcap
files created by the Lidar when it takes a survey. Most
of this should be included in the automated code that runs
in Run_Surveys.py, but this space allows for "offline" testing.

Created on Fri Sep 16 15:50:36 2022

@author: Michael Itzkin
"""

from LidarScan import LidarScan


"""
Run the program
"""

def main():
    """
    Run the program
    """
    
    # Load in a scan
    fname = 'Office Scan 2022-09-16 05:00:00.002905'
    lidar_data = LidarScan(fname)
    print(lidar_data.date_time)


if __name__ == '__main__':
    main()
