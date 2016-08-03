#!/usr/bin/python3
################################################################################
# name: sensor_ucnrs_dri_puller.py
# author: collin bode, email: collin@berkeley.edu
# date: 2016-05-09
# Python Version 3.x required
#
# Purpose:  Performs a web-scrape of the WRCC website pulling data for 
# each UCNRS weather station managed by WRCC.  Export files are made to replicate 
# Campbell Scientific LoggerNet .dat files. 
#
# UCNRS - University of California Natural Reserve System
# WRCC - Western Regional Climate Center, Desert Research Institute, Reno, NV
# Contacts:  David Simaril, David.Simeral@dri.edu 
#            Greg McCurdy, greg.mccurdy@dri.edu
# website:  wrcc.dri.edu
# curl -F 'stn=UCAC'  -F 'smon=04' -F 'sday=10'  -F 'syea=16'  -F 'emon=05'  -F 'eday=09'  -F 'eyea=16'  -F 'secret=Password'  -F 'dfor=02'  -F 'srce=W'  -F 'miss=08' -F 'flag=Y'  -F 'Dfmt=06'  -F 'Tfmt=01'  -F 'Head=01'  -F 'Deli=01'  -F 'unit=M'  -F 'WsMon=01'  -F 'WsDay=01'  -F 'WeMon=12' -F 'WeDay=31'  -F 'WsHou=00'  -F 'WeHou=24' -F 'Submit Info=Submit Info'  -F '.cgifields=unit' -F '.cgifields=flag'  -F '.cgifields=srce'  http://www.wrcc.dri.edu/cgi-bin/wea_list2.pl > ucac.dat
#
# POST Variables to get proper download
# 'stn'  station code 
# 'smon' start month
# 'sday' start day 10
# 'syea' start year 16
# 'emon' end month 05
# 'eday' end day 09
# 'eyea' end year 16
# 'secret' password to access older data
# 'dfor' format: 01 = RAWS, 02 = delimited .dat, 03 = columnar, 04 = excel, 05 = delimited txt
# 'srce' original data or Fire Program Analysis (FPA)
# 'miss' missing data format  01 = "M", 02 = "m", 03 = blank space, 08 = -9999
# 'flag' Include data flags?  Y = yes, N = no
# 'Dfmt' Date Format default 01 = YYMMDDhhmm, 06 = YYYY-MM-DD hh:mm
# 'Tfmt' Time format 01 = LST 0-23 default, 02 = LST 1-24, 03 = LST am/pm
# 'Head' Header 01 = column header short desc, 02 = list head long desc, 03 = no header
# 'Deli' Field Delimiter default 01 - comma, 02 - colon, 03 - pipe, 04 - space, 05 - tab  
# 'unit' M - metric, E - English
#  Sub interval windows: feature that was never finished? Leaving all as default. Seems
#  to fail if you remove them:  WsMon, WsDay, WeMon, WeDay, WsHou, WeHou
#  .cgifields - not sure what these are so I am leaving them in place
################################################################################

import requests
import datetime as dt

# First Run? Pull ALL data and make headers or just download yesterday (cron job)
booFirstRun = False
booDownloadData = False

# WRCC DRI Website
website = 'http://www.wrcc.dri.edu/cgi-bin/wea_list2.pl'

# WRCC has codes for each UC weather station
stations = ['ucac','ucab','hipk','whpt','ucbo',
'ucbm','ucde','ucbu','ucca','ucel','ucha','ucja',
'ucjp','ucmc','ucmo','ucrm','sagh','ucsc','ucse',
'ucsh','ucsr','ucgr','croo','wmtn','barc','ucyl']

# First Run Values
if(booFirstRun == True):
    #time_start = dt.datetime.strptime('2000-01-01 01:00:00',"%Y-%m-%d %H:%M:%S")
    head = '02'   # long header
    write_mode = 'w' # new file
else:
    head = '03'  # no header
    write_mode = 'a' # append to existing file
    

