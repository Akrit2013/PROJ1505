#!/usr/bin/python

# This script read the lmdb dataset which is created by fetch_image_info.py
# It will load the lmdb file and analyze the focal length info in each photo
# entry, and draw the information.

import getopt
import sys
import glog as log
import lmdbtools as lt
import matplotlib.pyplot as plt
import easyprogressbar as eb
import yaml
import numpy as np


def main(argv):
    db_file = None
    helpmsg = 'analyze_lmdb_info.py -i <lmdbfile>'
    rst = {}
    vector = []

    try:
        opts, args = getopt.getopt(argv, 'hi:')
    except getopt.GetoptError:
        print helpmsg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print helpmsg
            sys.exit()
        elif opt == '-i':
            db_file = arg

    # Open the lmdb file
    if db_file is None:
        print helpmsg
        sys.exit(2)

    log.info('Open the lmdb file %s' % db_file)
    db = lt.open_db_ro(db_file)
    db_stat = db.stat()
    log.info('Total Entries: %d' % db_stat['entries'])
    vector = np.zeros(db_stat['entries'])
    bar = eb.EasyProgressBar()
    bar.set_end(db_stat['entries'])
    bar.start()
    counter = 0
    err_counter = 0
    # Iter the the database
    with db.begin(write=False) as txn:
        with txn.cursor() as cur:
            for key, val in cur:
                counter += 1
                try:
                    val_dic = yaml.load(val)
                    focal_in35 = int(val_dic['focal_in35'])
                except:
                    err_counter += 1
                    continue
                # Filter our some error value
                if focal_in35 < 5 or focal_in35 > 200:
                    continue
                vector[counter-1] = focal_in35
                if focal_in35 in rst:
                    rst[focal_in35] += 1
                else:
                    rst[focal_in35] = 1
                bar.update(counter)
    db.close()
    bar.finish()
    vector = list(vector[vector != 0])
    log.info('Finished, errors: %d, The result:' % err_counter)
    print str(rst)
    # Draw the plot
    plt.hist(vector, bins=50)
    plt.xlabel('Focal')
    plt.ylabel('Photos')
    plt.title('Photo count in each focal')
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
