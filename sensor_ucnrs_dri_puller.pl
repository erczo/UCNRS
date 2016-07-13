#!/usr/bin/perl
################################################################################
# name: wrcc_dri_ucnrs_puller.p
# author: collin bode, email: collin@berkeley.edu
# date: 2016-05-09
#
# Purpose:  Performs a web-scrape of the WRCC website pulling data for 
# each UCNRS weather station managed by WRCC.
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
use strict;
use warnings;
use LWP::UserAgent;
use Date::Calc qw(:all);

# WRCC DRI Website
my $website = 'http://www.wrcc.dri.edu/cgi-bin/wea_list2.pl';
my $ua = LWP::UserAgent->new();  

# Days to pull data
my ($eyear, $emonth, $eday) = Today();
my ($syear,$smonth,$sday) = Add_Delta_Days($eyear,$emonth,$eday,-1);
$syear = substr($syear,2,2);
$smonth = sprintf("%02d",$smonth);
$sday = sprintf("%02d",$sday);
$eyear = substr($eyear,2,2);
$emonth = sprintf("%02d",$emonth);
$eday = sprintf("%02d",$eday);
#print "Start Date: ".$syear."-".$smonth."-".$sday."  End Date: ".$eyear."-".$emonth."-".$eday."\n";;

# WRCC has codes for each UC weather station
my @stations = ('ucac','ucab','hipk','whpt','ucbo',
'ucbm','ucde','ucbu','ucca','ucel','ucha','ucja',
'ucjp','ucmc','ucmo','ucrm','sagh','ucsc','ucse',
'ucsh','ucsr','ucgr','croo','wmtn','barc','ucyl');

# Define all POST variables required to make WRCC's website form to work
my $i = 1;
foreach my $station (@stations) { 
	#print $i.". Downloading ".$station."\n";
	
	# Define all POST Variables 
	my @post_data = [
		'stn' => $station,
		'smon' => $smonth,   
		'sday' => $sday,
		'syea' => $syear,  
		'emon' => $emonth,
		'eday' => $eday,  
		'eyea' => $eyear,     
		'secret' => '',                        
		'dfor' => '04',                        
		'srce' => 'W',                         
		'miss' => '03',                        
		'flag' => 'Y',                         
		'Dfmt' => '06',                        
		'Tfmt' => '01',                        
		'Head' => '03',                        
		'Deli' => '05',                         
		'unit' => 'M',
		'WsMon' => '01',
		'WsDay' => '01',
		'WeMon' => '12',
		'WeDay' => '31',
		'WsHou' => '00',
		'WeHou' => '24',
		'Submit Info' => 'Submit Info',
		'.cgifields' => 'unit',
		'.cgifields' => 'flag',
		'.cgifields' => 'srce'];
	
	# Heart of script. Send POST and get data back
	my $response = $ua->post($website, @post_data);
	my @content = $response->decoded_content();
	my $filepath = '/data/sensor/UCNRS/DRI/'.$station.'.tab';
	open(my $fout,'>>',$filepath) or die 'Could not open file';
	#print @content;
	print $fout @content;
	close $fout;
	$i +=1;
}
#print "Done!";
