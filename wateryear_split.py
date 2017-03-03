#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
#  wateryear_splitter.py
#  Author: Collin Bode
#  Date: March, 2016
#  
#  Purpose: Take all Campbell Scientific CR1000 .dat files and split them by 
#  water year (Oct.1 to Oct. 1).  Leave only current year in file. 
#  Modified from wateryear_splitter.pl perl script.
#  
#  Depedencies:  
#
################################################################################
import os
import sys
import datetime as dt
from dateutil.parser import parse
import gzip

def get_date(str_datetime):
    #print 'get_date('+str_datetime+')'
    str_datetime = str_datetime.strip('"')
    if(str_datetime == ''):
        str_datetime = 'blank'
    try:
        #dtime = dt.datetime.strptime(str_datetime,"%Y-%m-%d %H:%M:%S")
        #print dtime
        dtime = parse(str_datetime)
        #print 'get_date('+str_datetime+') = ',isinstance(dtime,dt.datetime)
        return dtime
    except:
        #print 'get_date('+str_datetime+') = Not_Date'
        return 'Not_Date'

def get_wy(dt_datetime):
    year = dt_datetime.year
    month = dt_datetime.month
    if(month > 9):
        year = year + 1
    return year

def create_wydir(localpath,wy):   
    str_wydir = 'wy'+str(wy)
    wypath = localpath+os.sep+str_wydir
    if(os.path.exists(wypath) == False):
        print 'creating '+str_wydir
        os.mkdir(wypath)
    else:
        print str_wydir,' exists. using.'
    return wypath

def get_dat_stats(fdats):
    fdats.seek(0)   # set pointer at beginning of file

    # Define parameters for reading the dates and header on dat file
    i = 0
    dmax = dt.datetime.strptime('1990-01-01',"%Y-%m-%d")    # most recent date in file
    dmin = dt.datetime.now()                              # oldest date in file.  
    header = []
    wy_list = []
    for row in fdats:
        #"TOA5","L5_1_CR1000","CR1000","19598","CR1000.Std.15","CPU:Level5_1.CR1","56774","Table501"
        #"TIMESTAMP","RECORD","BattV","L501Temp","Well15_psi","Well15_WaterLevel_m","Well15_ToC","Well16_psi","Well16_WaterLevel_m","Well16_ToC"
        #"TS","RN","","","","","","","",""
        #"","","Smp","Smp","Smp","Smp","Smp","Smp","Smp","Smp"
        #"2011-10-06 08:30:00",0,10.4,9.44,5.737,-21.77,11.34,9.71,-19.51,11.53,0.135,0.006,9.02,0.235,0.019,9.5,0.181,0.015,9.66,0.205,0.011,10.14,0.284,0.03,12.14
        arow = row.split(',')
        field1 = arow[0].strip()
        dtrow = get_date(field1)
        
        # Collect Header Rows
        if(dtrow == 'Not_Date'):
            #print i,'row is header, appending',row
            header.append(row)
            if(i > 6):
                print "Too many header rows!"
                sys.exit()
        # If Data Row, find Oldest, Newest Dates and Water Years
        else:
            if(dmax < dtrow):
                dmax = dtrow
            if(dmin >  dtrow):
                dmin = dtrow

            # Make a list of all water years represented in file
            wy = get_wy(dtrow)
            if(len(wy_list) == 0):
                #print len(wy_list),') water year: ',wy,', date: ',dtrow
                wy_list.append(wy)
            add_wy = True
            for wyr in wy_list:
                if(wyr == wy):
                    add_wy = False
            if(add_wy == True):
                #print len(wy_list),') water year: ',wy,', date: ',dtrow
                wy_list.append(wy)
        i += 1
    fdats.seek(0)   # set pointer at beginning of file
    return header,wy_list,dmin,dmax

##########################################         
# start
print 'WATERYEAR SPLIT START'
localpath = os.path.dirname(os.path.realpath(__file__))
localpath = localpath+os.sep+'LoggerNet_Test' 
#localpath = localpath+os.sep+'ucnrs_Test'
print 'Data Directory: '+localpath
now = dt.date.today()
wy_current = get_wy(now)
print 'year: ',now.year,', month: ', now.month,', water year: ',wy_current

##########################################         
# Create archive directory and subdirectory for backup
path_archive = localpath+os.sep+'archive'
if(os.path.exists(path_archive) == False):
    print 'Creating archive directory'
    os.mkdir(path_archive)
else:
    print 'Archive directory exists.'
# Now create today's archive
gdt = dt.datetime.strftime(dt.datetime.now(),"%Y-%m-%d")
backupdir = 'backup'+gdt
path_backupdir = path_archive+os.sep+backupdir

if(os.path.exists(path_backupdir) == True):
    print 'WARNING '+backupdir+' already exists. Renaming old directory.'
    j = 0
    backupdir2 = path_archive+os.sep+backupdir+'.'+str(j)+'.backup'
    while (os.path.exists(backupdir2) == True):
        print 'oops. '+backupdir2+' exists. trying another name...'
        j += 1
        backupdir2 = path_archive+os.sep+backupdir+'.'+str(j)+'.backup'
    print 'Old backup directory '+backupdir+' moved to '+backupdir2
    os.rename(path_backupdir,backupdir2)

