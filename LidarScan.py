#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the class definition for the LidarScan
object type that loads and helps analyze PCAP data from the lidar.

Created on Fri Sep 16 16:00:11 2022

@author: argus
"""

import datetime as dt
import os


# Set the data directory
DATA_DIR = os.path.join(r'/home', 'argus', 'Documents', 
                        'Lidar_Scans', 'Projects', 'Office_Testing')


class LidarScan():
    """
    Define a class object to hold
    and work with LiDAR data
    """
    
    def __init__(self, filename, DATA_DIR=DATA_DIR):
        """
        Initialize the LidarScan object
        
        filename: String with the filename of the .pcap file from the scan
        DATA_DIR: String with the directory of the lidar data. Defaults to the
                  folder with the office scans.
        """
        
        # Set the variables
        if '.pcap' in filename:
            self.fname = os.path.join(DATA_DIR, filename)
        else:
            self.fname = os.path.join(DATA_DIR, '{}.pcap'.format(filename))
            
        # The scan has a long timestamp in the filename. Pull
        # out the components here and store as class attributes
        self.date_time = self._get_time()
        
    """
    Internal class methods
    """
    
    def _get_time(self):
        """
        Get time values from the filename
        """
        
        # First, split the filename by the period character. Then
        # split by the system's path separator to get to the filename
        # that contains the date.
        [fname, frac_secs, extension] = self.fname.split('.')
        pieces = fname.split(os.path.sep)
        more_pieces = pieces[-1].split(' ')
        date, time = more_pieces[-2], more_pieces[-1]
        
        # Get the date time components and make a datetime object
        year, month, day = date.split('-')
        hour, minutes, seconds = time.split(':')
        return dt.datetime(year=int(year), month=int(month),
                                day=int(day), hour=int(hour), 
                                minute=int(minutes), second=int(seconds),
                                microsecond=int(frac_secs))
        
        
        
        
        
        
        
        
        