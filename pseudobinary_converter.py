#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# name: pseudobinary_converter.py
# author: collin bode, email: collin@berkeley.edu
# date: 2017-07-12
#
# Purpose:  Take GOES Satellite output in Campbell Scientific 
# pseudobinary strings and convert to normal text
# Based on Appendix B BASIC programin TX312 transmitter manual (p.45)
#
# Pseudo-binary Translation into a normal number
# The number is reconstructed from three characters.  Each character is
# converted into 6 binary bits.  ASCII bits have more than 6 bits,
# Some of which are used for transmission or are unknown, so only the last 
# 6 are used. If a string cannot be divided into sets of 3 characters, this
# translation cannot work.  
# 
# The pseudobinary converts to 3 parts: sign, exponent, and mantissa. 
# The 18 bits are used as follows:
# bits    Function
# 0-1         Transmission info. unused.
# 2               Sign: 1 or -1
# 3-4         Decimals: exponent is 0,1,2,3 which is the number of decimal points.
#         This is translated into 1,0.1,0.01,0.001 
# 5-18        Mantissa:  bit list which is powers of 2, then added up. 2^bitpower
#                 12 bits with the first the highest power and last the lowest.   
################################################################################
import sys
#from __future__ import print_function  # Only needed for Python 2
pseudobinary_test = ['BEC0035C17197002104G49-0NN301WXW01046 B^h@YJF@[F@\F@[F@@F@qF@rF@qF@@F@@F@@F@@F@@F@@F@@DjqDj]DjgEMTEIiEKt@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT^DT]DT]DlHD{XGmXChvB^h@Y@F@\F@]F@\F@@F@sF@uF@rF@@F@@F@@F@@F@@F@@F@@DjgDjLDjWEOUEKZEME@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DT]DT_Dl@D{XGmXChvB^h@XNF@]F@^F@]F@@F@wF@xF@uF@@F@@F@@F@@F@@F@@F@@DjRDipDj@ERPEN_EPd@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkzD{XGmXChvB^h@XDF@]F@^F@\F@AF@vF@xF@tF@@F@@F@@F@@F@@F@@F@@Di{DifDioETpEPSERy@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkvD{XGmXChvB^h@WzF@\F@]F@\F@@F@tF@uF@rF@@F@@F@@F@@F@@F@@F@@DjHDimDizEUgEQ|ESn@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DSGDTZDk|D{XGmXChvB^h@WpF@^F@^F@]F@@F@xF@xF@uF@@F@@F@@F@@F@@F@@F@@DjgDi{DjUEVSER[ETP@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DTMDT^DlED{XGmXChv ']
param = 'test' # test, debug, input file

def DCPstring2array(lrgs):
    dcp_parts = {}
    '''
    DCP example: BEC0035C17197002104G49-0NN301WXW01046
    DCP parts:   [dcp_address 8][timestamp 11][fail 1][signal_strength 2][freq_offset 2][modulation]
    position:    [0 - 7]         [8 - 18]     [19]    [20,21]            [22,23]         [24]
     
    DCP parts:   [data_quality][chan][spacecraft][ds_source][message_length][message]
    position:    [25]          [26,27,28] [29]   [30,31]     [32,33,34,35,36] [37+] 
    '''
    # DCP address - 8 digit hex
    dcp_parts["dcp_address"] = lrgs[0:8]
    # 11 digit timestamp YYDDDHHMMSS  Note the julian day
    dcp_parts["timestamp"] = lrgs[8:19]
    # 1 digit failure code (G/?)
    dcp_parts["fail"] = lrgs[19:20]
    # 2 digit signal strength (32-57)
    dcp_parts["signal_strength"] = lrgs[20:22]
    # 2 digit frequency offset (+-0-9)
    dcp_parts["freq_offset"] = lrgs[22:24]
    # 1 digit modulation index (N/L/H)
    dcp_parts["mod"] = lrgs[24:25]
    # 1 digit data quality (N/F/P)
    dcp_parts["data_quality"] = lrgs[25:26]
    # 3 digit GOES receive channel
    dcp_parts["chan"] = lrgs[26:29]
    # 1 digit GOES spacecraft indicatory (E/W)
    dcp_parts["spacecraft"] = lrgs[29:30]
    # 2 digit data source code (XW = sioux falls, west)
    dcp_parts["ds_source"] = lrgs[30:32]
    # 5 digit message data length
    dcp_parts["message_length"] = lrgs[32:37]
    # MESSAGE BODY 6 bits of every byte used. 
    # unclear whether blank space should be stripped
    dcp_parts["message"] = lrgs[37:len(lrgs)+1]
    return dcp_parts;

def char2bin(inchar):
    # The pseudobinary is spread across 3 ASCII characters
    # Each character binary has 9 digits.  
    # 1,2 are transmission info
    # 3 is unknown
    # 4-9 are the payload digits
    pso = ord(inchar)
    psb = bin(pso)
    pss = str(psb)
    psc = pss[len(pss)-6:len(pss)]
    if(param == 'debug'):
        print(inchar,len(inchar),pso,len(str(pso)),psb,len(psb),pss,len(pss),psc,len(psc))
    return psc

def pseudostring2array(pbstring):
    values = []
    for j in range(0,len(pbstring),3):
        bit1 = char2bin(pbstring[j])
        bit2 = char2bin(pbstring[j+1])
        bit3 = char2bin(pbstring[j+2])
        bits = bit1+bit2+bit3

        # The number is reconstructed from three parts: sign, exponent, and mantissa
        # Strip transmission & unknown digits
        # Sign: 1 or -1
        # Decimals: exponent is 0,1,2,3 which is the number of decimal points.
        #           This is translated into 1,0.1,0.01,0.001 
        # Mantissa:  digit list which is powers of 2, then added up. 2^b
        sign = pow(-1,int(bits[2]))
        decimals = pow(10,-1*(2 * int(bits[3])+int(bits[4])))
        bitmantissa = bits[5:18]  # 13 binary positions (0-12) reversed
        mantissa = 0
        for p in range(0,13):
            b = 12-p
            power2 = pow(2,b)
            value = int(bitmantissa[p])*power2   
            mantissa += value
            #print(p,b,power2,value,mantissa)
        number = sign * mantissa * decimals
        if(param == 'debug'):
            print(number,' <-- ',sign,decimals,mantissa)
        values.append(number)
    return values

    
# Test the Pseudo-binary conversion function
if(len(sys.argv) != 2):
    print('USAGE:',__file__,'<filename,test, or debug>')
    sys.exit()
else:
    param = sys.argv[1]

if(param == 'test' or param == 'debug'):
    dcp_strings = pseudobinary_test
else:
    dcp_strings = []
    fin = open(param,'r')
    for row in fin:
        dcp_strings.append(row)
    fin.close()

# Open CSV file for writing
fout = open('pbout_py.csv','w')

i = 0
for lrgs_string in dcp_strings:
    if(len(lrgs_string) > 18):
        i += 1
        # Parse the DCP header
        goes_array = DCPstring2array(lrgs_string)
        print("GOES Array:",goes_array)
        message = goes_array["message"].strip()
        psl = len(message)
        psmod = psl%3
        if(param == 'debug'):
            print(i,psl,psmod)
        if(psmod != 0):
            print('Pseudobinary message has character set('+str(psl)+') that is not divisable by 3('+str(psmod)+').  Skipping')
            continue
        # Convert the pseudobinary string to number array
        row = pseudostring2array(message)
        if(param == 'debug'):
            print('Pseudobinary:',message)
        print('message length:',len(message))
        print(row,file=fout)

fout.close()
print('DONE!')
        