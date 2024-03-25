#!/bin/sh
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
This script records and stores hourly LiDAR scans using the paraview
Python library and a cron job

1. Take a survey for a pre-determined number of seconds
2. Process the .pcap file produced by the lidar into .csv files
3. Organize the output files to save hard drive space


Created on Tue Oct  3 11:27:12 2023
@author: argus_user
"""

import lidarview.simple as lvsmp
import paraview.simple as smp

import datetime as dt
import numpy as np
import time
import os

# Set paths to the calibration file and the intepreter
calibration_file = r'/home/argus_user/Downloads/VeloView-5.1.0-Ubuntu18.04-x86_64/share/VLP-32c.xml'
interpreter = r"Velodyne Meta Interpreter"

# Set lidar parameters
port = 2368
orientation = [0, -90, 0]
survey_time = 5 # 60 * 10


#----------------------------------------------------------------------------#


def clean_up_survey(input_dir, location, scan_time, lidar_height,
                    SKIP_FILES=10,
                    CHUNK_SIZE=5000,
                    just_point_cloud=False):
    """
    Load the survey output data and store it as a .csv file, 
    then go and delete the original scan files
    
    input_dir: String with the path to the survey to process
    location: String with the survey location name
    scan_time: Datetime object with the timing of the survey
    lidar_height: Numeric value with the height of the lidar in meters
    SKIP_FILES: Int with the number of .csv files to skip over when processing
    CHUNK_SIZE: Int with the size of the "chunks" to break down the data into
    just_point_cloud: Bool to just store the point cloud data
    """
    
    output_file = os.path.join(input_dir,
                               f'{location}_{scan_time.strftime("%b_%d_%Y_%H_%M")}.nc')
    
    # Compile the survey data into a single numpy array
    scan_data = []
    scan_files = os.listdir(input_dir)
    for csv_file_name in scan_files[::SKIP_FILES]:
        chunk_container = pd.read_csv(os.path.join(input_dir, csv_file_name),
                                      chunksize=CHUNK_SIZE)
        for chunk in chunk_container:
            scan_data.append(chunk.to_numpy())
    scan_data = np.vstack(scan_data)
    
    # Create a new netCDF4 file
    ncfile = nc.Dataset(output_file, mode='w')

    # Create the relevant dimensions
    points_dim = ncfile.createDimension('points', scan_data.shape[0])
    columns_dim = ncfile.createDimension('columns', 3)
    value_dim = ncfile.createDimension('value', 1)

    # Create attributes
    split_name = output_file.split(os.sep)[-1].split('_')
    ncfile.title = f'Lidar Survey Data for {location}'
    ncfile.survey_date = f'{scan_time.strftime("%B %d, %Y")} at {scan_time.hour}:{scan_time.minute}'
    ncfile.processed_date = dt.datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    # Just save the point cloud if desired
    if just_point_cloud:

        # Write the XYZ values
        xyz = ncfile.createVariable('XYZ', np.float64, ('points', 'columns',))
        xyz.units = 'm'
        xyz.Description = 'Point cloud XYZ data'
        xyz[:] = scan_data[:, 7:]

    else:

        # Write the laser intensity values
        intensity = ncfile.createVariable('Intensity', int, ('points', ))
        intensity.units = '%'
        intensity.Description = 'Percent of light reflected back to the lidar'
        intensity[:] = scan_data[:, 0]

        # Write the laser ID values
        laser_id = ncfile.createVariable('Laser_ID', int, ('points', ))
        laser_id.units = 'None'
        laser_id.Description = 'Laser ID number in the order "fired", not sequential along the column of lasers'
        laser_id[:] = scan_data[:, 1]

        # Write the azimuth values
        azimuth = ncfile.createVariable('Azimuth', np.float64, ('points',))
        azimuth.units = 'Degrees'
        azimuth.Description = 'Azimuth angle (0-359.99) of the sensor when fired'
        azimuth[:] = scan_data[:, 2] * 1e-2

        # Write the distance_m values
        distance_m = ncfile.createVariable('Distance', np.float64, ('points',))
        distance_m.units = 'm'
        distance_m.Description = 'Distance of the point from the LiDAR sensor origin'
        distance_m[:] = scan_data[:, 3]

        if np.all(scan_data[:, 4] == scan_data[:, 5]):
            print('Adjusted time equals Timestamp, just saving the timestamp')
        else:

            # Write the adjusted_time values
            adjusted_time = ncfile.createVariable('Adjusted_Time', np.float64, ('points',))
            adjusted_time.units = 'microseconds'
            adjusted_time.Description = 'Microseconds since the top of the hour adjusted from the GPS input'
            adjusted_time[:] = scan_data[:, 4]

        # Write the time_stamp values
        time_stamp = ncfile.createVariable('Timestamp', np.float64, ('points',))
        time_stamp.units = 'microseconds'
        time_stamp.Description = 'Microseconds since the top of the hour adjusted from the GPS input'
        time_stamp[:] = scan_data[:, 5]

        # Write the vertical angle values
        vertical_angle = ncfile.createVariable('Vertical_Angle', np.float64, ('points',))
        vertical_angle.units = 'Degrees'
        vertical_angle.Description = 'Vertical angle of the laser'
        vertical_angle[:] = scan_data[:, 6]

        # Write the XYZ values
        xyz = ncfile.createVariable('XYZ', np.float64, ('points', 'columns', ))
        xyz.units = 'm'
        xyz.Description = 'Point cloud XYZ data'
        xyz[:] = scan_data[:, 7:]

    # Write a variable with the lidar elevation value
    lidar_elev_value = ncfile.createVariable('Lidar_Height', np.float64, 'value')
    lidar_elev_value.unit = 'meters'
    lidar_elev_value[:] = lidar_height

    # Close the open netCDF file
    ncfile.close()
    print('netCDF File Saved')


def crop_and_save(reader, filename):
    """
    Load in a .pcap file and save the frames as .csv files for analysis.
    This code is modified from th exmaple code at:
    https://gitlab.kitware.com/LidarView/lidarview-core/-/blob/master/Examples/Python/crop_and_export_example.py?ref_type=heads
    """
    
    fileDir = os.path.dirname(filename)
    basenameWithoutExtension = os.path.splitext(os.path.basename(filename))[0]
    filenameTemplate = os.path.join(fileDir, basenameWithoutExtension + '_%04d.csv')
    filenameCroppedTemplate = os.path.join(fileDir, basenameWithoutExtension + 'Cropped_%04d.csv')

    #set up filter for cropping
    threshold = smp.Threshold(registrationName='Threshold1', Input=reader)
    threshold.Scalars = ['POINTS', 'distance_m']

    ### Note : the below would be replaced by threshold.ThresholdRange = [0.0, 10.0] in former Paraview Versions ( such as in VV 5.1 )
    threshold.LowerThreshold = 0.0
    threshold.UpperThreshold = 10.0
    threshold.ThresholdMethod = 'Between'

    # Loop over the timesteps of interest
    time_steps = len(reader.TimestepValues)
    for time_step in range(0, time_steps):

        timestamp = reader.TimestepValues[time_step]
        smp.GetAnimationScene().AnimationTime = timestamp # or scene.GoToNext()

        threshold.UpdateVTKObjects()
        smp.UpdatePipeline(timestamp)

        filenameFull = filenameTemplate % time_step
        # filenameCropped = filenameCroppedTemplate % time_step

        smp.SaveData(filenameFull, proxy=reader, PointDataArrays=['adjustedtime', 'azimuth', 'distance_m', 'intensity', 'laser_id', 'timestamp', 'vertical_angle'])


def record_stream(fname, survey_time, pre_pause=1):
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
    
    # Initialize the stream
    stream = lvsmp.OpenSensorStream(calibration_file,
                                    interpreter,
                                    port,
                                    DetectFrameDropping=True,
                                    Rotate=orientation)
    print('----Recording stream initialized, starting recording----')
    
    # Start recording after a few seconds
    time.sleep(pre_pause)
    stream.RecordingFilename = fname
    stream.StartRecording()
    time.sleep(survey_time)
     
    # Stop Recording
    stream.StopRecording()
    print('----Recording Finished----')
    
    
#----------------------------------------------------------------------------#


def main():
    """
    Run the program
    """
    
    # Set the name of the project
    project_name = 'Madeira_Beach'
    
    # Set the current time
    current_time = dt.datetime.now()
    current_time_short = current_time.strftime('%Y%m%d%H%M')
    
    # Setup the .pcap file for the scan
    BASE_DIR = r'/home/argus_user/Documents/Lidar'
    PROJECT_DIR = os.path.join(BASE_DIR, 'Projects', project_name)
    fname_no_ext = f'{project_name} {current_time_short}'
    fname = os.path.join(PROJECT_DIR, f'{fname_no_ext}.pcap')

    # Do the recording
    record_stream(fname, survey_time)
    
    time.sleep(5)
   

if __name__ == '__main__':
    main()
