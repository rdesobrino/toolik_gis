'''
This script is to be executed from an ArcGIS Python Shell to generate the required files used in DJI Pilot UAS Planning by Toolik GIS
At the time of its development, DJI would not take any ol kml file
Developed May 2024, Rachel de Sobrino
'''
import arcpy
import os
import argparse
import shutil
import sys

if  __name__ == "__main__":

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    cwd = os.getcwd()

    # Looks for kmz, kml, shp in working folder if not input:
    def find_aoi():
        aoi_list = []
        for file in os.listdir(cwd):
            if file.endswith(".kmz") or file.endswith(".kml") or file.endswith(".shp"):
                aoi_list.append(os.path.abspath(file))
        # Asks for filepath if it can't find AOI
        while aoi_list == []:
            entry = input("Please enter a valid filepath for your AOI: ").strip("\"")
            if os.path.isfile(entry) and entry.endswith(".shp") or entry.endswith(".kmz") or entry.endswith(".kml"):
                aoi_list.append(entry)
        return aoi_list

    parser = argparse.ArgumentParser(description="""Create Files for DJI Flight Planning""")
    parser.add_argument("-i", help=" : KMZ/KML/SHP of target study area")
    parser.add_argument("-o", help=" : Output directory ", default = cwd)
    parser.add_argument("-aoi_b", help=" : AOI buffer size (meters)", default = 10)
    args = parser.parse_args()

    aoi_list = [args.i]
    if aoi_list == [None]:
        aoi_list = find_aoi()

    o_dir = args.o
    dji = os.path.join(o_dir, "DJI_Pilot")
    aoi_buffer = args.aoi_b

    temp = os.path.join(cwd, "lib\\temp")
    for dir in [dji, temp]:
        shutil.rmtree(dir, ignore_errors=True)
        try:
            os.mkdir(dir)
        except FileExistsError:
            print("Please delete ", dir, " Do you have its contents open in ArcGIS?")
            sys.exit()

    for aoi in aoi_list:
        name = os.path.splitext(os.path.basename(aoi))[0].replace(" ", "")
        aoi_type = os.path.splitext(aoi)[1]
        if " " in aoi:
            os.rename(aoi, os.path.join(os.path.dirname(aoi), name + aoi_type))
            aoi = os.path.join(os.path.dirname(aoi), name + aoi_type)

        # Display input parameters
        print("AOI filepath : " , aoi)
        print("Output directories : " , dji)
        print("AOI Buffer Size : " , aoi_buffer)

        #Converts KML/KMZ to Feature Layer for arcpy functions
        if aoi_type != ".shp":
            arcpy.conversion.KMLToLayer(aoi, temp)
            arcpy.env.workspace = os.path.join(temp, name + ".gdb")
            aoi =  arcpy.management.Project(os.path.join(temp, name + ".gdb\Placemarks\Polygons"),
                              os.path.join(temp, name + "_UTM_6N"), arcpy.SpatialReference(6335))

        def buffer_aoi(aoi, aoi_buffer, buffered_aoi):
            dist = str(aoi_buffer) + " Meters"
            buff_aoi_shp = arcpy.analysis.GraphicBuffer(aoi, buffered_aoi, dist, "SQUARE", "MITER", 10)
            print("...Buffered AOI file")
            return buff_aoi_shp

        def aoi_shp_to_kml(shp):
            lyr = arcpy.management.MakeFeatureLayer(shp, os.path.join(temp, name + "_Buffered"))
            arcpy.conversion.LayerToKML(lyr, os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".kml"))

        # Call arcpy functions
        buffered_aoi = os.path.join(temp, name + "_buffered")
        buffered_aoi_shp = buffer_aoi(aoi, aoi_buffer, buffered_aoi)
        aoi_shp_to_kml(buffered_aoi_shp)

        # Creating kml that will make DJI happy
        def add_placemark(file, coords):
            with open("Z:\_Drone_Info\Preflight_Processing\lib\\add_placemark.txt", "r") as ref:
                placemark = ref.read()
            start = placemark.find("<name>") + len("<name>")
            copy = placemark[placemark.find("</name>"):]
            placemark = placemark[:start]+(name)+(copy)
            start = placemark.find("<coordinates>") + len("<coordinates>")
            copy = placemark[placemark.find("</coordinates>"):]
            placemark = placemark[:start]+(coords)+(copy)
            with open(file, "r+") as file:
                text = file.read()
                start = text.find("<Document>") + len("</Document>")
                file.seek(start)
                file.write(placemark)
                file.write("</Document> \n </kml>")

        xml = os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".xml")
        txt = os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".txt")
        os.rename(os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".kml"), xml)
        os.rename(xml, txt)

        with open(txt, "r") as file:
            text = file.read()
            places = text.count("</Placemark>")
            end = 0
            for i in range(places):
                if places > 1:
                    name = name + "_dji" + str(i)
                new_txt = shutil.copy2("Z:\_Drone_Info\Preflight_Processing\lib\dji_kml_format.txt",
                                       os.path.join(dji, name + ".txt"))
                start = text.find("<coordinates>", end) + len("</coordinates")
                end = text.find("</coordinates", start)
                add_placemark(new_txt, text[start:end])

        for i in range(places):
            if places > 1:
                name = name + "_dji" + str(i)
            os.rename(os.path.join(dji, name +".txt"), os.path.join(dji, name +".kml"))
        print("...Created kml for DJI Pilot\n")
        os.remove(txt)