## adapted from Micasense docs: https://support.micasense.com/hc/en-us/articles/360054297594-How-to-integrate-Emlid-Reach-RTK-with-MicaSense-Sensors
##
## developed for integration Emlid Reach M2 with Micasense RedEdge-P

import argparse
import os
import re
import csv

if  __name__ == "__main__":

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description="""format Emlid Reach _events.pos file for Agisoft Metashape processing of Micasense .tifs""")
    parser.add_argument("-i", help=" : original _events.pos file")
    parser.add_argument("-o", help=" : path of to-be-created _events file with image numbers present")
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o

    def create_image_location_file(input_path, output_path):
        img_counter = 0

        try:
            # with open(input_path, 'rb') as f:
            with open(output_path, 'w') as o:
                with open(input_path, 'r') as f:
                    text_reader = csv.reader(f, delimiter=' ')
                    for row in text_reader:
                        date_to_img = re.match(r'\d{4}.\d{2}.\d{2}', row[0])
                        if date_to_img:
                            # g = open(output_path, 'ab')
                            # text_writer = csv.writer(g, delimiter=' ')
                            text_writer = csv.writer(o, delimiter=',')
                            text_writer.writerow([('IMG_%04d_1.tif' % (img_counter))]
                            + [row[4]]
                            + [row[5]]
                            + [row[8]])
                            img_counter += 1
        except IndexError:
            print("\ndoes your file end in an empty line?")
            print("processed ", img_counter, "images. ")

    create_image_location_file(input_path, output_path)


