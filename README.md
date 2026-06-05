 Preprocessing tool for ABL simulations

 era5_dta/ : 

 configuration file (.json) to select the goegraphical area of interest and the time period
 ERA5 data extraction script (extract_era_for_abl.py) results in a sequence of grib files with the necessary quantities 

 ABL_vertical_grid/ :

 configuration file (.json) to select the number of vertical levels, themaximum height and the stretching parameters for the ABL vertical grid 
 Creation of a netcdf file containing all the necessary informations to define the ABL vertical grid in NEMO (define_abl_vgrid.py)

