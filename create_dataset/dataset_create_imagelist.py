#!/usr/bin/python

# This script load the lmdb dataset created by fetch_image_info.py and check if
# the image has been download correctly. If true, write the image full path
# and the corresponding focal length in 135 system in a text file. e.g.
# /dataset/img1232434.jpg   35
# /dataset/img4354524.jpg   28

import lmdbtools as lt
import getopt
import glog as log
import yaml
import sys
import os
import easyprogressbar as eb
import Image
import myxml


def main(argv):
    db_file = None
    list_file = None
    img_path = None
    ext = '.jpg'
    if_check = False
    help_msg = 'dataset_create_imagelist.py -i <lmdb> -p <image path> -o <list>\
--check\n\
-i <lmdb>           The input lmdb database file\n\
-o <list>           The output image list file\n\
-p <image path>     The path which store the downloaded images\n\
--check [optional]  Force to check if the jpg image can be loaded.\n\
                    Which will slow down the process. Default False'
    try:
        opts, args = getopt.getopt(argv, 'hi:p:o:', ['check'])
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-i':
            db_file = arg
        elif opt == '-o':
            list_file = arg
        elif opt == '-p':
            img_path = arg
        elif opt == '--check':
            if_check = True
        else:
            print help_msg
            sys.exit(2)
    # Check arguments
    if db_file is None or list_file is None or img_path is None:
        print help_msg
        sys.exit(2)

    # Check if the image path exists
    log.info('Check image path %s' % img_path)
    if os.path.exists(img_path) is False:
        log.fatal('Can not locate the image path %s' % img_path)
        sys.exit(2)
    # Create the text list file
    log.info('Open the image list file %s' % list_file)
    try:
        fp = open(list_file, 'w')
    except IOError:
        log.fatal('Can not open %s for writing' % list_file)
        sys.exit(2)
    # open the lmdb file
    log.info('Open db file %s' % db_file)
    db = lt.open_db_ro(db_file)
    db_stat = db.stat()
    log.info('Total Entries: %d' % db_stat['entries'])
    bar = eb.EasyProgressBar()
    bar.set_end(db_stat['entries'])
    bar.start()
    counter = 0
    err_counter = 0
    # Iter the whole database
    with db.begin(write=False) as txn:
        with txn.cursor() as cur:
            for key, val in cur:
                counter += 1
                # Get the avaliable url to download photo
                try:
                    val_dic = yaml.load(val)
                    photo = myxml.parse_xml_to_etree(val_dic['photo'])
                    photo_id = photo.get('id')
                    focal_in35 = int(val_dic['focal_in35'])
                except:
                    err_counter += 1
                    continue
                # Filter our some error value
                if focal_in35 < 5 or focal_in35 > 200:
                    continue
                # Get the image full name
                if img_path[-1] == r'/':
                    img_name = img_path + photo_id + ext
                else:
                    img_name = img_path + r'/' + photo_id + ext
                img_name = os.path.abspath(img_name)
                # Check if the image exists
                if if_check:
                    # Load the image
                    try:
                        Image.open(img_name)
                    except:
                        err_counter += 1
                        continue
                else:
                    if os.path.exists(img_name) is False:
                        err_counter += 1
                        continue

                # Write the info to list file
                fp.writelines(img_name + ' %d\n' % focal_in35)
                bar.update(counter)
    # Finish the loop
    db.close()
    fp.close()
    bar.finish()
    log.info('Finished. errors: %d' % err_counter)


if __name__ == '__main__':
    main(sys.argv[1:])