if(os.path.exists(path_backupdir) == False):
    print 'Creating '+path_backupdir
    os.mkdir(path_backupdir)
else:
    sys.exit(path_backupdir+' still exists. wtf? quitting.')


i = 0
k = 0
##########################################         
# List each .dat file in directory, get header, water years, min and max datetimes
for str_dat in os.listdir(localpath):
    k = k+1
    # parse file and directory names looking for .dat files
    pref,suf = os.path.splitext(str_dat)    
    #print 'testing '+str_dat+', pref: '+pref+', suf: '+suf    
    #adat = str_dat.split('.')
    #pref = adat[0]    
    #suf = adat[1]
       
    # Dat file found, load and get stats
    if(suf == '.dat' or suf == '.backup'):
        parts_public = str_dat.split('_Public')
        parts_status = str_dat.split('_Status')
        if(len(parts_public) == 1 and len(parts_status) == 1):
            i = i+1
            #print k,i,str_dat
            #continue
        
            print k,i,'Moving '+str_dat+' to archive '+backupdir
            os.rename(localpath+os.sep+str_dat,path_backupdir+os.sep+str_dat)
            if(os.path.exists(localpath+os.sep+str_dat) == True):
                sys.exit('WARNING! '+str_dat+' remains in main directory. Something didnt work. Quiting.')
    
            # open file
            path_fdat = path_backupdir+os.sep+str_dat
            fdat = open(path_fdat)
                         
            ##########################################      
            # Function to get header rows and Date start and end
            header,wy_list,dmin,dmax = get_dat_stats(fdat)
            #print str_dat,' WY_LIST: ',wy_list
            print str_dat,' Date start: ',dmin,', end: ',dmax,wy_list
            '''
            if(i >10):
                print 'Stopping'
                break
            '''
            ##########################################         
            # Open water year files and write rows, stop if already done 
            for wyr in wy_list:
                print wyr
                str_wy = 'wy'+str(wyr)
                str_wydat = str_dat
                #wydatpath = localpath+os.sep+str_wy
                if(wyr == wy_current):
                    wydatpath = localpath
                else:
                    wydatpath = create_wydir(localpath,wyr)     # This function will create directory if it doesn't exist
                #print wydatpath+os.sep+str_wydat
                
                # Check if file already exists, if so, rename the old file
                if(os.path.exists(wydatpath+os.sep+str_wydat) == True):   
                    print 'WARNING '+str_wydat+' already exists! Renaming old file'
                    j = 0
                    str_wydat_bak = str_dat+'.'+str_wy+'.backup'
                    while (os.path.exists(wydatpath+os.sep+str_wydat_bak) == True):
                        j += 1
                        str_wydat = str_dat+'.'+str_wy+'.'+str(j)+'.backup'
                    print 'Renaming old '+str_wydat+' to '+str_wydat_bak
                    os.rename(wydatpath+os.sep+str_wydat,wydatpath+os.sep+str_wydat_bak)
                
                # Once you have a unique filename, create and open file
                if(os.path.exists(wydatpath+os.sep+str_wydat) == False):
                    wydat = open(wydatpath+os.sep+str_wydat,'a')  
                    print 'CREATING '+wydatpath+os.sep+str_wydat
                else:
                    sys.exit('WARNING! Failed to move previous file. Quitting.')
                
                # Header
                for row in header:
                    wydat.write(row)      
                
                # Write data rows    
                i = 0
                fdat.seek(0)    # reset file iterator back to beginning of file
                for row in fdat:
                    arow = row.split(',')
                    field1 = arow[0].strip()
                    dtrow = get_date(field1)
                    if(dtrow != 'Not_Date'):
                        dtyear = get_wy(dtrow)
                        if(dtyear == wyr):
                            wydat.write(row)
                            i += 1
                print str_wy,': ',i,' rows written to '+str_dat
                wydat.close()
                
            ##########################################         
            # Gzip the DAT file into archive directory
            fdat.seek(0)
            j = 0
            # Make sure the gzip filename is unique
            # Check if file already exists, if so, rename the old gzip file
            path_gzip = path_fdat+'.gz'
            if(os.path.exists(path_gzip) == True):   
                print 'WARNING gzip file already exists!'
                j = 0
                path_gzip_old = path_fdat+'.'+str(j)+'.gz'
                while (os.path.exists(path_gzip_old) == True):
                    j += 1
                    path_gzip_old = path_fdat+'.'+str(j)+'.gz'
                print 'Renaming old gzip file '+path_gzip+' --> '+path_gzip_old
                os.rename(path_gzip,path_gzip_old)
            # Gzip datfile
            if(os.path.exists(path_gzip) == False):
                print 'Gzip into archive '+path_gzip
                gzdat = gzip.open(path_gzip,'wb')
                gzdat.writelines(fdat)
                fdat.close()
                gzdat.close()
                print 'CLOSED '+str_dat 
            
            # Delete DAT file - only do after confirming gzip file exists!
            if(os.path.exists(path_gzip) == True):
                os.remove(path_fdat)
                print 'Deleted source file '+str_dat
            else:
                sys.exit('GZIP Failed! Cowardly refusing to delete .dat file. Quitting.')
            print '\n'    

# Done 
print "\n"
print 'DONE! All ',i,' files of ',k,' in directory processed.'

