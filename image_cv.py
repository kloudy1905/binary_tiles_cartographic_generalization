import cv2
import os
import numpy as np

project_path = r"C:\Users\Orio\Documents\ArcGIS\Projects\Generalization_Project"
data_path = rf"{project_path}\Data1"

# Shape-based file cleaning
folder_names = ['original_tiles',
                'generalized_tiles',
                'original_combined_tiles',
                'generalized_combined_tiles']

# for name in folder_names:
#     path = rf"{data_path}\{name}"
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             img = cv2.imread(file_path)
#             if img.shape[:2] != (100, 100):
#                 os.remove(file_path)
#             else:
#                 rows, cols, _ = img.shape
#                 for i in range(rows):
#                     for j in range(cols):
#                         k = img[i, j]

# def is_white(file_path):
    # img = cv2.imread(file_path)
    # if np.any(img != 255):
    #     return False
    # # rows, cols, _ = img.shape
    # # for i in range(rows):
    # #     for j in range(cols):
    # #         pix = img[i, j]
    # #         if 0 in pix:
    # return True

def clean_folders(org_folder, gen_folder):
    # files_del = []
    # for root, dirs, files in os.walk(org_folder):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         img = cv2.imread(file_path)
    #         if img.shape[:2] != (100, 100):
    #             os.remove(file_path)
    #         else:
    #             files_del.append(file_path)

    # for root, dirs, files in os.walk(org_folder):
    #     for dir in dirs:
    #         print(dir)
    #     for file in files:
    #         print(file)

    list = os.listdir(org_folder)
    for file in list:
        full_name = rf"{org_folder}\{file}"
        if os.path.isfile(full_name):
            img = cv2.imread(full_name)
            if img.shape[:2] != (100, 100):
                #print(rf"{full_name} is not 100x100")
                os.remove(full_name)
                # os.remove(rf"{gen_folder}\{file}")
            elif np.all(img == 255):
                #print(rf"{full_name} is white")
                os.remove(full_name)
                # os.remove(rf"{gen_folder}\{file}")


clean_folders(data_path + '\original_tiles', data_path + '\generalized_tiles')















