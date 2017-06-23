#!/home/collin/pyv/bin/python
################################################################################
# name: sensor_ucnrs_dri_puller.py
# author: collin bode, email: collin@berkeley.edu
# date: 2016-05-09
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
# 'secret' password to access older data. This may change 'wrcc14'
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
#
# .time files have the last date downloaded for that .dat file. 
#   booFirstRun = True will set date in file to 1995
#   booFirstRun = False, but no file exists, it will set date to 29 days prior
#
# .dat files are constructed from webscrape to look like LoggerNet .dat files.
# booDatDelete will be set to true
#   if booFirstRun = True, but receives no header
#   if booDownloadData = True, but no data is downloaded and file only has header  
################################################################################

import requests
import mysql.connector
import datetime as dt
import logging
import os

# Boolean controls for script. Cron job mode is false, false, true.
booFirstRun = False     # True = Download all data available from 1990 until now
                        #        DRI controlled sites only can download 30 days, 
                        #        unless you have 'secret' password.
                        # False(default) = just download the last 24 hours 
                        # booWriteHeader will automatically be set to True.
booWriteHeader = False  # True = Get Long Header parse into LoggerNet header.
                        # False(default) = No header, just data. 
booDownloadData = True  # True(default). False will only download headers.

# Logging Level
log_level = logging.INFO  # DEBUG (too low level to be useful), INFO (troubleshoot), WARN (default), ERROR, CRITICAL 
log = logging.getLogger(__name__)   
station_name = ''

# Define path and station filename
path = '/data/sensor/UCNRS/'
pwfilepath = '/data/local/bin/sensor/odm.pw'

# Helper Function to create a single Logger message string from multiple inputs. Adds Station.
def m(*message):
    mess = [station_name,'-']
    for me in message:
        mess.append(str(me))
    m = ' '.join(mess)
    return m

# Helper function to create a unique filename and avoid clobbering existing files
def unique_file(f):
    i = 0
    f1 = f
    while(os.path.exists(f1) == True):
        i += 1
        ff = f.split('.')
        suf = ff[len(ff)-1]
        fff = f.split(suf)
        pref = fff[0]
        f1 = pref+'bak'+str(i)+'.'+suf
        log.info('File exists, '+f+' trying new file: '+f1)
    return f1

# Function to create ODM Database connection
def odm_connect(pwfilepath,boo_dev=False):
    # NOTE: password file should NEVER be uploaded to github!
    fpw = open(pwfilepath,'r')
    user = fpw.readline().strip()
    pw = fpw.readline().strip()
    fpw.close()
    if(boo_dev == True):
        db = 'odm_dev'
    else:
        db = 'odm'
    cnx = mysql.connector.connect(
        user=user,
        password=pw,
        host='gall.berkeley.edu',
        database=db)
    return cnx

# Function to get list of UCNRS stations, DRI prefix, and start date
def odm_station_list(pwfilepath):
    sql = 'SELECT st.StationName,st.FileName,min(startdate) as startdate '+\
          'FROM datastreams as ds, stations as st '+\
          'WHERE ds.StationName = st.StationName AND st.mc_name = "UCNRS" '+\
          'GROUP BY st.stationname,st.filename'
    conn = odm_connect(pwfilepath)
    cursor = conn.cursor()
    cursor.execute(sql)
    st_list = []
    for stationname,datfile,date_start in cursor.fetchall():
        ss = datfile.split('_')
        station = ss[0]
        log.debug(m('odm_station_list:',stationname,station,str(date_start)))
        st_list.append([stationname,station,datfile,date_start])    
    cursor.close()
    conn.close()
    return st_list

def pull_dri(station,time_start,time_end):                
    # WRCC DRI Website
    website = 'http://www.wrcc.dri.edu/cgi-bin/wea_list2.pl'

    # Define all POST variables required to make WRCC's website form to work
    post_data = {'stn':station.upper(),
    'smon':str(time_start.month).zfill(2),   
    'sday':str(time_start.day).zfill(2),
    'syea':str(time_start.year)[2:4],  
    'emon':str(time_end.month).zfill(2),
    'eday':str(time_end.day).zfill(2),  
    'eyea':str(time_end.year)[2:4],     
    'secret':'wrcc14',                        
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
    'Submit Info':'Submit Info'}
    log.debug(m(post_data))
    
    # POST request that is the heart of this script
    r = requests.post(website,post_data)
    log.debug(m('pull_dri:header:',r.headers))
    log.debug(m('pull_dri:status_code:',r.status_code))

    # R now has the downloaded data. 
    rd = (r.text).split("\n")
    return rd
    
