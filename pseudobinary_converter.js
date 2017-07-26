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
const goes = require('./goes');
//import * as goes from './goes';

// Test the Pseudo-bindary conversion function
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
	var test_string = 'BEC0035C17197002104G49-0NN301WXW01046 B^h@YJF@[F@\F@[F@@F@qF@rF@qF@@F@@F@@F@@F@@F@@F@@DjqDj]DjgEMTEIiEKt@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT^DT]DT]DlHD{XGmXChvB^h@Y@F@\F@]F@\F@@F@sF@uF@rF@@F@@F@@F@@F@@F@@F@@DjgDjLDjWEOUEKZEME@OqF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DT]DT_Dl@D{XGmXChvB^h@XNF@]F@^F@]F@@F@wF@xF@uF@@F@@F@@F@@F@@F@@F@@DjRDipDj@ERPEN_EPd@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkzD{XGmXChvB^h@XDF@]F@^F@\F@AF@vF@xF@tF@@F@@F@@F@@F@@F@@F@@Di{DifDioETpEPSERy@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT`DT_DT`DkvD{XGmXChvB^h@WzF@\F@]F@\F@@F@tF@uF@rF@@F@@F@@F@@F@@F@@F@@DjHDimDizEUgEQ|ESn@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DSGDTZDk|D{XGmXChvB^h@WpF@^F@^F@]F@@F@xF@xF@uF@@F@@F@@F@@F@@F@@F@@DjgDi{DjUEVSER[ETP@OrF@@F@@I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~I~DT_DTMDT^DlED{XGmXChv ';
if(param == 'test' ) {
	lrgs_strings.push(test_string);
	booTest = true;
} 
else if ( param == 'debug' ) {
	lrgs_strings.push(test_string);
	booDebug = true;
	booTest = true;
}
else { 	// Argv: load file from argument
	var fs = require('fs')
	lrgs_strings = fs.readFileSync(param).toString().split("\n");
}

// MAIN
for (var lrgs_string of lrgs_strings) {
	if(lrgs_string.length > 18) {
		// Parse GOES metadata and separate out Message
		var goes_array = goes.DCPstring2array(lrgs_string,booDebug);
		console.log("GOES Array:");
		console.log(goes_array);
		
		// Parse Message, i.e. the data content of transmission
		var message = goes_array["message"];
		console.log("message length: "+message.length);
		var value_set = goes.pseudostring2array(message,booDebug);
		//console.log(value_set.toString());
		
		// Data Row Constructor - separate rows of data and add timestamps.
		var data_set = goes.values2data(goes_array,value_set,column_num,booDebug);
		//console.log(data_set.toString());

		// Export Message content to CSV file
		require("fs").appendFile( 
			"pbstring_js_out.csv", 
			value_set.toString()+'\n',
			function(err) { console.log(err ? "Error on export: "+err : "ok")}
		);
	}
}
console.log("DONE!");
