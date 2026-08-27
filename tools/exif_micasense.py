## Script to generate text files of all image paths in Micasense folder (corresponding to Emlid Reach events file)
## then to generate exif metadata of all images
## output a textfile with image names and exact times

import argparse
import os
import exiftool

if  __name__ == "__main__":

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description="""Generate exif metadata for all Micasense photos""")
    parser.add_argument("-i", help=" : path to 3_Photos/Micasense folder ")
    args = parser.parse_args()

    mica_path = args.i

    for dir in os.listdir(mica_path):
        if os.path.isdir(os.path.join(mica_path, dir)):
            img_list = []
            for img_folder in os.listdir(os.path.join(mica_path, dir)):
                if os.path.isdir(os.path.join(mica_path, dir, img_folder)):
                    for img in sorted(os.listdir(os.path.join(mica_path, dir, img_folder))):
                        if img[-5:] == "1.tif":\
                            img_list.append(os.path.join(mica_path, dir, img_folder,img))
            img_data = ""
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(img_list)
                for dict in metadata:
                    # print(dict["File:FileName"])
                    # print(dict["EXIF:DateTimeOriginal"])
                    img_name = dict["File:FileName"]
                    date_time = dict["EXIF:DateTimeOriginal"]
                    img_data += (img_name + "," + date_time + "\n")
            print(img_data)
            with open(os.path.join(mica_path, (dir + ".txt")), "a") as txt:
                txt.write(img_data)
