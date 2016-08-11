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
stations = {'Hastings':'ucha',
'Blue Oak Ranch':'ucbo',
'Angelo':'ucac',
'Bodega':'ucbm',
'Deep Canyon':'ucde',
'Burns':'ucbu',
'Chickering':'ucca',
'Elliott':'ucel',
'James':'ucja',
'Jepson':'ucjp',
'Rancho Marino':'ucrm',
'BigCreek Whale':'whpt',
'BigCreek Highlands':'hipk',
'BigCreek Gatehouse':'ucbc',
'McLaughlin':'ucmc',
'Motte':'ucmo',
'Santa Cruz Island':'ucsc',
'Sedgwick':'ucse',
'SNARL':'ucsh',
'Anza Borrego':'ucab',
'Stunt Ranch':'ucsr',
'Granites':'ucgr',
'WhiteMt Summit':'wmtn',
'WhiteMt Barcroft':'barc',
'WhiteMt Crooked':'croo',
'Younger':'ucyl',
'Sagehen Creek':'sagh'}

# Loop through all the stations
for station_name,station in stations.items():
    print(station_name,station)    
        
    # Define path and station filename
    #path = '/data/sensor/UCNRS/'
    path = '/Users/cbode/Documents/GoogleDrive/UCNRS_WeatherStations/DatFiles_DRI/'
    fstation = station+'_'+station_name.replace(' ','_').lower()+'_dri.dat'
    fpath = path+fstation
    temppath = fpath+'.temp'
    hpath = path+'dri_headers/'+fstation+'.header'
    
    if(os.path.exists(fpath) and os.path.exists(hpath)):
        # move existing file to temporary file
        os.rename(fpath,temppath) 
        
        # open files
        fin = open(temppath,'r')
        fout = open(fpath,'w')
        fhead = open(hpath,'r')
        
        #######
        # Get Header lines from header file
        hrow = []
        for row in fhead:
            hrow.append(row)
        hfields = hrow[1].split(',')
        fhead.close()        
        #fieldnames = ','.join(map(str, hfields))
        
        #######
        # Loop through header and dat file, out put to main dat file
        i = 0
        for row in fin:
            #print(i)
            fields = row.split(",")
            if(i == 0):
                fout.write(hrow[0])
            elif(i == 1):
                if(fields[0] == '"TIMESTAMP"'):
                    print(station_name,' row',i,'Fields')
                    for j in range(0,len(fields)):
                        if(not '_flag' in hfields[j]):
                            print(fields[j],'-->',hfields[j])
                    fout.write(hrow[1])
                else:
                    i = -9999
                    fin.close()
                    fout.close()
                    sys.exit("BAD ROW! Exiting. DAT")
            elif(i == 2):
                fout.write(hrow[2])
            elif(i == 3):
                fout.write(hrow[3])
            else:
                firstfield = fields[0].replace('"','')
                if(len(firstfield) > 0):
                    firstchar = firstfield[0]
                else:
                    firstchar = ''
                if(firstchar == '1' or firstchar == '2'):
                    fout.write(row)
                else:
                    print(station_name,i,'BAD ROW',firstchar,fields[0])
            i += 1
        print('DONE with ',station,i)
        fin.close()
        fout.close()
        print('Deleting temp file '+temppath)
        os.remove(temppath)
    else:
        print(fstation+' or its header are not found, skipping...')
print('Done!')