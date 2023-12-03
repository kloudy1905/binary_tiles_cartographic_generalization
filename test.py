import os
import arcpy
from arcpy.ia import *
import cv2
import numpy as np

project_path = r"C:\Users\Orio\Documents\ArcGIS\Projects\Generalization_Project"
gdb_path = rf"{project_path}\Generalization_Project.gdb"

prj1 = arcpy.management.ProjectRaster(map1, rf"{gdb_path}\org_bin_prj", prj_file)
