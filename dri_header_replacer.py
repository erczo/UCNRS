# -*- coding: utf-8 -*-
#!/home/collin/pyv/bin/python
################################################################################
# name: header_replacer.py
# author: collin bode, email: collin@berkeley.edu
# date: 2016-08-07
# 
# purpose: Replace the header on a .dat file for all files that meet filter.
#
################################################################################

import os
import sys

# WRCC has codes for each UC weather station
stations = ['ucac','ucbo','ucab','ucja',
'ucbm','ucde','ucbu','ucca','ucel','ucha',
'ucjp','ucmc','ucmo','ucrm','ucsc','ucse',
'ucsh','ucsr','ucgr','ucyl','hipk','whpt',
'sagh','croo','wmtn','barc']
 
# Loop through all the stations, webscrape, and parse
for station in stations:
    print(station)    
    
    # Define path and station filename
    #path = '/data/sensor/UCNRS/'
    path = '/Users/cbode/Documents/GoogleDrive/UCNRS_WeatherStations/DatFiles_DRI/'
    fpath = path+station+'_dri.dat'
    temppath = fpath+'.temp'
    hpath = path+'dri_headers/'+station+'_dri.header'
    
    # move existing file to temporary file
    os.rename(fpath,temppath)
    
    # open files
    fin = open(temppath,'r')
    fout = open(fpath,'w')
    fhead = open(hpath,'r')
    
    # Get fieldname line from header file
    fields = fhead.readlines()[1].split(',')
    fieldnames = ','.join(map(str, fields))
    fhead.close()
    #print(fieldnames)
    print('next is dat file')
    
    # Loop through header and dat file, out put to main dat file
    i = 0
    for row in fin:
        i += 1
        #print(i)
        if(i == 2):
            fields = row.split(",")
            if(fields[0] == '"TIMESTAMP"'):
                print(station,i," OLD ROW: ",row)
                print("      NEW ROW: ",fieldnames)
                fout.write(fieldnames)
            else:
                i = 9999
                fin.close()
                fout.close()
                sys.exit("BAD ROW! Exiting. DAT")
        else:
            fout.write(row)
                
    print('DONE with ',station,i)
    fin.close()
    fout.close()
