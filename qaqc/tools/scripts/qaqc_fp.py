## This script is part of an ArcGIS toolbox for performing routine QA/QC steps in the ToolikGIS drone processing SOP
## Required parameters include input DEM (expects NAVD88), input DEM in WGS84, and at least for now, the path to the UAS footprint. Calculations with publcily available NEON and PGC DEMs are done automatically.
## Rd 250113

import os
import arcpy
from datetime import datetime

aprx = arcpy.mp.ArcGISProject("CURRENT")
gdb = aprx.defaultGeodatabase
map = aprx.listMaps('Map')[0]

start = datetime.today().strftime('%y%m%d')+"_"+str(datetime.now().strftime('%H%M'))
input = arcpy.GetParameterAsText(0)
wgs = ";".join([arcpy.GetParameterAsText(1), "Z:\Toolik\Toolik1\hypsographic\PGC_Arctic_DEM\ArcticDEM.vrt pgc"])
neon = ""
fp = arcpy.GetParameterAsText(2)
yr = arcpy.GetParameterAsText(3)

name = os.path.basename(input).split(".")[0]
arcpy.AddMessage(name)

neon_extent = arcpy.ddd.RasterDomain(
    in_raster="Z:\Toolik\Toolik1\hypsographic\\NEON_DSM_Mosaic_2019.TIF", out_feature_class=os.path.join(gdb, "NEON_Extent"),out_geometry_type="POLYGON")

extent = arcpy.ddd.RasterDomain(
    in_raster=input,
    out_feature_class=os.path.join(gdb, "InputDEM_Extent"),
    out_geometry_type="POLYGON")

arcpy.management.MakeFeatureLayer(extent, "InputDEM_Extent_lyr")
arcpy.management.MakeFeatureLayer(neon_extent, "NEON_Extent_lyr")

arcpy.management.SelectLayerByLocation("InputDEM_Extent_lyr", 'INTERSECT', "NEON_Extent_lyr")
if int(arcpy.management.GetCount("InputDEM_Extent_lyr")[0]) != 0:
    arcpy.AddMessage("DEM intersects with NEON extent")
    neon = "Z:\Toolik\Toolik1\hypsographic\\NEON_DSM_Mosaic_2019.TIF neon"

dems = ";".join([input,neon])
arcpy.AddMessage("WGS84 DEMS: " + wgs)
arcpy.AddMessage("NAVD88 DEMS: " + dems)

points_name = name + "_" + start
points = arcpy.management.CreateSpatialSamplingLocations(
in_study_area=extent,
out_features=os.path.join(gdb, points_name),
sampling_method="RANDOM",
min_distance="2 Meters",
num_samples=1000)

map.addDataFromPath(os.path.join(gdb, points_name))
map.addDataFromPath(fp)

arcpy.management.CreateFeatureclass(
    out_path=gdb,
    out_name="DEMs",)
arcpy.AddMessage(os.path.basename(fp)+"\Footprint")
selection = arcpy.management.SelectLayerByLocation(
    in_layer=os.path.basename(fp)+"\Footprint",
    overlap_type="INTERSECT",
    select_features=points_name)
arcpy.management.CopyFeatures(selection, "DEMs")

fp = []
with arcpy.da.SearchCursor("DEMs", ['Filepath', 'Year']) as cursor:
    for row in cursor:
        try:
            # arcpy.AddMessage(os.path.dirname(row[0]))
            # arcpy.AddMessage(row[1] + " " + yr)
            if yr == "" or int(row[1]) >= int(yr):
                fp.append(os.path.dirname(row[0]))
        except ValueError:
            arcpy.AddMessage("The file " + os.path.dirname(row[0]) + " was not used because it doesn't follow current naming conventions.")

arcpy.AddMessage(input)
for dir in fp:
    for file in os.listdir(dir):
        if "DEM" in file and file.endswith(".tif") and file.upper() != os.path.basename(input).upper() and file not in dems:
            dems = ";".join([dems, os.path.join(dir, file)])

arcpy.AddMessage(dems)

try:
    for cs in [wgs, dems]:
        arcpy.sa.ExtractMultiValuesToPoints(
        in_point_features=points,
        in_rasters=cs,
        bilinear_interpolate_values="NONE")

    ## Calculate difference for NAVD88 DEMs
    calc = {}                              ## {field name for subtraction: dem1 field.name, dem2 field.name}
    fields = arcpy.ListFields(points)

    for i in range(6, len(fields)):        # skip OBJECTID, SHAPE, CID, wgs84 dem, pgc, self
        field_name = "_" + input[-11:-4] + "_" + fields[i].name[-6:]
        rep = 0  # for tracking files from the same date
        for field_names in calc:
            if field_name in calc:
                rep += 1
        if rep != 0:
            field_name += str(rep)

        arcpy.management.AddField(
        in_table=points,
        field_name=field_name,
        field_type="FLOAT")
        calc[field_name]=[fields[5].name, fields[i].name]

    fields = arcpy.ListFields(points)
    for field in fields:
        if field.name in calc.keys():
            arcpy.management.CalculateField(
            in_table=points,
            field=field.name,
            expression="!"+str(calc[field.name][0])+"!-!"+str(calc[field.name][1])+"!")
            arcpy.AddMessage("Calculating "+field.name + ": !"+str(calc[field.name][0])+"!-!"+str(calc[field.name][1])+"!")

    ## Handle wgs84 DEMs last
    fields = arcpy.ListFields(points)
    arcpy.management.AddField(
            in_table=points,
            field_name="_" + input[-11:-4] + "_" + "pgc",
            field_type="FLOAT")
    arcpy.management.CalculateField(
            in_table=points,
            field="_" + input[-11:-4] + "_" + "pgc",
            expression="!"+fields[3].name+"!-!"+fields[4].name+"!")
    arcpy.AddMessage("Calculating _" + input[-11:-4] + "_" + "pgc: " + "!" + "!"+fields[3].name+"!-!"+fields[4].name+"!")

except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
    arcpy.AddError("Please remove the output files from your map and delete them from the geodatabase and then try again")