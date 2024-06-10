PreflightFiles.py

Rachel de Sobrino
TFS GIS May 2024

This script creates an output kml and clipped projected DEM for use in Drone Harmony software. It requires a .kml, .kmz, or .shp input file as the AOI.
There are no required input parameters in order to make it click and run.

To run:

1. Right-click the script, click Open With, and navigate to the Python environment provided by ArcGIS Pro. e.g. "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe". You can select Always if you primarily want to run scripts in the ArcGIS Pro environment to make this a click-and-go. A terminal window will pop up and close upon completion.
-- Requires a .kml, .kmz, or .shp input file, either in the same folder as the script or paste the filepath when prompted in the terminal.

OR

2. Open a Python terminal using the ArcGIS Pro environment (in Start search Python and verify the filepath contains "\ArcGIS"). Type python, the path to the script, and any desired input parameters. Use -h or --help for options.
-- all input parameters are optional. If you place the input AOI file in the same location as the script it will detect it.
-i: path to input AOI as .shp/.kml/.kmz
-o: output directory
-aoi_b: size in meters to buffer the AOI (this is to ensure result of drone flight includes full AOI after processing). The default is 10m
-d: path to DEM file. Default is PGC's ArcticDEM at 2m resolution: "Z:\Toolik\Toolik1\hypsographic\PGC_Arctic_DEM\Mosaic\ArcticDEM_mosaic.vrt"
-dem_b: size in meters to buffer the DEM around the AOI. The default is 10m.
-rs: resolution in meters to resample the DEM to.
-f: desired file format. options are GeoTiff(gtif) and ASCII (ascii). Geotiff is the default. 

Pay attention to the terminal. If you don't provide an AOI or the script doesn't find an AOI in its folder it will ask you for a filepath. Error handling is printed to the terminal.

The output files (a .kml of the flight AOI, buffered by 10m) and a DEM (clipped to the AOI + another 10m, in 4326 WGS 84) will be exported to an \Outputs folder, or wherever you specified. Please delete the temp folder after the script completes (lock files are maintained on .gdbs so it can't be deleted from within the script)