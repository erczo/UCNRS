#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
################################################################################
# name: pseudobinary_converter.py
# author: collin bode, email: collin@berkeley.edu
# date: 2017-07-12
#
# Purpose:  Take GOES Satellite output in Campbell Scientific 
# pseudobinary strings and convert to normal text
# Based on Appendix B BASIC programin TX312 transmitter manual (p.45)
################################################################################

def char2bin(inchar):
    # The pseudobinary is spread across 3 ASCII characters
    # Each character binary has 9 digits.  
    # 1,2 are transmission info
    # 3 is unknown
    # 4-9 are the payload digits
    pso = ord(inchar)
    psb = bin(pso)
    pss = str(psb)
    if(len(pss) == 9):
        psc = pss[3:len(pss)]
    else:
        psc = pss[2:len(pss)]
    print(inchar,len(inchar),pso,len(str(pso)),psb,len(psb),pss,len(pss),psc,len(psc))
    return psc

def pseudo2numbers(ps):
    row = []
    for j in range(0,psl-1,3):
        c1 = char2bin(ps[j])
        c2 = char2bin(ps[j+1])
        c3 = char2bin(ps[j+2])
        
        # The number is reconstructed from three parts: sign, exponent, and mantissa
        # Strip transmission & unknown digits
        # Sign: 1 or -1
        # Decimals: exponent is 0,1,2,3 which is the number of decimal points.
        #           This is translated into 1,0.1,0.01,0.001 
        # Mantissa:  digit list which is powers of 2, then added up. 2^b

        sign = pow(-1,int(c1[2]))
        decimals = pow(10,-1*(int(c1[4]) + 2 * int(c1[3])))
        
        # 13 binary positions (0-12) reversed
        mantissa = c1[5]+c2+c3   
        values = []
        for p in range(0,13):
            b = 12-p
            power2 = pow(2,b)
            values.append(int(mantissa[p])*power2)   
            #print(p,b,power2,values[p])
        total = sum(values)
        number = sign * total * decimals
        row.append(number)
        #print('Final: ',number)    
    return row
    

pseudobinary_test = [
    "B]v@YJV",
    "B]v@WfF@pF@qF@nF@AFAkFAnFAiF@@F@@F@@F@@F@@F@@F@@DjxDbmDZs",
    "B]v@T^FAHFAJFAGF@AFBhFBjFBgF@@F@@F@@F@@F@@F@\$$PX?V$~$$yEUy$BWX$I]$M%E~$C$EIC7wc6P>,$$u>$~$$^$w$NqkQ$~A'l/\_]~hX$)X?:DoO",
    "B]v@RzFA\FAdFAXF@DFCUFCaFCNF@@F@@F@@F@@F@@F@@F@@DgnDgBDg[EeJEa_EcV@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~DTbDT^DT`Dj@D{XGmXChvB]v@RpFAlFArFAdF@DFCpFC|FCaF@@F@@F@@F@@F@@F@@F@@DgLDfjDf{EgYEcLEea@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~DTbDT_DT`DipD{XGmXChvB]v@Q~FAvFBAFApF@EFDEFDPFC|F@@F@@F@@F@@F@@F@@F@@DfqDf`DfhEfzEdSEfG@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~DTbDT_DT`DieD{XGmXChvB]v@QtFAtFAvFApF@BFD@FDHFCtF@@F@@F@@F@@F@@F@@F@@DfjDf\DfbEfsEcVEeX@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~DTbDT_DTaDiVD{XGmXChvB]v@QjFAeFAuFASF@LFCRFCtFBlF@@F@@F@@F@@F@@F@@F@@DfxDfYDfdEfXEbEEdU@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$.$:;Q$/$$`DSHDTZDiAD{XGmXChvB]v@Q`FAHFASF@$F@FFBTFBlFBBF@@F@@F@@F@@F@@F@@F@@DgBDfqDfyEeCEafEcg@OsF@@F@@I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~I$~DTcDTNDT`DhzD{XGmXChv",
    "3$^t$m$QM$R$BW$$$$0WV$BB$W$v%Fq$0YDLuC#W$WE$$$V",
    "B^@Cn|F@eF@oF@`F@EFAIFA]F@~F@@F@@F@@F@@F@@F@@F@@DaAD`mD`yBLeEyWE{z@OsF@@F@@I?7l>v]oj\$c$K/]o$[2ZNd$@$6Y$.ooS *$$$$$($$($4$#>$Kw$CbST$Gx AY$ID4$Pw$Avt$0$E+>_<=m#\80lEn$$S.\V5|$FM$$$C@^F@aF$$VoSBMJ$$$P:$YC~3zjdk:njj/iz9b*yR^{v-8=$AM$f^'$$RRLq"
]
#pseudobinary_test = ['DSR']
#pseudobinary_test = ["3$^t$m$QM$R$BW$$$$0WV$BB$W$v%Fq$0YDLuC#W$WE$$$V"]
#pseudobinary_test = ["B]v@YJ"]
i = 0
for ps in pseudobinary_test:
    i += 1
    psl = len(ps)
    psmod = psl%3
    print(i,psl,psmod)
    if(psmod != 0):
        print('Pseudobinary has character set('+str(psl)+') that is not divisable by 3('+str(psmod)+').  Skipping',ps)
        continue
    # Convert the pseudobinary string to number array
    row = pseudo2numbers(ps)
    print('Pseudobinary:',ps)
    print('Numeric',row)
        