#!/bin/sh
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script takes the .csv files from a Lidar survey and stores them in a netCDF file

- This initial version of the script just takes the data and makes a netCDF
  file. It needs to be updated on the Argus computer to then go through and
  delete the .csv files

Michael Itzkin; January 24, 2024
"""

import datetime as dt
import netCDF4 as nc
import pandas as pd
import numpy as np
import schedule
import time
import os


def main():
    """
    Run the code
    """

    """
    User input here
    """

    # Set the scan name and date
    location = 'Madeira_Beach'

    # Set the scan height and location.
    # NOTE: This should be measured in the field and/or collected from the GPS
    lidar_height = 0  # 1.524

    # Set the number of rows to process at a time (no real reason to change this)
    CHUNK_SIZE = 5000
    SKIP_FILES = 10

    # Set this to TRUE to just save the point cloud data
    just_point_cloud = False

    """
    Do not change anything below this line
    """

    # Get the list of .csv files that contain the scan
    project_folder = os.path.join(r'/home/argus_user/Documents/Lidar/Projects', location)
    surveys = [filename for filename in os.listdir(project_folder) if os.path.isdir(os.path.join(project_folder,filename))]
    for survey in surveys:
        scan_date = dt.datetime.strptime(survey, '%b_%d_%Y_%H_%M')
        scan_folder = os.path.join(project_folder, survey)
        scan_files = os.listdir(scan_folder)
        output_file = os.path.join(scan_folder, f'{location}_{survey}.nc')
    
        start_compile = dt.datetime.now()
        print(f'--- Working on {output_file} ---')
    
        # Compile the survey data into a single numpy array
        scan_data = []
        for csv_file_name in scan_files[::SKIP_FILES]:
            chunk_container = pd.read_csv(os.path.join(scan_folder, csv_file_name), chunksize=CHUNK_SIZE)
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
        ncfile.survey_date = f'{scan_date.strftime("%B %d, %Y")} at {scan_date.hour}:{scan_date.minute}'
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
                adjusted_time[:]
    
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
    
        print('Finished processing survey')


if __name__ == '__main__':
    while True:
        if dt.datetime.now().minute == 30:
            main()
        time.sleep(60)
