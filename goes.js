/* 
GOES Satellite functions for pseudobinary conversion and for 
parsing DCP download headers. 

Campbell Scientific data loggers use the GOES satellite system to transmit
from remote locations.  To keep transmissions to a minimum, they use pseudobinary.
Pseudobinary is ASCII characters that can be decoded into normal numbers. 
*/

function DCPstring2array (lrgs,booTest=false,booDebug=false) {
	/*
	DCP METADATA
	Each transmission is prefixed with a DCP transmission metadata string.  These
	should always be 37 characters long and are not in pseudobindary.  This must be
	parsed and separated from the message before any conversion can take place.  
	NOTE: the data does not have timestamps.  It must be interpreted from the medata 
	timestamp. 
	*/
	var dcp_parts = {};
	/*
	[dcp_address 8][timestamp 11][fail 1][signal_strength 2][freq_offset 2][modulation]
	[0 - 7]			[8 - 18]	 [19]	 [20,21]			[22,23]			[24]
	 
	[data_quality][chan][spacecraft][ds_source][message_length][message]
	[25]		  [26,27,28] [29]	[30,31]		[32,33,34,35,36] [37+] 
	*/
	// DCP address - 8 digit hex
	dcp_parts["dcp_address"] = lrgs.substring(0,8);
	// 11 digit timestamp YYDDDHHMMSS  Note the julian day
	dcp_parts["timestamp"] = lrgs.substring(8,19);
	// 1 digit failure code (G/?)
	dcp_parts["fail"] = lrgs.substring(19,20);
	// 2 digit signal strength (32-57)
	dcp_parts["signal_strength"] = lrgs.substring(20,22);
	// 2 digit frequency offset (+-0-9)
	dcp_parts["freq_offset"] = lrgs.substring(22,24);
	// 1 digit modulation index (N/L/H)
	dcp_parts["mod"] = lrgs.substring(24,25);
	// 1 digit data quality (N/F/P)
	dcp_parts["data_quality"] = lrgs.substring(25,26);
	// 3 digit GOES receive channel
	dcp_parts["chan"] = lrgs.substring(26,29);
	// 1 digit GOES spacecraft indicatory (E/W)
	dcp_parts["spacecraft"] = lrgs.substring(29,30);
	// 2 digit data source code (XW = sioux falls, west)
	dcp_parts["ds_source"] = lrgs.substring(30,32);
	// 5 digit message data length
	dcp_parts["message_length"] = lrgs.substring(32,37);
	// MESSAGE BODY 6 bits of every byte used. 
	// unclear whether blank space should be stripped: .trim()
	dcp_parts["message"] = lrgs.substring(37,lrgs.length+1).trim();
	return dcp_parts;
}

function char2bin (inchar,booTest=false,booDebug=false) {
	/* 
	Pseudobinary requires conversion from ASCII character
	to binary bits, but only the last 6 digits of the binary.
	If you get that wrong, the values are off.
	*/
	var unint = inchar.charCodeAt(0);
	var fullbit = unint.toString(2);
	var fb_len = fullbit.length;
	var bit = fullbit.substring(fb_len-6,fb_len);
	var b_len = bit.length;
	if(booDebug == true) {
		console.log(inchar+'-->'+unint+'-->'+fullbit+'('+fb_len+')-->'+bit+'('+b_len+')');
	}
	return bit;
}

