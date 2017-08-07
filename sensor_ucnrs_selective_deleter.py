# -*- coding: utf-8 -*-
##############################################################
# sensor_ucnrs_selective_deleter.py
# Author: Collin Bode
# Date: 2017-06-14
#
# Purpose:  to delete datavalues from the misbehaving stations
# from UCNRS DRI downloads.  There are 9 stations that need revision.
##############################################################

import mysql.connector
import datetime as dt

def odm_connect(pwfilepath,boo_dev=False):
    # NOTE: password file (pwfile) should NEVER be uploaded to github!
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

station_list = [
    ['James',343]]
    
'''
 ['Elliott',341],
 ['WhiteMt Crooked',362],
 ['Sagehen Creek',364],
 ['James',343],
 ['Jepson',344],
 ['Rancho Marino',345],
 ['Sedgwick',355],
 ['WhiteMt Summit',360],
 ['Younger',363]
]
'''
pwfilepath = 'C:/Users/me/Documents/GitHub/odm.pw'
conn = odm_connect(pwfilepath)
ds_list = []
for station,stationid in station_list:
    print(station,stationid)
    cursor = conn.cursor()
    sql = 'select DatastreamID, DatastreamName from datastreams where stationid = '+str(stationid)
    cursor.execute(sql)
    for datastreamid,datastream in cursor.fetchall():
        #print(station,datastreamid,datastream)
        ds_list.append([station,datastreamid,datastream])    
    cursor.close()

for station,datastreamid,datastream in ds_list:
    # Count Records Before
    cursor = conn.cursor()
    sql = 'SELECT count(*) FROM odm.datavalues_UCNRS WHERE DatastreamID = '+str(datastreamid)
    cursor.execute(sql)
    result = cursor.fetchall()
    ds_count = result[0][0]
    
    # Count Dev records before
    sql_dev = 'SELECT count(*) FROM odm_dev.datavalues_UCNRS WHERE DatastreamID = '+str(datastreamid)
    cursor.execute(sql_dev)
    result_dev = cursor.fetchall()
    dsdev_count = result_dev[0][0]
    print(station,ds_count,dsdev_count,datastream)
    '''
    # Backup Records to odm_dev
    sql = 'REPLACE INTO odm_dev.datavalues_UCNRS SELECT * FROM datavalues_UCNRS WHERE datastreamid = '+str(datastreamid)
    cursor.execute(sql)
    
    # Count Dev records after
    sql_dev = 'SELECT count(*) FROM odm_dev.datavalues_UCNRS WHERE DatastreamID = '+str(datastreamid)
    cursor.execute(sql_dev)
    result_dev = cursor.fetchall()
    dsdev_count = result_dev[0][0]
    print(station,ds_count,dsdev_count,datastream)
    '''
    # Backup Records to odm_dev
    #sql = 'DELETE FROM odm.datavalues_UCNRS WHERE datastreamid = '+str(datastreamid)
    sql = 'DELETE FROM odm.datavalues_UCNRS WHERE datastreamid = '+str(datastreamid)+' AND LocalDateTime > "2011-02-28 22:50:00"';
    cursor.execute(sql)    
    
    # Count Records After 
    cursor = conn.cursor()
    sql = 'SELECT count(*) FROM odm.datavalues_UCNRS WHERE DatastreamID = '+str(datastreamid)
    cursor.execute(sql)
    result = cursor.fetchall()
    ds_count = result[0][0]
    print(station,ds_count,dsdev_count,datastream)    
    cursor.close()
    
conn.close()
