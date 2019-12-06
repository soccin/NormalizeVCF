#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import vcfpy
import sys

# Trick for making the dictionary a struct
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

# Nice clean place to put global values
class Globals:
  pass

# In DMP code these are settable from the command line
# These are the defaults in the code
# which match dmp_impact.v5.conf also
glbs=Globals()

glbs.TNRatio=float(5)
glbs.TotalDepth=float(0)
glbs.AlleleDepth=float(3)
glbs.VariantFreq=float(0.01)

# Open input, add FILTER header, and open output file
vin = vcfpy.Reader.from_path(sys.argv[1])
normal = sys.argv[2]
tumor = sys.argv[3]

# Alternative way of getting sample call record
# normal_idx=vin.header.samples.name_to_idx[normal]
# tumor_idx=vin.header.samples.name_to_idx[tumor]
#    tumor_data=rec.calls[tumor_idx]
#    normal_data=rec.calls[normal_idx]

vin.header.add_info_line(
    vcfpy.OrderedDict([
        ('ID', 'RESCUE'), ('Number',0), ('Type','Flag'),
        ('Description','DMP-Rescued mutation'), ('Source','DMP_Rescue.py'), ('Version','1.0.1')
        ]))

vout = vcfpy.Writer.from_path('/dev/stdout', vin.header)

for rec in vin:

    tumor_data=rec.call_for_sample[tumor].data
    normal_data=rec.call_for_sample[normal].data

    if 'REJECT' in rec.FILTER and normal_data['DP'] > 8 and tumor_data['DP'] > 14:
        tVAF=1.0*tumor_data['AD'][1]/tumor_data['DP']
        nVAF=1.0*normal_data['AD'][1]/normal_data['DP']

        if tVAF > glbs.TNRatio * nVAF:
            rec.FILTER=['PASS']
            rec.INFO['RESCUE']=True
            rec.INFO['SOMATIC']=True
            rec.INFO['VT']="SNP"
            rec.add_format('SS')
            rec.call_for_sample[tumor].data["SS"]=2
            rec.call_for_sample[normal].data["SS"]=0

    vout.write_record(rec)