function pseudostring2array (pbstring,booTest=false,booDebug=false) {
	/*
	PSEUDOBINARY
	The number is reconstructed from three characters.  Each character is
	converted into 6 binary bits.  ASCII characters can have from 6 to 11 bits.
	Only the last 6 bits are used. If a string cannot be divided into sets of 3 
	characters, this translation cannot work.  

	The pseudobinary converts to 3 parts: sign, exponent, and mantissa. 
	The 18 bits are used as follows:
	bits	Function
	0-1			Transmission info. unused.
	2				Sign: 1 or -1
	3-4			Decimals: exponent is 0,1,2,3 which is the number of decimal points.
	        This is translated into 1,0.1,0.01,0.001 
	5-18		Mantissa:  bit list which is powers of 2, then added up. 2^bitpower
					12 bits with the first the highest power and last the lowest.	
	*/
	var values = [];  // Array of the values decoded from the pseudobinary string
	for (var i = 0; i < pbstring.length; i+=3) {
		/*
		var char1 = pbstring.charCodeAt(i).toString(2);
		var char2 = pbstring.charCodeAt(i+1).toString(2);
		var char3 = pbstring.charCodeAt(i+2).toString(2);

		var bit1 = char1.substring(char1.length -6,char1.length);
		var bit2 = char2.substring(char2.length -6,char2.length);
		var bit3 = char3.substring(char3.length -6,char3.length);
		
		if(booDebug == true) {
			console.log(i+' char1('+pbstring.substring(i,i+1)+')-->'+char1+"-->"+bit1
			+', char2('+pbstring.substring(i+1,i+2)+')-->'+char2+"-->"+bit2
			+', char3('+pbstring.substring(i+2,i+3)+')-->'+char3+"-->"+bit3);	
		}	
		*/	
		var bit1 = char2bin(pbstring.substring(i,i+1));
		var bit2 = char2bin(pbstring.substring(i+1,i+2));
		var bit3 = char2bin(pbstring.substring(i+2,i+3));
		var bits = bit1+bit2+bit3;
		console.log(i+'. '+bits+'('+bits.length+')');

		//bits ='012345678901234567'; // test srting
		var bitsign = Number(bits.substring(2,3));
		var bitdecimal1 = Number(bits.substring(3,4));
		var bitdecimal2 = Number(bits.substring(4,5));
		var bitmantissa = bits.substring(5,18);
		//console.log(i+' sign: '+bitsign+', decimals: '+bitdecimal1+', '+bitdecimal2+', mant: '+bitmantissa);

		// Convert from bits to meaningful number parts
		var sign = Math.pow(-1,bitsign);
		var decimal = Math.pow(10, -1 * (2*bitdecimal1 + bitdecimal2));
		var mantissa = 0;
		//console.log(i+' sign: '+bitsign+'-->'+sign+', decimals: '+(2*bitdecimal1 + bitdecimal2)+' --> '+decimal);
		for (var j = 0; j < bitmantissa.length; j++) {
			var k = 12 - j;
			var power = Math.pow(2,k);
			var mbit = Number(bitmantissa.substring(j,j+1));
			var mval = mbit * power;
			mantissa += mval;
			//console.log(i+' mantissa: '+mantissa+', mbit: '+mbit+', power: '+power);
		}
		var value = sign * decimal * mantissa;
		if(value == -8190 || value == 8190) {
			value = NaN;
		}
		values.push(value);
		if(booDebug == true) {
			console.log(i+' Value: '+value+', sign: '+sign+', decmal: '+decimal+', mantissa: '+mantissa);
		}
	}
	return values;
}

function values2data (goes_array,value_set,column_num,booTest=false,booDebug=false) {
	var data_rows = [];
	// Timestamp - this is the time of transmission, so it is the last timestamp
	// convert to ISO standard time UTC, provide offset. 
	// Jim Norris says the GOES transmitter waits 22 minutes before transmission
	var dcp_timestamp = goes_array["timestamp"];
	console.log("DCP Timestamp: "+dcp_timestamp);
	var year = dcp_timestamp.substring(0,2);
	var julian_day = dcp_timestamp.substring(2,5);
	var hour = dcp_timestamp.substring(5,7);
	var minute = dcp_timestamp.substring(7,9);
	var second = dcp_timestamp.substring(9,11);
	console.log("Year: "+year+", Julian Day: "+julian_day+", Hour: "+hour+", Min: "+minute+", Sec:"+second);

	// Separate into data rows.  For hourly transmissions this should be 6 rows. 
	// Do I assume hourly?  Calculate?  Input as argument? Default hourly.
	row = []
	for(var value of value_set) {
		row.push(value);
		if(value == 671) {
			data_rows.push(row)
			console.log("Rows: "+data_rows.length);
			row = [];		
		}
	}
	console.log("End of values in value_set. Now have "+row.length+" rows.");


	// Row Timestamps - back calculate the time for each row, assuming interval based 
	// on transmission frequency and the number of rows.  Default 10 min.

	// Nan Values:   convert -8190 values to NaNs.  
	
	return data_rows;
}

exports.DCPstring2array = DCPstring2array;
exports.char2bin = char2bin;
exports.pseudostring2array = pseudostring2array;
exports.values2data = values2data;