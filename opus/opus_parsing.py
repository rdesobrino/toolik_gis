"""
This script is for use by ToolikGIS in post-processing GPS data with OPUS to reduce repetitive motion injuries by GIS analysts when copying and pasting data.
241014 Rd
"""

import os
import argparse
from datetime import datetime

if __name__ == "__main__":

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description="""Read OPUS outputs from eml folder and output for Toolik GIS average spreadsheets.""")
    parser.add_argument("-i", help=" : input folder of .eml files for each OPUS output", default = os.path.join(cwd, "eml"))
    parser.add_argument("-name", help=" : optional name for output spreadsheet",
                        default="OPUS_Coordinates_" + datetime.today().strftime('%Y%m%d'))

    parser.add_argument("-o", help=" : output spreadsheet filepath", default = os.path.join(cwd, "OPUS_Coordinates_" + datetime.today().strftime('%Y%m%d') + ".csv"))

    args = parser.parse_args()
    name = args.name
    emls = args.i
    if name:
        csv = os.path.join(cwd, name + ".csv")
    else:
        csv = args.o
    out_lines = ["Date,Filename,Easting,Northing,Ortho_Hgt,CORS_Used,RMS,Duration"]

    def duration(start,stop):
        [h,m,s] = start.split(":")
        start = float(h) +float(m)/60 + float(s)/3600
        [h, m, s] = stop.split(":")
        stop = float(h) + float(m) / 60 + float(s) / 3600
        return stop - start

    for file in os.listdir(emls):
        if not "aborting" in file: # only search successful opuses
            with open(os.path.join(emls, file), "r") as eml:
                lines = eml.readlines()
                text = "\t".join(lines)

                date = text[text.find("START: ")+len("START: "):text.find("START: ")+len("START: ")+10]
                name=text[text.find("FILE: ")+len("FILE: "):text.find("FILE: ")+len("FILE: ")+text[text.find("FILE: ")+len("FILE: "):].find(" ")]

                e_search = text[text.find("Easting (X)  [meters]")+len("Easting (X)  [meters]"):].split(" ")
                easting = [char for char in e_search if char != ''][0]

                n_search = text[text.find("Northing (Y) [meters]")+len("Northing (Y) [meters]"):].split(" ")
                northing = [char for char in n_search if char != ''][0]

                o_search = text[text.find("ORTHO HGT:") + len("ORTHO HGT:"):].split(" ")
                ortho = [char[:-3] for char in o_search if char != ''][0]

                c_search = text[text.find("PID       DESIGNATION                        LATITUDE    LONGITUDE DISTANCE(m)") + len("PID       DESIGNATION                        LATITUDE    LONGITUDE DISTANCE(m)"):].split("\n")
                cors = ""
                for line in c_search[1:4]:
                    cors += line.split(" ")[1] + " "

                rms_search = text[text.find("RMS:") + len("RMS:"):].split(" ")
                rms = [char for char in rms_search if char != ''][0].strip()[:-3]

                start_search = text[text.find("START:") + len("START:"):].split(" ")
                start = [char for char in start_search if char != ''][1]
                stop_search = text[text.find("STOP:") + len("START:"):].split(" ")
                stop = [char for char in stop_search if char != ''][1]
                dur = str(round(duration(start,stop),3))
                if dur == '23.983':
                    dur = '24'

                row = [date, name, easting, northing, ortho, cors[:-1],rms,dur]
                out_lines.append(",".join(row))
        else: print("ABORTED:    ", file)
    try:
        with open(csv, "w") as f:
            blah = "\n".join(out_lines)
            f.write(blah)
    except PermissionError:
        print("Do you have the output .csv open?")
        with open(os.path.join(cwd, datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"), "w") as f:
            blah = "\n".join(out_lines)
            f.write(blah)
        print("Output is here instead: ", os.path.join(cwd, datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"))

    #prints to command line for copy paste
    for row in out_lines:
        p_row = ""
        row = row.split(",")
        for val in row:
            p_row += val + "\t"
        print(p_row)







