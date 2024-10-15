'''
This script is for use by ToolikGIS in post-processing GPS data with OPUS to reduce repetitive motion injuries by GIS analysts when copying and pasting data.
241014 Rd
'''

## TODO suck it up and parse out cors bases

import os
import argparse
from datetime import datetime

if  __name__ == "__main__":

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description="""Read OPUS outputs and format for Toolik GIS average spreadsheets.""")
    parser.add_argument("-i", help=" : input folder of .eml files for each OPUS output", default = os.path.join(cwd, "eml"))
    parser.add_argument("-name", help=" : Name for output spreadsheet: ",
                        default="OPUS_Coordinates_" + datetime.today().strftime('%Y%m%d'))

    parser.add_argument("-o", help=" : Output spreadsheet ", default = os.path.join(cwd, "OPUS_Coordinates_" + datetime.today().strftime('%Y%m%d') + ".csv"))


    args = parser.parse_args()
    name = args.name
    emls = args.i
    csv = args.o
    if not os.path.exists(os.path.join(cwd, "txt")):
        txts = os.mkdir(os.path.join(cwd, "txt"))
    out_lines = ["Date,Filename,Easting,Northing,Ortho_Hgt,CORS_Used"]

    for file in os.listdir(emls):

        if not "aborting" in file:
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
                cors = ""

                row = [date, name, easting, northing, ortho, cors]
                out_lines.append(",".join(row))

    try:
        with open(csv, "w") as f:
            blah = "\n".join(out_lines)
            f.write(blah)
    except PermissionError:
        print("Do you have the output .csv open?")
        with open(os.path.join(cwd, datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"), "w") as f:
            blah = "\n".join(out_lines)
            f.write(blah)
        print("I'll forgive you. Output is here: ", os.path.join(cwd, datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"))

    for row in out_lines:
        p_row = ""
        row = row.split(",")
        for val in row:
            p_row += val + "\t"
        print(p_row)