def create_header(station,station_name,time_start):
    # pull one day's data with header
    time_end = time_start + dt.timedelta(days=1)
    rd_head = pull_dri(station,time_start,time_end)
    
    # Generate the fixed parts of the header
    # "TOA5","ucja_james","CR1000","3437","CR1000.Std.30.01","CPU:UC_James_Reserve_Meadow_ver_D.CR1","45609","TenMin"
    # <file format>,<logger type>,<?loggercode?>,<OS version>,<Running code>,<last record>,<table name> 
    row1 = '"TOA5","'+station_name+'","CR1000,"9999","CR1000.Std.30.01","CPU:DRI_WRCC_webscrape.cr1","49999","'+station+'"'
    row2 = '"TIMESTAMP","RECORD"'
    row3 = '"TS","RN"'
    row4 = '"",""'
    j = 0
    t = 0   # how many duplicates of Min TC 10m are there?
    log.info('Header being created...')
    for row in rd_head:
        log.debug(m(row))
        j += 1
        if(len(row) > 0):
            fields = row.split("\r")
            firstchar = fields[0][0]
            if(firstchar == ':'): 
                fieldname = fields[0]

                # DRI long headers are sentence descriptions
                # This segment shortens them to field names with no unusual characters
                fieldname = fieldname.replace('"','')                                      
                fieldname = fieldname.replace(':','')                    
                fieldname = fieldname.strip()
                fieldname = fieldname.replace(' ','_')
                fieldname = fieldname.replace('_in.','_Inches')
                fieldname = fieldname.replace('.','')
                fieldname = fieldname.replace('(','')
                fieldname = fieldname.replace(')','')
                fieldname = fieldname.replace('_#','')
                fieldname = fieldname.replace('#','')
                fieldname = fieldname.replace('_-_','_')
                fieldname = fieldname.replace("'","")
                fieldname = fieldname.replace('`','')
                fieldname = fieldname.replace('__','_')
                fieldname = fieldname.replace('Maximum','Max')
                fieldname = fieldname.replace('Minimum','Min')
                fieldname = fieldname.replace('Temperature','Temp')
                fieldname = fieldname.replace('temperature','Temp')
                fieldname = fieldname.replace('Ave_','Avg_')
                fieldname = fieldname.replace('Average','Avg')
                fieldname = fieldname.replace('Miscellaneous','Misc')
                fieldname = fieldname.replace('Identification','ID')
                fieldname = fieldname.replace('Standard_Deviation','Std_Dev')
                fieldname = fieldname.replace('Standard_Deveation','Std_Dev')
                fieldname = fieldname.replace('_mag/arcsec2','_mag')
                fieldname = fieldname.replace('/','')
                fieldname = fieldname.replace('\\','')
                
                # Fix Thermocouple duplicate 
                if('Min_Temp_Thermocouple_10' in fieldname):
                    t += 1
                    if(t == 2):
                        fieldname = fieldname.replace('Min','Avg')

                # Field units are inserted for posterity, but not used by loader
                fieldunits = fields[1].strip()
                fieldunits = (fieldunits[1:len(fieldunits)-1]).strip()
                log.debug(m(j,' fieldname:'+fieldname+', units: '+fieldunits+"\n"))
                if(fieldname == 'Day_of_Year' or fieldname == 'Time_of_Day'):
                    # ignore these fields
                    row2 = row2
                else:                    
                    row2 += ',"'+fieldname+'","'+fieldname+'_flag"'
                    row3 += ',"",""'
                    row4 += ',"'+fieldunits+'","text"'
            # Stop when you reach data
            if(firstchar == '1' or  firstchar == '2'):
                log.info(m('create_header',station,'DATA FOUND BREAKING',fields[0][0:10]))
                break
       
    # New header
    log.debug(m("row1 = "+row1))
    log.debug(m("row2 = "+row2))
    log.debug(m("row3 = "+row3))
    log.debug(m("row4 = "+row4))
    log.debug("\n")
    
    header = [row1,row2,row3,row4]    
    return header

