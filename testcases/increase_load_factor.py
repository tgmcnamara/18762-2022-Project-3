import os
import sys
from unittest import case
import numpy as np

# Crude function to increase all of the generator and load
# Ps and Qs by a constant factor, which can make a network
# infeasible if you increase it enough
def increase_load_factor(raw_file, load_factor):
    out_file = raw_file.strip('.RAW').strip(".raw") + ("_load_factor_%.3f.RAW" % load_factor)
    in_gen_section = False
    in_load_section = False
    in_ptr = open(raw_file, 'r')
    out_ptr = open(out_file, 'w')
    for line in in_ptr:
        if "END OF GENERATOR DATA" in line:
            in_gen_section = False
        if "END OF LOAD DATA" in line:
            in_load_section = False
        if line[:2] == "@!":
            out_ptr.write(line)
            continue
        if "BEGIN GENERATOR DATA" in line:
            in_gen_section = True
            out_ptr.write(line)
            continue
        if "BEGIN LOAD DATA" in line:
            in_load_section = True
            out_ptr.write(line)
            continue        
        if in_gen_section:
            line_data = line.strip('\n').replace(' ', '').split(',')
            # Pg
            line_data[2] = "%.6f" % (float(line_data[2])*load_factor) 
            # Qg
            line_data[3] = "%.6f" % (float(line_data[3])*load_factor) 
            # Qmin = float(line_data[4])
            line_data[4] = "%.6f" % (float(line_data[4])*load_factor) 
            # Qmax = float(line_data[5])
            line_data[5] = "%.6f" % (float(line_data[5])*load_factor) 
            line = ",".join(map(str,line_data)) + "\n"
        elif in_load_section:
            line_data = line.strip('\n').replace(' ', '').split(',')
            # Pl = float(line_data[5])
            line_data[5] = "%.6f" % (float(line_data[5])*load_factor )
            # Ql = float(line_data[6])
            line_data[6] = "%.6f" % (float(line_data[6])*load_factor) 
            line = ",".join(map(str,line_data)) + "\n"
        out_ptr.write(line)                
    in_ptr.close()
    out_ptr.close()

if __name__ == "__main__":
    print(sys.argv[1:])
    raw_file = sys.argv[1]
    load_factor = float(sys.argv[2])
    increase_load_factor(raw_file, load_factor)