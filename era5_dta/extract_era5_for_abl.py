#!/bin/python
# --------------------------------------------------------
#            Auteur  (date de creation) :
#        J. Pianezze (   20.08.2022   )
# --------------------------------------------------------
# https://cds.climate.copernicus.eu/api-how-to
# conda install cdsapi

import json
import os
import cdsapi
import datetime
import numpy as np

c = cdsapi.Client()

config_file = "era5_dta.json"
with open(config_file, "r") as f:
    config = json.load(f)
# #########################################################
# ###           to be defined by user                   ###
# #########################################################
# - first_date      = first date to extract (has to be at 00 UTC)
# - last_date       = last  date to extract (has to be at 18 UTC)
# - period_in_hr    = period_in_hr between two forcing files
# - area_to_extract = 'North/West/South/East'
#
first_date          = datetime.datetime(config["start_year"],config["start_month"], config["start_day"],  config["start_hour"], 0, 0)
last_date           = datetime.datetime(config["end_year"],config["end_month"], config["end_day"],  config["end_hour"], 0, 0)
period_in_hr        = config['period_in_hr'] 
area_to_extract     = f'{config['lat_max']}/{config['lon_min']}/{config['lat_min']}/{config['lon_max']}' #'50.0/-8.0/47.0/-3.0'
#
# #########################################################

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute date and time variables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
date_an   = str(first_date.year)+'-'+str(first_date.month).zfill(2)+'-'+str(first_date.day).zfill(2)+'/to/'+\
            str( last_date.year)+'-'+str( last_date.month).zfill(2)+'-'+str( last_date.day).zfill(2)
time_an   = np.arange(0,24,period_in_hr)
time_an   = [format(x, '02d') for x in time_an]
file_an   = 'from_'+str(first_date.year)+'-'+str(first_date.month).zfill(2)+'-'+str(first_date.day).zfill(2)+'_at_00_UTC_to_'   +\
                    str( last_date.year)+'-'+str( last_date.month).zfill(2)+'-'+str( last_date.day).zfill(2)+'_at_18_UTC_every_'+\
                    str(   period_in_hr).zfill(2)+'hr'

first_date = first_date - datetime.timedelta(hours=24)
date_fc    = str(first_date.year)+'-'+str(first_date.month).zfill(2)+'-'+str(first_date.day).zfill(2)+'/to/'+\
             str( last_date.year)+'-'+str( last_date.month).zfill(2)+'-'+str( last_date.day).zfill(2)
step_fc    = np.arange(1,13,1)
step_fc    = [format(x, '02d') for x in step_fc]
last_date  = last_date  + datetime.timedelta(hours=24)
file_fc    = 'from_'+str(first_date.year)+'-'+str(first_date.month).zfill(2)+'-'+str(first_date.day).zfill(2)+'_at_07_UTC_to_'   +\
                     str( last_date.year)+'-'+str( last_date.month).zfill(2)+'-'+str( last_date.day).zfill(2)+'_at_06_UTC_every_'+\
                     str(              1).zfill(2)+'hr'
if config["single_grib_file"]:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract Model Level fields : u, v, t et q
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c.retrieve('reanalysis-era5-complete', {
          'date'     : date_an,
          'levelist' : '98/to/137',
          'levtype'  : 'ml',
          'param'    : 'u/v/t/q',
          'stream'   : 'oper',
          'time'     : time_an,
          'type'     : 'an',
          'area'     : area_to_extract,
          'grid'     : '0.28125/0.28125',
      }, 'model_levels_uvtq_'+file_an+'.grib')
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract Model Level fields : lnsp
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c.retrieve('reanalysis-era5-complete', {
          'date'     : date_an,
          'levelist' : '1',
          'levtype'  : 'ml',
          'param'    : 'lnsp',
          'stream'   : 'oper',
          'time'     : time_an,
          'type'     : 'an',
          'area'     : area_to_extract,
          'grid'     : '0.28125/0.28125',
      }, 'model_levels_lnsp_'+file_an+'.grib')
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract SurFaCe fields : z, lsm, msl
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c.retrieve('reanalysis-era5-complete', {
          'date'     : date_an,
          'levtype'  : 'sfc',
          'param'    : config["sfc_fields"],
          'stream'   : 'oper',
          'time'     : time_an,
          'type'     : 'an',
          'area'     : area_to_extract,
          'grid'     : '0.28125/0.28125',
      },  'surface_levels_'+file_an+'.grib')  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract SurFaCe fields : sw, lw and precip
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    c.retrieve('reanalysis-era5-complete', {
          'date'     : date_fc,
          'levtype'  : 'sfc',
          'param'    : '228/176/177/175/169',
          'step'     : step_fc,
          'stream'   : 'oper',
          'time'     : ['06','18'],
          'type'     : 'fc',
          'area'     : area_to_extract,
          'grid'     : '0.28125/0.28125',
      }, 'flux_'+file_fc+'.grib')

else: 
    def range_for_date(start_date, end_date, period_in_hr):                                                                   
        for n in range(int((end_date - start_date).total_seconds()/(3600.0*period_in_hr))+1):                                     
            yield start_date + datetime.timedelta(seconds=n*3600.0*period_in_hr) 

    for date in range_for_date(first_date, last_date, period_in_hr):        
        date_to_be_extracted   = str(date.year)+'-'+str(date.month).zfill(2)+'-'+str(date.day).zfill(2)
        time_to_be_extracted   = str(date.hour).zfill(2)
        name_of_extracted_file = str(date.year)+str(date.month).zfill(2)+str(date.day).zfill(2)+'.'+str(date.hour).zfill(2)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extract Model Level fields : u, v, t et q
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        c.retrieve('reanalysis-era5-complete', {
              'date'     : date_to_be_extracted,
              'levelist' : '98/to/137',
              'levtype'  : 'ml',
              'param'    : 'u/v/t/q',
              'stream'   : 'oper',
              'time'     : time_to_be_extracted,
              'type'     : 'an',
              'area'     : area_to_extract,
              'grid'     : '0.28125/0.28125',
          }, 'model_levels_uvtq_'+name_of_extracted_file+'.grib')       
        #
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extract Model Level fields : lnsp
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        c.retrieve('reanalysis-era5-complete', {
              'date'     : date_to_be_extracted,
              'levelist' : '1',
              'levtype'  : 'ml',
              'param'    : 'lnsp',
              'stream'   : 'oper',
              'time'     : time_to_be_extracted,
              'type'     : 'an',
              'area'     : area_to_extract,
              'grid'     : '0.28125/0.28125',
          }, 'model_levels_lnsp_'+name_of_extracted_file+'.grib')
        #
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extract SurFaCe fields : z, lsm, msl
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        c.retrieve('reanalysis-era5-complete', {
              'date'     : date_to_be_extracted,
              'levtype'  : 'sfc',
              'param'    : config["sfc_fields"],
              'stream'   : 'oper',
              'time'     : time_to_be_extracted,
              'type'     : 'an',
              'area'     : area_to_extract,
              'grid'     : '0.28125/0.28125',
          },  'surface_levels_'+name_of_extracted_file+'.grib')  
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
