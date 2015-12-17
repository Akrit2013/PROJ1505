#!/usr/bin/python

# This script read the flickr_lmdb file created by fetch_image_info.py
# Iter the database get the url and download the image into target dir

import toolbox as tb
import lmdbtools as lt
import getopt
import sys
import glog as log
import yaml
import myxml
import crash_on_ipy


def main(argv):
    db_file = None
    skip_num = None
    data_path = '../data'
    overwrite = False
    help_msg = 'download_image.py -i <lmdbfile> -o[optional] <datapath>\
--overwrite[optional] --skip <num>\n\
-i <lmdbfile>       The input lmdb file contains the exif of photos\n\
-o <datapath>       The path where to store the downloaded photos\n\
--overwrite         If set, overwrite the exists photos, default not\n\
--skip <num>        Skip the first XX photos'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['overwrite', 'skip='])
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
            data_path = arg
        elif opt == '--overwrite':
            overwrite = True
        elif opt == '--skip':
            skip_num = int(arg)
        else:
            print help_msg
            sys.exit(2)

    if db_file is None:
        print help_msg
        sys.exit(2)

    # Try to open the database file
    db = lt.open_db_ro(db_file)
    if db is None:
        log.fatal('\033[0;31mCan not open %s\033[0m' % db_file)
        sys.exit(2)

    # Get the entries from the database
    entries = db.stat()['entries']
    # Entries counter
    counter = 0
    # Check the data path
    if not tb.check_path(data_path):
        log.info('Create new dir %s' % data_path)
    # Iter the data base
    if skip_num is not None:
        log.info('Skipping the first %d entries...' % skip_num)
    with db.begin(write=False) as txn:
        with txn.cursor() as cur:
            for key, val in cur:
                counter += 1
                if skip_num is not None and counter < skip_num:
                    continue
                # Parse the val into dict
                val_dic = yaml.load(val)
                # Get the avaliable url to download photo
                photo = myxml.parse_xml_to_etree(val_dic['photo'])
                url = tb.get_url(photo, val_dic['urls'], True)
                # Download the url and save image
                log.info('Download %s from %s [%d/%d]' %
                         (key, url, counter, entries))
                try:
                    tb.download_url_and_save(url, key, overwrite, data_path)
                except:
                    log.error('\033[0;31mFailed to download %s from %s\033[0m'
                              % (key, url))
                    continue

    db.close()


if __name__ == "__main__":
    main(sys.argv[1:])
