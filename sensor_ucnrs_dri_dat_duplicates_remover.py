#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# author: collin bode
# date: 8/6/2017
# purpose: Remove duplicates from .dat files.  Assumes ISO time

from __future__ import print_function
import os
import datetime as dt
import pandas as pd

def file_lastline(filepath):
    with open(filepath,'r') as f:
        filelines = f.readlines()
        lines = len(filelines)
        lastline = filelines[lines-1]
        return lastline

def file_lastdate(filepath,sep=',',ts_pos=0):
    with open(filepath,'r') as f:
        ts = 'ERROR'
        filelines = f.readlines()
        linenum = len(filelines)
        lastline = filelines[linenum-1]
        values = lastline.split(sep)
        str_time = values[ts_pos].strip().replace('"','')
        try:
            ts = dt.datetime.strptime(str_time,"%Y-%m-%d %H:%M:%S")
        except:
            print("ERROR: "+file+" Doesn't have timestamp at postition "+str(ts_pos)+": "+str_time)                         
        return ts

def file_firstdate(filepath,sep=',',ts_pos=0):
    # Returns both the first timestamp in file and how many header rows there were
    # Assumes ISO date structure.  Will not work otherwise 
    ts = 'ERROR'
    with open(filepath,'r') as f:
        i = 0
        filelines = f.readlines()
        for line in filelines:
            values = line.split(sep)
            str_time = values[ts_pos].replace('"','')
            try:
                ts = dt.datetime.strptime(str_time,"%Y-%m-%d %H:%M:%S")
                print(i,'Found Timestamp!',ts)
                break
            except:
                continue
                #print(i," Line doesn't have timestamp at postition "+str(ts_pos)+": "+str_time)                         
            i += 1
            if(i > 100):
                print(i,' Never found any timestamps. Quitting.')
                break
    return ts,i  

path = '/Users/collin/Desktop/SensorDB_Duplicates/'
inpath = path+'source/'
outpath = path+'new/'

print('UCNRS Stations Last Seen:')
with open('file_stats.csv','w') as fout:
    fout.write('file,date_start,date_end,rows_ideal,rows_actual,diff_iva,rows_fixed,diff_ivf\n')
    j = 0
    for file in os.listdir(path):
        #print('test',file)
        if(len(file.split('.')) == 0):
            pass
        elif(file.split('.')[-1] == 'dat'):
            fpath = inpath+file
            opath = outpath+file
            
            # Find Start and end dates
            date_end = ''
            date_start = ''
            
            # Get Header and create replacement file
            with open(opath,'w') as fout:
                with open(fpath,'r') as f:
                    i = 0
                    ts =''
                    all_lines = f.readlines()
                    actual_row_count = len(all_lines)
                    for line in all_lines:
                        values = line.split(',')
                        str_time = values[ts_pos].replace('"','')
                        try:
                            ts = dt.datetime.strptime(str_time,"%Y-%m-%d %H:%M:%S")
                            print(i,'Found Timestamp!',ts)
                            break
                        except:
                            continue
                        i += 1
                        if(i == actual_row_count):
                            
                    
            '''
            # Count Rows
            date_interval = date_end - date_start
            logger_interval = dt.timedelta(minutes=10)
            ideal_row_count = (date_interval / logger_interval) + header_count
            actual_row_count = 0
            with open(fpath) as f:
                actual_row_count = len(f.readlines())
            rows_diff = ideal_row_count - actual_row_count

            # Get Header and create replacement file
            with open(outpath,'w') as fout:
                with open(fpath,'r') as f:
                    k = 0
                    for line in f.readlines():
                        
            
            
            # Remove Duplicatesusing Pandas
            #df = pd.DataFrame(fpath,skiprows=1,)
            '''

            station = file.split('_')[1].strip()
            print(station+"\t\t Start:",date_start," End:",date_end," Iddeal Row Count:",ideal_row_count," Actual Row Count:",actual_row_count," Difference:",rows_diff)
            outrow = [file,dt.datetime.strftime(date_start,"%Y-%m-%d %H:%M:%S"),dt.datetime.strftime(date_end,"%Y-%m-%d %H:%M:%S"),str(ideal_row_count),str(actual_row_count),str(rows_diff)]
            str_outrow = ','.join(outrow)
            fout.write(str_outrow+'\n')
            j += 1
            If(j > 1):
                break

print('----------------------------')