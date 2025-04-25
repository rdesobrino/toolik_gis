# This script is intended to be run once to footprint allllll of the drone imagery collected by ToolikGIS over the years
# with some manual sleuthing and metadata updating expected based on the various ways data are stored

import os
import arcpy
from datetime import datetime

x7s = {}
multis = {}

def prowl(wd_path):
    for fname in os.listdir(wd_path):
        fname = fname.upper()
        f = os.path.join(wd_path, fname)

        if os.path.isfile(f) and fname.endswith('.TIF'):
            f = f.replace('/', '\\').upper()

            rasterInfo = arcpy.Raster(f).getRasterInfo()
            bands = rasterInfo.getBandCount()
            cs = rasterInfo.getSpatialReference().name not in ["Unknown", "unnamed"]

            if ((3 <= bands <= 4 and "NDVI" not in f and "NIR" not in f) or "RGB" in f) and cs and not ("DEM" in f or "DSM" in f): ## there are some four band RGBs?? and 3band multispec/ndvi
                x7s[fname]=[f,bands]
            elif cs and not ("DEM" in f or "DSM" in f): ## catch anything passed over above  ## TODO does this need to look for keywords too? TODO: do I want one band NDVI
                multis[fname]=[f,bands]

        # continue searching relevant directories only
        elif os.path.isdir(f) and fname.split("_")[-1] not in "KlAUPPK_PLANNING_IMAGERY_NDVI_IMAGES_PHOTOS_METASHAPE_PLANNING_METADATA_ARCGIS_PRO_ANALYST_NOTES_DOCS_ARCMAP" and not fname.endswith(".FILES") and "PLANNING_FILES" not in fname:
            prowl(wd_path+"/" + fname)

search = ['Z:\Toolik\Project_UAS', r'Z:\2024_Work\UAS_Processing', r'Z:\2023_Work\UAS_Processing', r"Z:\2022_Work\UAS_Flight_Processing", r'Z:\2021_Work\_UAS_Processing', 'Z:\Toolik\Project_UAS']
for folder in search:
    print("Searching " + folder)
    prowl(folder)

gdb = r"C:\Users\rcdesobrino\Desktop\repos\toolik_gis\qaqc\ArcGIS\qaqc_testing.gdb"
x7 = os.path.join(gdb, "x7_fp_" + datetime.today().strftime('%Y%m%d'))
ms = os.path.join(gdb, "micasense_fp_" + datetime.today().strftime('%Y%m%d'))

try:   ### I think the only benefit of this is printing the error message. delete??? but the error message is useful
    print("Creating Mosaic Datasets...")
    arcpy.management.CreateMosaicDataset(
        in_workspace=gdb,
        in_mosaicdataset_name="x7_fp_" + datetime.today().strftime('%Y%m%d'),
        coordinate_system='PROJCS["NAD_1983_2011_UTM_Zone_6N",GEOGCS["GCS_NAD_1983_2011",DATUM["D_NAD_1983_2011",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-147.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]],VERTCS["NAVD_1988",VDATUM["North_American_Vertical_Datum_1988"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]',
        num_bands=3,
        product_definition="NATURAL_COLOR_RGB",
        product_band_definitions="Red 630 690;Green 530 570;Blue 440 510"
    )
    arcpy.management.CreateMosaicDataset(
        in_workspace=gdb,
        in_mosaicdataset_name="micasense_fp_" + datetime.today().strftime('%Y%m%d'),
        coordinate_system='PROJCS["NAD_1983_2011_UTM_Zone_6N",GEOGCS["GCS_NAD_1983_2011",DATUM["D_NAD_1983_2011",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-147.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]],VERTCS["NAVD_1988",VDATUM["North_American_Vertical_Datum_1988"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]',
    )

    datasets = {x7: x7s, ms: multis}
    for dataset in datasets:
        d_list = list(datasets[dataset].values())
        print("Adding rasters to " + dataset)
        arcpy.management.AddRastersToMosaicDataset(
            in_mosaic_dataset=dataset,
            raster_type="Raster Dataset",
            input_path=[pair[0] for pair in d_list],
            update_boundary="UPDATE_BOUNDARY",
            calculate_statistics="CALCULATE_STATISTICS",
            maximum_pyramid_levels=None,
            spatial_reference='PROJCS["NAD_1983_2011_UTM_Zone_6N",GEOGCS["GCS_NAD_1983_2011",DATUM["D_NAD_1983_2011",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-147.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]],VERTCS["NAVD_1988",VDATUM["North_American_Vertical_Datum_1988"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision',
            build_thumbnails="BUILD_THUMBNAILS",
            build_pyramids="BUILD_PYRAMIDS")

        print("Calculating Fields...")
        arcpy.management.CalculateField(
            in_table=dataset,
            field="Date",
            expression='six(!Name!)',
            expression_type="PYTHON3",
            code_block="""def six(name):
            return name[-6:] """
        )
        arcpy.management.CalculateField(
            in_table=dataset,
            field="Year",
            expression='four(!Name!)',
            expression_type="PYTHON3",
            code_block="""def four(name):
                year = "20" + name[-6:-4]
                return year """
        )
        arcpy.management.CalculateField(
            in_table=dataset,
            field="Filepath",
            expression="""get(!Name!, datasets[dataset])""",
            expression_type="PYTHON3",
            code_block="""def get(name, dict):
            return dict[name.upper()+'.TIF'][0] """
        )
        arcpy.management.CalculateField(
            in_table=dataset,
            field="Bands",
            expression="""get(!Name!, datasets[dataset])""",
            expression_type="PYTHON3",
            code_block="""def get(name, dict):
            return dict[name.upper()+'.TIF'][1] """ ## for some yet-unknown reason some lowercase names still got in
        )
        arcpy.management.DeleteField(## TODO make non-deletable awful fields not visible
            in_table=dataset,
            drop_field="Tag;GroupName;ProductName",
            method="DELETE_FIELDS"
        )
    print("Building Footprints...")  ## unfortunately this does NOT work for micasense
    arcpy.management.BuildFootprints(
        in_mosaic_dataset=x7,
        where_clause="",
        reset_footprint="RADIOMETRY",
        min_data_value=1,
        max_data_value=254,
        update_boundary="UPDATE_BOUNDARY",)

except arcpy.ExecuteError:
    print("Something caused an ArcGIS tool to fail")
    print(arcpy.GetAllMessages())




