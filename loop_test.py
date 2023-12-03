import os
import shutil
import arcpy

project_path = r"C:\Users\Orio\Documents\ArcGIS\Projects\Generalization_Project"
data_path = rf"{project_path}\Data1"

split_names = ['split_org','split_gen','split_org_comb','split_gen_comb']
folder_names = ['original_tiles','generalized_tiles','original_combined_tiles','generalized_combined_tiles']
tile_names = ['org_bin_prj.tif','gen_bin_prj.tif','comb_org_prj.tif','comb_gen_prj.tif']
img_names = ['org','gen','comb_org','comb_gen']

for split in split_names:
    for folder in folder_names:
        for tile in tile_names:
            for img in img_names:
                new_1 = rf"{data_path}\{split}"
                if not os.path.exists(new_1):
                    os.makedirs(new_1)

                new_2 = rf"{data_path}\{folder}"
                if not os.path.exists(new_2):
                    os.makedirs(new_2)

                if len(os.listdir(new_1)) == 0:
                    arcpy.management.SplitRaster(rf"{data_path}\tiff_files\{tile}", new_1, img,
                                             "SIZE_OF_TILE", "PNG", "NEAREST", "1 1", "100 100", 0, "PIXELS",
                                             None, None, None, "FEATURE_CLASS", "DEFAULT", "")

                if len(os.listdir(new_2)) == 0:
                    files_png = []
                    for root, dirs, files in os.walk(new_1):
                        for file in files:
                            if file.endswith('.PNG'):
                                files_png.append(os.path.join(root, file))

                    for file in files_png:
                        shutil.move(file, new_2)