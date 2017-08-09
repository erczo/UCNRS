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

#path = '/Users/collin/Desktop/SensorDB_Duplicates/'
path = 'D:/sensor/UCNRS_Dups/'
inpath = path+'source/'
outpath = path+'new/'

print('UCNRS Stations Last Seen:')
with open(path+'file_stats.csv','w') as freport:
    report_header = 'file,date_start,date_end,rows_ideal,rows_actual,diff_iva,rows_fixed,diff_ivf\n'
    freport.write(report_header)
    j = 0
    for file in os.listdir(inpath):
        #print('test',file)
        if(len(file.split('.')) == 0):
            pass
        elif(file.split('.')[-1] == 'dat'):
            fpath = inpath+file
            opath = outpath+file
            
            # Set date and row count variables
            date_end = dt.datetime(1800,1,1)
            date_start = ''
            actual_row_count = 0
            ideal_row_count = 0
            fixed_row_count = 0
            header_row = 0
            header_length = 0
            
            # Get Header and create replacement file
            with open(opath,'w') as fout:
                with open(fpath,'r') as f:
                    i = 0
                    ts =''
                    all_lines = f.readlines()
                    actual_row_count = len(all_lines)
                    for line in all_lines:
                        values = line.split(',')
                        str_time = values[0].replace('"','')
                        if(str_time == "TIMESTAMP"):
                            header_row = i
                            print(i,'HEADER FIELDS')
                        try:
                            ts = dt.datetime.strptime(str_time,"%Y-%m-%d %H:%M:%S")
                            if(header_length == 0):
                                print(i,'Found Timestamp!',ts)
                                header_length = i
                            # Record End Date
                            if(date_end < ts):
                                date_end = ts
                        except:
                            if(date_start == ''):
                                print(i,'HEADER:',line)
                                fout.write(line)
                                
                        # Record Start Date
                        if(date_start == ''):
                            date_start = ts
                        i += 1
                        
                # Count Rows
                date_interval = date_end - date_start
                logger_interval = dt.timedelta(minutes=10)
                ideal_row_count = (date_interval / logger_interval) + header_length
                diff_iva = ideal_row_count - actual_row_count
    
                # Remove Duplicates using Pandas
                # skip rows actually allows for removing before and after header rows
                # this snippet builds a list of rows to be removed
                skips = []
                for s in range(0,header_length):
                    if(s > header_row):
                        skips.append(s)
                # Create Pandas DataFrame from faulty file
                df = pd.read_csv(fpath,skiprows=skips,header=header_row,parse_dates=True,index_col=0)
                dfu = df.drop_duplicates(keep='first')
                dfu.to_csv(path+'dfu_temp.csv',header=False)
                
                # Feed cleaned non-duplicate dfu_temp.csv file into new output file
                with open(path+'dfu_temp.csv','r') as ffu:
                    ffu_lines = ffu.readlines()
                    fixed_row_count = len(ffu_lines)+header_length
                    for line in ffu_lines:
                        fout.write(line)
                # Delete temp file
                os.remove(path+'dfu_temp.csv')
                
                # count rows of fixed versus ideal
                diff_ivf = ideal_row_count - fixed_row_count
                
            outrow = [file,dt.datetime.strftime(date_start,"%Y-%m-%d %H:%M:%S"),dt.datetime.strftime(date_end,"%Y-%m-%d %H:%M:%S"),str(ideal_row_count),str(actual_row_count),str(diff_iva),str(fixed_row_count),str(diff_ivf)]
            str_outrow = ','.join(outrow)
            freport.write(str_outrow+'\n')
            print(report_header)
            print(str_outrow)
            j += 1

print('----------------------------')
print('-----DONE!------------------')