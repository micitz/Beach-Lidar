#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains a class definition to work with the
Velodyne Lidar

Created on Thu Oct  5 11:07:51 2023

@author: argus_user
"""

import lidarview.simple as lvsmp
import time


class LidarSurvey():
    """
    Define a class object to run and analyze lidar data
    """
    
    def __init__(self, output_fname, survey_time, orientation=[0, -90, 0],
                 port=2368, calibration_fname='VLP-32c.xml',
                 interpreter='Velodyne Meta Interpreter'):
        """
        Initialize the LidarSurvey object
        
        output_fname: String with the name of the output file from/for the scan
        survey_time: Int with the length of the scan [Seconds]
        orientation: List with the yaw, pitch, and roll of the lidar
            - Side scan should be [0, -90, 0]
            - Horizontal scan should be [0, 0, 0]
        port: Int with the listening port for the lidar. Don't change this
        calibration_fname: Calibration file for the lidar, don't change
        interpreter: Not sure, don't change
        """
        
        # Set parameters for the Lidar
        self.fname = output_fname
        self.calibration_fname = calibration_fname
        self.interpreter = interpreter
        self.port = port
        self.orientation = orientation
        self.survey_time = survey_time
        
    def record_stream(self, pre_pause=1, fname=None, survey_time=None):
        """
        Initialize and record the data stream from the lidar
        
        pre_pause: Int with the time to pause before recording [Seconds]
        fname: String with a filename to save the recording as. This overrides
               self.fname. No reason to do this unless the filename is being
               updated in a loop
        survey_time: Int with the number of seconds to record for. This 
                     overrides self.survey_time so there's no reason to set
                     this unless the survey times need to change over time
        """
        
        # Set the filename
        if fname:
            print(f'WARNING: Changing self.fname from {self.fname} to {fname}')
            self.fname = fname
            
        # Set the survey time
        if survey_time:
            print(f'WARNING: Changing self.survey_time from {self.survey_time} seconds to {survey_time} seconds')
            self.survey_time = survey_time
        
        # Initialize the stream
        stream = self._initialize_stream()
        print('----Recording stream initialized, starting recording----')
        
        # Start recording after a few seconds
        time.sleep(pre_pause)
        stream.RecordingFilename = self.fname
        stream.StartRecording()
        time.sleep(self.survey_time)
         
        # Stop Recording
        stream.StopRecording()
        print('----Recording Finished----')
        
    """
    Internal methods
    """
    
    def _initialize_stream(self):
        """
        Initialize the data stream for recording
        """
        
        stream = lvsmp.OpenSensorStream(self.calibration_fname,
                                        self.interpreter,
                                        self.port,
                                        DetectFrameDropping=True,
                                        Rotate=self.orientation)
        
        return stream
        

