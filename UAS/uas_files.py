'''
This script is to be executed from an ArcGIS Python Shell to generate the required files used in Drone Harmony UAS Planning by Toolik GIS
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

    # Looks for kmz, kml, shp in working folder:
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
    parser.add_argument("-o", help=" : Output directory ", default = os.path.join(cwd, "Outputs"))
    parser.add_argument("-aoi_b", help=" : AOI buffer size (meters)", default = 50)
    parser.add_argument("-d", help=" : dem file", default = "Z:\Toolik\Toolik1\hypsographic\PGC_Arctic_DEM\Mosaic\ArcticDEM_mosaic.vrt")
    parser.add_argument("-dem_b", help=" : DEM buffer size (meters)", default = 50)
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
    dem = args.d
    aoi_buffer = args.aoi_b
    d_buffer = args.dem_b
    res = args.rs
    f_type = args.f

    # Display input parameters
    print("AOI filepath : " , aoi)
    print("Output directory : " , o_dir)
    print("Output format: ", f_type)
    print("AOI Buffer Size : " , aoi_buffer)
    print("DEM : " , dem)
    print("DEM Buffer Size : " , d_buffer)
    print("Resampling: ", res)
    print("\n")

    # Cleans up output folder for current run
    shutil.rmtree(o_dir, ignore_errors=True)
    os.mkdir(o_dir)

    #Cleans up temp folder for current run
    temp = os.path.join(cwd, "temp")
    shutil.rmtree(temp, ignore_errors=True)
    try:
        os.mkdir(temp)
    except FileExistsError:
        print("Please delete the temp folder. Do you have its contents open in ArcGIS?")
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
    #buff_aoi_shp = arcpy.analysis.PairwiseBuffer(aoi, buffered_aoi, dist)
    buff_aoi_shp = arcpy.analysis.GraphicBuffer(aoi, buffered_aoi, dist, "SQUARE", "MITER", 10)
    print("...Buffered AOI file")
    return buff_aoi_shp


# Clip Raster doesn't always like it if the feature class and dem are in different projections but reprojecting the full dem file takes a long time
def check_projections(aoi, dem):
    aoi_sr = arcpy.Describe(aoi).spatialReference.factoryCode
    dem_sr = arcpy.Describe(dem).spatialReference.factoryCode
    if dem_sr != aoi_sr:
        aoi = arcpy.management.Project(aoi, os.path.join(temp, name + "_" + str(dem_sr)), dem_sr)
    return aoi

def clip_dem(shp, dem):
    shp = check_projections(shp, dem)
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
    dem_o = arcpy.management.ProjectRaster(dem, os.path.join(o_dir, d_name + "_" + str(d_buffer) + "m_buffered.tif"), sr)
    print("...Reprojected DEM to WGS84: 4326")
    if f_type == "ascii":
        arcpy.conversion.RasterToASCII(dem_o, os.path.join(o_dir, d_name + "_" + str(d_buffer) + "m_buffered.asc"))
        print("...Converted DEM to ASCII")
    return dem_o

def aoi_shp_to_kml(shp):
    #shp = arcpy.management.MinimumBoundingGeometry(shp, os.path.join(temp, name + "_MinArea"), "RECTANGLE_BY_AREA")
    lyr = arcpy.management.MakeFeatureLayer(shp, os.path.join(temp, name + "_Buffered"))
    arcpy.conversion.LayerToKML(lyr, os.path.join(o_dir, name + "_" + str(aoi_buffer) + "m" + ".kml"))
    print("...Created .kml from shapefile")

# Call functions
buffered_aoi = os.path.join(temp, name + "_buffered")
buffered_aoi_shp = buffer_aoi(aoi, aoi_buffer, buffered_aoi)

aoi_shp_to_kml(buffered_aoi_shp)

buffered_aoi_for_dem = os.path.join(temp, name + "_for_DEM")
buffered_aoi_shp = buffer_aoi(buffered_aoi_shp, aoi_buffer, buffered_aoi_for_dem)

project_dem(buffered_aoi_shp, dem)

shutil.rmtree(temp, ignore_errors=True)