import os
import cv2
import numpy as np
import arcpy
import arcpy.ia
from arcpy.ia import *

def generate_tiles(output_folder, input_file):
    if len(os.listdir(output_folder)) == 0:
        arcpy.management.SplitRaster(input_file, output_folder, "t", "SIZE_OF_TILE",
                                     "PNG", "NEAREST", "1 1", "128 128", 0, "PIXELS",
                                     None, None, None, "FEATURE_CLASS", "DEFAULT", "")
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if not file.endswith('.PNG'):
                    os.remove(os.path.join(root, file))

def clean_folders(org_folder, gen_folder):
    list_dir = os.listdir(org_folder)
    for item in list_dir:
        path_org = rf"{org_folder}\{item}"
        path_gen = rf"{gen_folder}\{item}"
        if os.path.isfile(path_org):
            img = cv2.imread(path_org)
            img_no_border = img[1:-1,1:-1,:3]
            if img.shape[:2] != (128, 128):
                os.remove(path_org)
                os.remove(path_gen)
            elif np.all(img_no_border == 255):
                os.remove(path_org)
                os.remove(path_gen)

arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = True

# Paths (to be changed)
project_path = r"C:\Users\Orio\Documents\ArcGIS\Projects\Generalization_Project"
gdb_path = rf"{project_path}\Generalization_Project.gdb"
data_path = rf"{project_path}\Data"
arcpy.env.workspace = data_path
aprx = arcpy.mp.ArcGISProject(rf"{project_path}\Generalization_Project.aprx")

aprxMap = aprx.listMaps()[0]
prj_file = rf"{data_path}\custom_map_projection.prj"
aprxMap.spatialReference = arcpy.SpatialReference(prj_file)

# Avoiding duplicated layers
for lr in aprxMap.listLayers():
    aprxMap.removeLayer(lr)

aprxMap.addBasemap("Light Gray Canvas")

# Import data
print("Importing data...")
build_in = arcpy.conversion.FeatureClassToFeatureClass("buildings.shp", gdb_path, "buildings")
street_in = arcpy.conversion.FeatureClassToFeatureClass("streets.shp", gdb_path, "streets")

aprxMap.addDataFromPath(build_in)
aprxMap.addDataFromPath(street_in)

# Generalize
print("Simplifying layers...")
build_gen = arcpy.cartography.SimplifyBuilding(build_in, rf"{gdb_path}\buildings_simpl_15m", "15 Meters")
street_gen = arcpy.cartography.SimplifyLine(rf"{gdb_path}\streets", rf"{gdb_path}\streets_simpl",
                                            "BEND_SIMPLIFY", "15 Meters")
aprxMap.addDataFromPath(build_gen)
aprxMap.addDataFromPath(street_gen)

# Creating raster binary maps for both datasets
print("Rasterizing original dataset...")
build_in_ras = arcpy.conversion.PolygonToRaster(build_in, "OBJECTID", rf"{gdb_path}\build_in_ras",
                                                "CELL_CENTER", "Shape_Area", 1E-05)
street_in_ras = arcpy.conversion.PolylineToRaster(street_in, "OBJECTID", rf"{gdb_path}\street_in_ras",
                                                  "MAXIMUM_LENGTH", "NONE", 1E-05, "BUILD")

print("Rasterizing generalized dataset...")
build_gen_ras = arcpy.conversion.PolygonToRaster(build_gen, "OBJECTID", rf"{gdb_path}\build_gen_ras",
                                                 "CELL_CENTER", "Shape_Area", 1E-05)
street_gen_ras = arcpy.conversion.PolylineToRaster(street_gen, "OBJECTID", rf"{gdb_path}\street_gen_ras",
                                                  "MAXIMUM_LENGTH", "NONE", 1E-05, "BUILD")

# Mosaics from buildings and streets datasets
comb_org = arcpy.management.MosaicToNewRaster([build_in_ras, street_in_ras], data_path,
                                      "combined_original.tif", '', "8_BIT_UNSIGNED", None, 1, "LAST", "FIRST")
comb_gen = arcpy.management.MosaicToNewRaster([build_gen_ras, street_gen_ras], data_path,
                                      "combined_generalized.tif", '', "8_BIT_UNSIGNED", None, 1, "LAST", "FIRST")

