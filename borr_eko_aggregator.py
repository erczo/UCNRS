# -*- coding: utf-8 -*-
"""
BORR eKo investigator / aggregator 
Author: Collin Bode, email: collin@berkeley.edu
Date: May 17, 2016

Background: eKo motes at the UCNRS Blue Oak Ranch Reserve.
The eKo basestation at the reserve provides xml packets on a port.  A perl script
written by Mark Holler pulls those packets, parses them and exports to csv text files.
This is done on the wanda.berkeley.edu server.  Problem is the packets come in at 
15 second intervals.  We need 5-30 minute aggregation.  This was done by RRDB
in the old script.

Purpose: to take 15 second eKo mote data and aggregate to a larger time interval.

"""
import os
import pandas as pd
import glob
import sys

purpose = 'count' # '15min', 'boardid'

# Board identification by fields
boardtypes = (
      ['eN2100','node internal parameters',['internalTemp','batteryV','solarV','packetNumber','vRef' ]],  
      ['en2120','node internal parameters',['internalTemp','batteryV','solarV','externalV','packetNumber','vRef' ]], 
      ['eS1101','Soil Moisture/Temp sensor', ['soilMoisture','soilTemperature']], 
      ['eS1201','Ambient Temperature/Humidity Sensor', ['temperature','humidity','dewPoint']],  
      ['ET22','Weather Station Data', ['Temp','TempInt','Humidity','DewPoint','Solar','UVCnt','BP','Rain','RainRate','RainTotal','WindLast','WindMax','WindAvg','WindDir','WindDirAvg']],  
      ['eS1100','soil moisture only sensor', ['soilMoisture']],  
      ['eT159','BOR special sensor set',  ['Temperature','VWC','LeafWetCnts','ref_cnts','LeafWetExc','CS625Exc','CS625PlsWdth','ExtV' ]],   
      [ 'ET173','pressure/temp sensor', ['pr','depth','temp','exc','fsp','r_temp','r_pressure','ref_cnt','exc_cnt','temp_cnt','pressure_cnt' ]]
      )

for board in boardtypes:
    print board[0],board[1]
sys.exit(0)

# Loop through all files int eKo export edirectory
for ekopath in glob.glob('/Users/cbode/eKo/*.csv'):
    df = pd.read_csv(ekopath,index_col=[0],parse_dates=True)

    # Identify sensor board based on the fields
    
    # Count number of records per interval
    count = df.resample('15Min',how={df.columns[0]:'count'}).max()
    pathdir,ekofile = os.path.split(ekopath)
    print ekofile,"\t",count[0]
    
    # Export data in 15 minute intervals
    if(purpose == '15min'):
        df15m = df.resample('15Min',how='mean')
        path,suf = ekopath.split('.')
        eko15min = path+'_15min.csv'
        df15m.to_csv(eko15min,header=True)
        print eko15min," exported."
print 'Done!'