def get_correct_header(station,station_name,t_start):
    # Go slightly back in time, then check headers for a few days. Take the most recent
    test_date = t_start - dt.timedelta(days=1)
    head0 = create_header(station,station_name,test_date)
    for i in range(1,12):
        test_date += dt.timedelta(days=1)
        head = create_header(station,station_name,test_date)
        if(head0 == head):
            log.debug(m(str(test_date),'headers same'))
        else:
            log.info(m(str(test_date),'header changed! old length:',len(head0[1]),'new lenth:',len(head[1])))
            log.debug(m(str(time_start),head0[1]))
            log.debug(m(str(test_date),head[1]))
            break   
    return head


#############################################################   
#
# BEGIN MAIN
#
# Logging Setup
log.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # create a logging format
fhandler = logging.FileHandler(path+'sensor_ucnrs_dri_puller.log') # create a file handler
fhandler.setLevel(log_level)
fhandler.setFormatter(formatter)
log.addHandler(fhandler)            # add the file handler to the logger    
shandler = logging.StreamHandler()
shandler.setFormatter(formatter)
log.addHandler(shandler)            # add the console handler to the logger
log.disabled = False

log.info('START sensor_ucnrs_dri_puller.py')
log.info('\t log level:'+str(log.level)+' handler level:'+str(shandler.level))

# Check for existance of the helper files directories, if not create
timepath = path+'dri_time/'
headpath = path+'dri_headers/'
rawpath = path+'dri_raw/'
if(os.path.exists(timepath) == False):  
    os.makedirs(timepath)
if(os.path.exists(headpath) == False):
    os.makedirs(headpath)
if(os.path.exists(rawpath) == False):
    os.makedirs(rawpath)


#############################################################   
# Loop through all the stations, webscrape, and parse
#station_list = [['Jepson','ucjp','ucjp_jepson_dri.dat',dt.datetime(2017, 4, 30, 9, 50)]]
station_list = odm_station_list(pwfilepath)