for station in stations:
    #print("Downloading "+station)
    
    # Define path and station filename
    #path = '/data/sensor/UCNRS/DRI/'
    #path = '/Users/cbode/Desktop/DRI/'    
    path = "L:\\Google Drive\\UCNRS_WeatherStations\\DatFiles_DRI\\"
    fpath = path+station+'_dri.dat'
    #fpath = path+'headers_dri.csv'

    # Days to pull data
    time_end = dt.datetime.now()
    # time_interval_days = dt.timedelta(days=1)
    # time_start = time_end - time_interval_days    
    if(booFirstRun == False):
        # pull the last row in file
        f = open(fpath,'r')
        k = 0
        for row in f:
            #print(row)
            k += 1
        fields = row.split(',')
        dtstring = fields[0]
        if dtstring.startswith('"') and dtstring.endswith('"'):
           dtstring = dtstring[1:-1]
        if dtstring.startswith("'") and dtstring.endswith("'"):
            dtstring = dtstring[1:-1]
        print(station+' last date: '+dtstring)
        time_start = dt.datetime.strptime(dtstring,"%Y-%m-%d %H:%M:%S") 
        f.close()
    break
    
    # Define all POST variables required to make WRCC's website form to work
    post_data = {'stn':station,
    'smon':str(time_start.month).zfill(2),   
    'sday':str(time_start.day).zfill(2),
    'syea':str(time_start.year)[2:4],  
    'emon':str(time_end.month).zfill(2),
    'eday':str(time_end.day).zfill(2),  
    'eyea':str(time_end.year)[2:4],     
    'secret':'',                        
    'dfor':'02',                        
    'srce':'W',                         
    'miss':'08',                        
    'flag':'Y',                         
    'Dfmt':'06',                        
    'Tfmt':'01',                        
    'Head':'02',                        
    'Deli':'01',                         
    'unit':'M',
    'WsMon':'01',
    'WsDay':'01',
    'WeMon':'12',
    'WeDay':'31',
    'WsHou':'00',
    'WeHou':'24',
    'Submit Info':'Submit Info',
    '.cgifields':'unit',
    '.cgifields':'flag',
    '.cgifields':'srce'} 
    print(post_data)
    
    # POST request that is the heart of this script
    r = requests.post(website,post_data)

    # R now has the downloaded data. 
    received_data = (r.text).split("\n")

    # Open file for writing        
    fout = open(fpath,write_mode)    
    
    ############################################################################
    # HEADER: Build a new header. Ginger wants as similar to .dat as possible.    
    if(booFirstRun == True):
        '''    
        # Loggernet Header for ucac
        Row1: Station Id "TOA5","ucac_angelo","CR1000","44472","CR1000.Std.22","CPU:UC_Angelo.CR1","22000","TenMin"
        Row2: Fields     "TIMESTAMP","RECORD","Day_of_Year","Hour","RS_kw_m2_Avg","RS_kw_m2_Max","RS_kw_m2_Min","RS_kw_m2_Std","PAR_Avg","PAR_Max","PAR_Min","WS_mph_WVc(1)","WS_mph_WVc(2)","WS_mph_WVc(3)","WS_mph_WVc(4)","WS_mph_Max","WS_mph_Std","WS_mph_Min","AT_C_Max","AT_C_Min","AT_C_Avg","RH_pct_Max","RH_pct_Min","RH_pct_Avg","BP_mb_Avg","PCPN_in_Tot","PCPN_tot","RGTemp_C_Avg","TC_C_2_Max","TC_C_2_Min","TC_C_2_Avg","TC_C_10_Max","TC_C_10_Min","TC_C_10_Avg","delta_T_C_Max","delta_T_C_Min","delta_T_C_Avg","Soil_T2_C_Max","Soil_T2_C_Min","Soil_T2_C_Avg","Soil_T4_C_Max","Soil_T4_C_Min","Soil_T4_C_Avg","Soil_T8_C_Max","Soil_T8_C_Min","Soil_T8_C_Avg","Soil_T20_C_Max","Soil_T20_C_Min","Soil_T20_C_Avg","VWC4_Avg","VWC_V_Avg","CS616_4_Avg","CS616_V_Avg","batt_volt_Max","batt_volt_Min","batt_volt_Avg","PTemp_Avg","ForwardTxX10","ReflectTxX10","Sta_Id"
        Row3: Empty      "TS","RN","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""
        Row4: Aggregate  "","","Smp","Smp","Avg","Max","Min","Std","Avg","Max","Min","WVc","WVc","WVc","WVc","Max","Std","Min","Max","Min","Avg","Max","Min","Avg","Avg","Tot","Smp","Avg","Max","Min","Avg","Max","Min","Avg","Max","Min","Avg","Max","Min","Avg","Max","Min","Avg","Max","Min","Avg","Max","Min","Avg","Avg","Avg","Avg","Avg","Max","Min","Avg","Avg","Smp","Smp","Smp"
        Row5+: Data      "2013-05-14 15:10:00",52418,134,1510,0.715,0.734,0.693,0.011,0.85,0.872,0.832,3.846,3.228,49.57,31.74,8.77,2.093,0,25.11,24.57,24.85,26.55,23.08,23.78,965.8099,0,0,28.37,26.04,23.89,24.78,25.06,23.56,24.31,0.234,-1.35,-0.467,30.4,29.97,30.19,23.14,22.8,22.99,20.25,19.88,20.05,17.71,17.46,17.58,0.145,0.112,22.46,21.08,13.06,13.05,13.05,28.28,0,0,412
    
        # Webscrape Short Header for ucac
        Anza Borrego Desert Research Center  California 
        :          	  LST  	 W/m2	    	 W/m2	    	 W/m2	    	 W/m2	    	um/m2	    	um/m2	    	um/m2	    	 m/s 	    	 m/s 	    	 Deg 	    	 Deg 	    	 m/s 	    	 Deg 	    	 m/s 	    	Deg C	    	Deg C	    	Deg C	    	  %  	    	  %  	    	  %  	    	mbar 	    	 mm  	    	 mm  	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	Deg C	    	 VWC 	    	  %  	    	 Unk 	    	freq 	    	volts	    	volts	    	volts	    	Deg C	    	     	    
        :   Date   	 Time  	 Solar 	    	  Max  	    	  Min  	    	Std dev	    	Ave PAR	    	Max PAR	    	Min PAR	    	  Wind 	    	 Wind  	    	 Wind  	    	Std Dev	    	Mx Gust	    	Std Dev	    	  Min  	    	 Mx Air	    	 Mn Air	    	 Av Air	    	Mx Rel 	    	Mn Rel 	    	  Rel  	    	 Barom 	    	 Precip	    	 Accum 	    	Rn Gaug	    	  2m   	    	  2m   	    	  2m   	    	Max T  	    	Min T  	    	Min T  	    	10m-2m 	    	10m-2m 	    	10m-2m 	    	2" Soil	    	2" Soil	    	2" Soil	    	4" Soil	    	4" Soil	    	4" Soil	    	8" Soil	    	8" Soil	    	8" Soil	    	20"Soil	    	20"Soil	    	20"Soil	    	Soil M 	    	Vol Wtr	    	 Misc  	    	  TDR  	    	Max Bat	    	Min Bat	    	Battery	    	Dat Pan	    	Station	    
        :YYYY/MM/DD	 hh:mm 	  Rad. 	 flg	Solar R	 flg	Solar R	 flg	Sol.Rad	 flg	Flux Dn	 flg	Flux Dn	 flg	Flux Dn	 flg	  Speed	 flg	Vec Mag	 flg	 Direc 	 flg	Wnd Dir	 flg	 Speed 	 flg	Wnd Spd	 flg	Wnd Spd	 flg	  Temp 	 flg	  Temp 	 flg	  Temp 	 flg	Humidty	 flg	Humidty	 flg	Humidty	 flg	 Press 	 flg	       	 flg	 Pcpn  	 flg	  Temp 	 flg	Mx Temp	 flg	Mn Temp	 flg	Av Temp	 flg	TC 10m 	 flg	TC 10m 	 flg	TC 10m 	 flg	 Mx dT 	 flg	 Mn dT 	 flg	Delta T	 flg	Max Tmp	 flg	Min Tmp	 flg	Ave Tmp	 flg	Max Tmp	 flg	Min Tmp	 flg	Ave Tmp	 flg	Mx Temp	 flg	Mn Temp	 flg	Av Temp	 flg	Mx Temp	 flg	Mn Temp	 flg	Av Temp	 flg	@ 2 in.	 flg	 Cont 1	 flg	  #1   	 flg	 #1    	 flg	 Volts 	 flg	 Volts 	 flg	Voltage	 flg	  Temp 	 flg	 Id. # 	 flg
        2016/05/09	00:00	0	0	0	0	0	0	0	0	1	0	1	0	0	0	0.7841	0	0.726	0	299.1	0	22.08	0	1.241	0	0.358	0	0.5552	0	16.53	0	15.43	0	15.93	0	52.28	0	50.2	0	50.9	0	980.4	0	0	0	287.8	0	13.11	0	16.45	0	15.06	0	15.68	0	18.36	0	17.64	0	17.9	0	2.782	0	1.542	0	2.216	0	23.22	0	22.86	0	23.05	0	27.4	0	27.05	0	27.24	0	28.19	0	27.91	0	28.06	0	26.15	0	25.87	0	26.01	0	0.031	0	0.032	0	17.14	0	17.17	0	12.67	0	12.61	0	12.66	0	14.86	0	418	0
        
        # Webscrape Long Header for ucac
            <!DOCTYPE html
       	PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
      	 "http://www.w3.org/TR/html4/loose.dtd">
        <PRE>
        :Day of Year
        (     )
        :Time of Day
        (     )
        :Solar Radiation 
        ( W/m2)
        ... cut fields ...
        (Deg C)
        :Station Identification Number
        (     )
        '''
        row1 = '"TOA5","'+station+'","DRI WRCC webscrape"\n'
        row2 = '"TIMESTAMP","RECORD"'
        row3 = '"TS","RN"'
        row4 = '"",""'
        j = 0
        for row in received_data:
            #print(row)
            j += 1
            if(len(row) > 0):
                fields = row.split("\r")
                firstchar = fields[0][0]
                #print(j,'. fields: ',fields,"\n")
                if(firstchar == ':'): 
                    fieldname = fields[0].strip()
                    fieldname = fieldname[1:len(fieldname)]
                    fieldunits = fields[1].strip()
                    fieldunits = (fieldunits[1:len(fieldunits)-1]).strip()
                    #print(j,' fieldname:'+fieldname+', units: '+fieldunits+"\n")
                    if(fieldname == 'Day of Year' or fieldname == 'Time of Day'):
                        # ignore these fields
                        row2 = row2
                    else:                    
                        row2 += ',"'+fieldname+'","'+fieldname+' flag"'
                        row3 += ',"",""'
                        row4 += ',"'+fieldunits+'","text"'
                if(firstchar == '1' or  firstchar == '2'):
                    print('DATA FOUND BREAKING')
                    break
        # Print new header
        print("row1 = "+row1)
        print("row2 = "+row2)
        print("row3 = "+row3)
        print("row4 = "+row4)
        print("\n")
        
        # Write header
        fout.write(row1+"\n")
        fout.write(row2+"\n")
        fout.write(row3+"\n")
        fout.write(row4+"\n")

    ############################################################################
    # Parse Data 
    # restart use of received_data array (that seems automatic)
    # Make sure first character is from year (19xx or 20xx)
    # Merge date and time into TIMESTAMP 
    if(booDownloadData == True):
        print('____Data next____')
        for row in received_data:
            if(len(row) > 0):
                fields = row.split(",")
                firstchar = fields[0][0]
                #print(fields[0], 'first character: ',firstchar)
                if(firstchar == '1' or firstchar == '2'):
                    date = fields.pop(0).strip()
                    time = fields.pop(0).strip()
                    ts = dt.datetime.strptime(date+' '+time,"%Y/%m/%d %H:%M")
                    timestamp = dt.datetime.strftime(ts,"%Y-%m-%d %H:%M:%S")
                    #print(date,' ',time,' --> ',timestamp)
                    newrow = '"'+timestamp+'",99'
                    #print(newrow)
                    for field in fields:
                        newrow += ','+field.strip()
                    newrow += "\n"
                    print(newrow)
                    fout.write(newrow)
                else:
                    print('BAD HTML! ')
    # Finish up with station 
    fout.close()  
    print(station+" downloaded and writen to file at "+path+station+'.dat')  
print('All Done!')
