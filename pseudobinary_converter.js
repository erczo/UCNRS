// pseudobinary_converter.js
/*
Campbell Scientific data loggers use the GOES satellite system to transmit
from remote locations.  To keep transmissions to a minimum, they use pseudobinary.
Pseudobinary is ASCII characters that can be decoded into normal numbers. 

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

DCP METADATA
Each transmission is prefixed with a DCP transmission metadata string.  These
should always be 37 characters long and are not in pseudobindary.  This must be
parsed and separated from the message before any conversion can take place.  
NOTE: the data does not have timestamps.  It must be interpreted from the medata 
timestamp. 
*/


function DCPstring2array(lrgs) {
	dcp_parts = [];
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
	dcp_parts["message"] = lrgs.substring(37,lrgs.length+1);
	return dcp_parts;
} 

function pseudostring2array(pbstring) {
	var values = [];  // Array of the values decoded from the pseudobinary string
	for (var i = 0; i < pbstring.length; i+=3) {
		var char1 = pbstring.charCodeAt(i).toString(2);
		var char2 = pbstring.charCodeAt(i+1).toString(2);
		var char3 = pbstring.charCodeAt(i+2).toString(2);

		var bit1 = char1.substring(char1.length -6,char1.length);
		var bit2 = char2.substring(char2.length -6,char2.length);
		var bit3 = char3.substring(char3.length -6,char3.length);
		
		if(param == 'debug') {
			console.log(i+' char1('+pbstring.substring(i,i+1)+')-->'+char1+"-->"+bit1
			+', char2('+pbstring.substring(i+1,i+2)+')-->'+char2+"-->"+bit2
			+', char3('+pbstring.substring(i+2,i+3)+')-->'+char3+"-->"+bit3);	
		}		
		var bits = bit1+bit2+bit3;
		//console.log(i+' '+bits+' '+bits.length);

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
		values.push(value);
		if(param == 'debug') {
			console.log(i+' Value: '+value+', sign: '+sign+', decmal: '+decimal+', mantissa: '+mantissa);
		}
	}
	return values;
}

function values2data(goes_array,value_set,column_num) {
	var data_rows = [];
	// Timestamp - this is the time of transmission, so it is the last timestamp
	// convert to ISO standard time UTC, provide offset. 

	// Separate into data rows.  For hourly transmissions this should be 6 rows. 
	// Do I assume hourly?  Calculate?  Input as argument? Default hourly.

	// Row Timestamps - back calculate the time for each row, assuming interval based 
	// on transmission frequency and the number of rows.  Default 10 min.

	// Nan Values:   convert -8190 values to NaNs.  
	
	return data_rows;
}

//
// Test the Pseudo-bindary conversion function
//
// Argv: Accept an argument
if (process.argv.length <= 2) {
    console.log("Usage: " + __filename + " SOME_PARAM");
    process.exit(-1);
}
var param = process.argv[2];
console.log(__filename+' param: ' + param);

// Argv: command line argument can be test, debug, or a file name
var lrgs_strings = [];
var column_num = 58;
if(param == 'test' || param == 'debug') {
	column_num = 58;
	var test_string = 'BEC0035C17197002104G49-0NN301WXW01046 B^h@YJF@[F@\F@[F@@F@qF@rF@qF@@F@@F@@F@@F@@F@@F@@DjqDj]DjgEMTEIiEKt@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT^DT]DT]DlHD{XGmXChvB^h@Y@F@\F@]F@\F@@F@sF@uF@rF@@F@@F@@F@@F@@F@@F@@DjgDjLDjWEOUEKZEME@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DT]DT_Dl@D{XGmXChvB^h@XNF@]F@^F@]F@@F@wF@xF@uF@@F@@F@@F@@F@@F@@F@@DjRDipDj@ERPEN_EPd@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkzD{XGmXChvB^h@XDF@]F@^F@\F@AF@vF@xF@tF@@F@@F@@F@@F@@F@@F@@Di{DifDioETpEPSERy@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkvD{XGmXChvB^h@WzF@\F@]F@\F@@F@tF@uF@rF@@F@@F@@F@@F@@F@@F@@DjHDimDizEUgEQ|ESn@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DSGDTZDk|D{XGmXChvB^h@WpF@^F@^F@]F@@F@xF@xF@uF@@F@@F@@F@@F@@F@@F@@DjgDi{DjUEVSER[ETP@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DTMDT^DlED{XGmXChv ';
	lrgs_strings.push(test_string);
	console.log(param);
} 
else { 	// Argv: load file from argument
	var fs = require('fs')
	lrgs_strings = fs.readFileSync(param).toString().split("\n");
}

// MAIN
for (var lrgs_string of lrgs_strings) {
	if(lrgs_string.length > 18) {
		// Parse GOES metadata and separate out Message
		var goes_array = DCPstring2array(lrgs_string);
		console.log("GOES Array:");
		console.log(goes_array);
		
		// Parse Message, i.e. the data content of transmission
		var message = goes_array["message"];
		console.log("message length: "+message.length);
		var value_set = pseudostring2array(message);
		//console.log(value_set.toString());
		
		// Data Row Constructor - separate rows of data and add timestamps.
		var data_set = values2data(goes_array,value_set,column_num);
		console.log(data_set.toString());

		// Export Message content to CSV file
		require("fs").appendFile( 
			"pbstring_js_out.csv", 
			value_set.toString()+'\n',
			function(err) { console.log(err ? "Error on export: "+err : "ok")}
		);
	}
}
console.log("DONE!");