for station_name,station,fstation,station_first_time in station_list:
    log.info(m(station_name,station,fstation,str(station_first_time)))   

    # Define filename paths
    #str_station = station+'_'+station_name.replace(' ','_').lower()+'_dri'
    str_station,datdump = fstation.split('.dat')
    fpath = path+fstation
    frawpath = rawpath+str_station+'_raw.txt'
    ftpath = timepath+str_station+'.time'         # The .time file holds the last timestmap recorded
    fheadpath = headpath+str_station+'.header' # The .header file just holds the header 
    write_mode = 'a' # append to existing file
        
    # Build a header if the file doesn't exist yet and FirstRun wasn't called.
    if(os.path.exists(fpath) == False):
        booFirstRun == True

    ###########
    # TIME  
    # booFirstRun set up file header and download all data
    if(booFirstRun == True):
        if(station =='hipk' or station == 'whpt'):
            time_start = dt.datetime.now() - dt.timedelta(days=29)  # For 30 day locked stations
        else:
            #time_start = dt.datetime.strptime('1990-01-01 01:00:00',"%Y-%m-%d %H:%M:%S") #  DEBUG  '2017-04-27 01:00:00'
            time_start = station_first_time                                
        time_start_o = time_start
        time_end = dt.datetime.now()
        #time_end = dt.datetime.strptime('2015-01-05 01:00:00',"%Y-%m-%d %H:%M:%S")  # DEBUG
        write_mode = 'w' # new file
        booWriteHeader = True
    # booWriteHeader & booDownloadData False: Use to only write headers to separate file
    elif(booWriteHeader == True and booDownloadData == False):
        time_start = dt.datetime.now() - dt.timedelta(days=29)  
        time_end = time_start + dt.timedelta(days=1)
        time_start_o = time_start
    # Normal operation - daily download
    else: #booFirstRun == False
        if(os.path.exists(ftpath) == True):
            try:
                ft = open(ftpath,'r')   # open .time file and get last datetime pulled
                dtstring = (ft.read()).strip()
                time_start_o = dt.datetime.strptime(dtstring,"%Y-%m-%d %H:%M:%S") 
                time_start = time_start_o - dt.timedelta(days=1) # add a day for safety
                time_end = dt.datetime.now()
                ft.close()
            except:
                log.error(m("Time File doesn't have valid dates. Skipping...",ftpath))
                continue
        else:
            log.error("No Time File found: "+ftpath+" Please perform a First Run. Skipping...")
            continue

    ###########
    # Webscrape DRI - pull headers and data
    received_data = pull_dri(station,time_start,time_end)

    # dump raw text from DRI    
    if(log_level == logging.INFO):
        frawout = open(frawpath,'a')
        for row in received_data:
            frawout.write(row+'\n')
        frawout.close()

    ###########
    # Open .dat file for writing        
    fout = open(fpath,write_mode)    
    
    ###########
    # HEADER: Build a new header. Ginger wanted as similar to .dat as possible.    
    if(booWriteHeader == True):       
        header = get_correct_header(station,station_name,time_start)        
        if(len(header[1]) > 22):   # make sure the header has something in it
            log.info(m(station_name,'writing header to header file and dat file'))
            fheadout = open(fheadpath,'w')       # header to header file
            for h in range(0,4):
                fheadout.write(header[h]+"\n")
                fout.write(header[h]+"\n")   # header to empty .dat                
            fheadout.close()
        else:
            log.error(station+' has no data for time-period. cannot download header.')
                       
    ############################################################################
    # Parse Data 
    # Make sure first character is from year (19xx or 20xx)
    # Merge date and time into TIMESTAMP 
    booFoundTime = False
    booMidHeader = False
    timestamp = 'GEORGE'
    ts_previous = time_start
    ts = time_start
    l = 0
    h = 0
    if(booDownloadData == True):
        log.info('____Data next____')
        for row in received_data:
            l += 1
            log.debug(m('rd:',row))
            if(len(row) > 0):
                fields = row.split(",")
                firstchar = fields[0][0]
                if(firstchar == '1' or firstchar == '2'):
                    booMidHeader = False
                    ts_previous = ts
                    date = fields.pop(0).strip()
                    time = fields.pop(0).strip()
                    ts = dt.datetime.strptime(date+' '+time,"%Y/%m/%d %H:%M")
                    timestamp = dt.datetime.strftime(ts,"%Y-%m-%d %H:%M:%S")
                    newrow = '"'+timestamp+'",99'
                    for field in fields:
                        newrow += ','+field.strip()
                    newrow += "\n"
                    if(ts == ts_previous and booFoundTime == True):
                        log.error(m('Redundant timestamp:',str(ts),'==',str(ts_previous),'Row:',row))
                        pass
                    else:
                        fout.write(newrow)
                    booFoundTime = True
                    log.debug(m(newrow))
                # DRI periodically changes headers and columns mid-download.  
                elif(booFoundTime == True and firstchar == ':' and booMidHeader == True): 
                    log.debug(m('MidHeader:',h,row))
                    h += 1
                elif(booFoundTime == True and firstchar == ':' and booMidHeader == False): 
                    log.error(m('ALERT! ALERT! HEADER SWITCH MIDSTREAM!',row))
                    booMidHeader = True
                    tslast = ts + (ts - ts_previous)   #  add the station's timestep past last timestamp
                    
                    # Must close and move existing .dat file
                    fout.close() 
                    fpathdated0 = path+str_station+'_'+dt.datetime.strftime(ts,"%Y-%m-%d")+'.dat'
                    fpathdated = unique_file(fpathdated0)                                                                    
                    os.rename(fpath,fpathdated)
                    log.warning(m('Midstream header: moved old .DAT file and created new one.',fpathdated,fpath))
                    
                    # Close and move existing header file
                    fheadpathdated0 = headpath+str_station+'_'+dt.datetime.strftime(ts,"%Y-%m-%d")+'.header' 
                    fheadpathdated = unique_file(fheadpathdated0) 
                    os.rename(fheadpath,fheadpathdated)
                    log.warning(m('Midstream header: moved old .HEADER file and created new one.',fheadpathdated,fheadpath))
                    
                    # Open blank file and start over
                    fout = open(fpath,write_mode)
                    fheadout = open(fheadpath,'w')       # header to header file
                    
                    # re-run header function 
                    header = get_correct_header(station,station_name,tslast)
                    for h in range(0,4):
                        fout.write(header[h]+"\n") 
                        fheadout.write(header[h]+"\n") 
                    fheadout.close()    
                else:
                    log.debug(m('BAD HTML! ',row))
                    pass
                    
        # Write last timestamp
        if(timestamp != 'GEORGE'):
            ft = open(ftpath,'w')
            ft.write(timestamp+"\n")
            ft.close()
            log.info("Downloaded and writen to file")
        else:
            log.error('WARNING! No values to download.')
    # Finish up with station 
    fout.close()  

# Close out script
log.info('All Done!')
fhandler.close()
shandler.close()
logging.shutdown()
log.disabled = True
del log


############################################################################
# HEADER TEXT FOR REFERENCE
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
