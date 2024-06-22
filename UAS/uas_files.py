'''
This script is to be executed from an ArcGIS Python Shell to generate the required files used in Drone Harmony and DJI Pilot UAS Planning by Toolik GIS
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
        aoi = False
        for file in os.listdir(cwd):
            if file.endswith(".kmz") or file.endswith(".kml") or file.endswith(".shp"):
                aoi = os.path.abspath(file)
        # Asks for filepath if it can't find AOI
        while aoi == False:
            entry = input("Please enter a valid filepath for your AOI: ").strip("\"")
            if os.path.isfile(entry) and entry.endswith(".shp") or entry.endswith(".kmz") or entry.endswith(".kml"):
                aoi = entry
        return aoi

    parser = argparse.ArgumentParser(description="""Create Files for Drone Harmony PreFlight Planning""")
    parser.add_argument("-i", help=" : KMZ/KML/SHP of target study area")
    parser.add_argument("-o", help=" : Output directory ", default = cwd)
    parser.add_argument("-aoi_b", help=" : AOI buffer size (meters)", default = 10)
    parser.add_argument("-d", help=" : dem file", default = "Z:\Toolik\Toolik1\hypsographic\PGC_Arctic_DEM\Mosaic\ArcticDEM_mosaic.vrt")
    parser.add_argument("-dem_b", help=" : DEM buffer size (meters)", default = 10)
    parser.add_argument("-rs", help=" : resolution in meters to resample DEM", default = 0)
    parser.add_argument("-f", help=" : output format: ascii or gtif", default="gtif")
    args = parser.parse_args()

    aoi = args.i
    if aoi == None:
        aoi = find_aoi()
    name = os.path.splitext(os.path.basename(aoi))[0].replace(" ", "")
    aoi_type = os.path.splitext(aoi)[1]
    if " " in aoi:
        os.rename(aoi, os.path.join(os.path.dirname(aoi), name + aoi_type))
        aoi = os.path.join(os.path.dirname(aoi), name + aoi_type)

    o_dir = args.o
    dh = os.path.join(o_dir, "Drone_Harmony")
    dji = os.path.join(o_dir, "DJI_Pilot")
    dem = args.d
    aoi_buffer = args.aoi_b
    d_buffer = args.dem_b
    res = args.rs
    f_type = args.f

    # Display input parameters
    print("AOI filepath : " , aoi)
    print("Output directories : " , dh, "; ", dji)
    print("Output format: ", f_type)
    print("AOI Buffer Size : " , aoi_buffer)
    print("DEM : " , dem)
    print("DEM Buffer Size : " , d_buffer)
    print("Resampling: ", res)
    print("\n")

    # Cleans up output and temp folders for current run
    temp = os.path.join(cwd, "temp")
    for dir in [dh, dji, temp]:
        shutil.rmtree(dir, ignore_errors=True)
        try:
            os.mkdir(dir)
        except FileExistsError:
            print("Please delete ", dir, " Do you have its contents open in ArcGIS?")
            sys.exit()

    gdb = os.path.join(temp, name + ".gdb")
    d_name = os.path.splitext(os.path.basename(dem))[0]

#Converts KML/KMZ to Feature Layer for arcpy functions
if aoi_type != ".shp":
    arcpy.conversion.KMLToLayer(aoi, temp)
    arcpy.env.workspace = gdb
    for fc in arcpy.ListFeatureClasses('*', '', 'Placemarks'):
        aoi = fc

def buffer_aoi(aoi, aoi_buffer, buffered_aoi):
    dist = str(aoi_buffer) + " Meters"
    buff_aoi_shp = arcpy.analysis.GraphicBuffer(aoi, buffered_aoi, dist, "SQUARE", "MITER", 10)
    print("...Buffered AOI file")
    return buff_aoi_shp

def clip_dem(shp, dem):
    d_sr = arcpy.Describe(dem).spatialReference.factoryCode
    shp = arcpy.management.Project(shp, os.path.join(temp, name + "_" + str(d_sr)), d_sr)
    clipped_dem = arcpy.Clip_management(dem, "0 0 0 0", os.path.join(temp, d_name + "_clip.tif"), shp, "-999", "ClippingGeometry")
    print("...Clipped DEM to AOI")
    clipped_dem = resample_dem(clipped_dem, res)
    return clipped_dem

def resample_dem(dem, res):
    if arcpy.Describe(dem).spatialReference.linearUnitName == "Meter" and arcpy.Raster(dem).meanCellHeight < float(res) and arcpy.Raster(dem).meanCellWidth < float(res):
        dem = arcpy.Resample_management(dem, os.path.join(temp, d_name[:7] + "_" + str(res)), str(res), "NEAREST")
        print("...Resampled DEM to", res, "m resolution")
    return dem
def project_dem(aoi, dem):
    dem = clip_dem(aoi, dem)
    sr = arcpy.SpatialReference(4326)
    dem_o = arcpy.management.ProjectRaster(dem, os.path.join(dh, d_name + "_" + str(d_buffer) + "m_buffered.tif"), sr)
    print("...Reprojected DEM to WGS84: 4326")
    if f_type == "ascii":
        arcpy.conversion.RasterToASCII(dem_o, os.path.join(dh, d_name + "_" + str(d_buffer) + "m_buffered.asc"))
        print("...Converted DEM to ASCII")
    return dem_o

def aoi_shp_to_kml(shp):
    lyr = arcpy.management.MakeFeatureLayer(shp, os.path.join(temp, name + "_Buffered"))
    arcpy.conversion.LayerToKML(lyr, os.path.join(dh, name + "_" + str(aoi_buffer) + "m" + ".kml"))
    arcpy.conversion.LayerToKML(lyr, os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".kml"))
    print("...Created .kml for Drone Harmony")

# Call arcpy functions
aoi = arcpy.management.Project(aoi, os.path.join(temp, name + "_UTM_6N"), arcpy.SpatialReference(6335))
buffered_aoi = os.path.join(temp, name + "_buffered")
buffered_aoi_shp = buffer_aoi(aoi, aoi_buffer, buffered_aoi)

aoi_shp_to_kml(buffered_aoi_shp)

buffered_aoi_for_dem = os.path.join(temp, name + "_for_DEM")
buffered_aoi_shp = buffer_aoi(buffered_aoi_shp, aoi_buffer, buffered_aoi_for_dem)

project_dem(buffered_aoi_shp, dem)

# Creating kml that will make DJI happy
xml = os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".xml")
txt = os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".txt")
os.rename(os.path.join(dji, name + "_" + str(aoi_buffer) + "m" + ".kml"), xml)
os.rename(xml, txt)
with open(txt, "r") as file:
    text = file.read()
    start = text.find("<coordinates>") + len("</coordinates")
    end = text.find("</coordinates")
    coords = (text[start:end])

ref_kml = shutil.copy2("Z:\_Drone_Info\Preflight_Processing\sample_dji.kml", os.path.join(dji, name + "_dji.kml"))
ref_xml = os.path.join(dji, name + "_dji.xml")
ref_txt = os.path.join(dji, name + "_dji.txt")
os.rename(ref_kml, ref_xml)
os.rename(ref_xml, ref_txt)

with open(ref_txt, "r+") as file:
    text = file.read()
    start = text.find("<coordinates>") + len("</coordinates")
    end = text.find("</coordinates")
    copy = text[end:]
    file.seek(start)
    file.write(coords)
    file.write(copy)

os.rename(ref_txt, ref_kml)
print("...Created kml for DJI Pilot")
os.remove(txt)