# Symbology
print("Creating binary maps...")
binary_colormap = [[1, 0, 0, 0], [2, 255, 255, 255]]

# Features
con1 = arcpy.sa.Con(build_in_ras, 1, build_in_ras, "Value > 1")
con2 = arcpy.sa.Con(build_gen_ras, 1, build_gen_ras, "Value > 1")
con3 = arcpy.sa.Con(comb_org, 1, comb_org, "Value > 0")
con4 = arcpy.sa.Con(comb_gen, 1, comb_gen, "Value > 0")

# Background
bgd1 = arcpy.sa.Con(arcpy.sa.IsNull(con1), 2, con1, "Value = 1")
bgd2 = arcpy.sa.Con(arcpy.sa.IsNull(con2), 2, con2, "Value = 1")
bgd3 = arcpy.sa.Con(con3, 2, con3, "Value = 0")
bgd4 = arcpy.sa.Con(con4, 2, con4, "Value = 0")

map1 = Colormap(bgd1, colormap = binary_colormap)
map2 = Colormap(bgd2, colormap = binary_colormap)
map3 = Colormap(bgd3, colormap = binary_colormap)
map4 = Colormap(bgd4, colormap = binary_colormap)

map1.save(rf"{gdb_path}\original_binary")
map2.save(rf"{gdb_path}\generalized_binary")
#map3.save(rf"{gdb_path}\combined_original")
#map4.save(rf"{gdb_path}\combined_generalized")

clip1 = arcpy.management.Clip(map3, build_in, rf"{gdb_path}\comb_org_clip", "", "255", "", "MAINTAIN_EXTENT")
clip2 = arcpy.management.Clip(map4, build_in, rf"{gdb_path}\comb_gen_clip", "", "255", "", "MAINTAIN_EXTENT")

prj1 = arcpy.management.ProjectRaster(map1, rf"{gdb_path}\org_bin_prj", prj_file)
prj2 = arcpy.management.ProjectRaster(map2, rf"{gdb_path}\gen_bin_prj", prj_file)
prj3 = arcpy.management.ProjectRaster(clip1, rf"{gdb_path}\comb_org_prj", prj_file)
prj4 = arcpy.management.ProjectRaster(clip2, rf"{gdb_path}\comb_gen_prj", prj_file)

new_0 = rf"{data_path}\tiff_files"
if not os.path.exists(new_0):
    os.makedirs(new_0)

if len(os.listdir(new_0)) == 0:
    arcpy.conversion.RasterToOtherFormat([prj1, prj2, prj3, prj4], rf"{data_path}\tiff_files", 'TIFF')

aprxMap.addDataFromPath(rf"{data_path}\tiff_files\org_bin_prj.tif")
aprxMap.addDataFromPath(rf"{data_path}\tiff_files\gen_bin_prj.tif")
aprxMap.addDataFromPath(rf"{data_path}\tiff_files\comb_org_prj.tif")
aprxMap.addDataFromPath(rf"{data_path}\tiff_files\comb_gen_prj.tif")

# Create tiles
print("Creating training tiles...")
folder_names = ['original_tiles', 'generalized_tiles', 'original_combined_tiles', 'generalized_combined_tiles']

for name in folder_names:
    new = rf"{data_path}\{name}"
    if not os.path.exists(new):
        os.makedirs(new)

generate_tiles(data_path + rf"\{folder_names[0]}", data_path + r"\tiff_files\org_bin_prj.tif")
generate_tiles(data_path + rf"\{folder_names[1]}", data_path + r"\tiff_files\gen_bin_prj.tif")
generate_tiles(data_path + rf"\{folder_names[2]}", data_path + r"\tiff_files\comb_org_prj.tif")
generate_tiles(data_path + rf"\{folder_names[3]}", data_path + r"\tiff_files\comb_gen_prj.tif")

# Process image datasets
clean_folders(data_path + r"\original_tiles", data_path + r"\generalized_tiles")
clean_folders(data_path + r"\original_combined_tiles", data_path + r"\generalized_combined_tiles")


arcpy.management.ClearWorkspaceCache()
aprx.save()
