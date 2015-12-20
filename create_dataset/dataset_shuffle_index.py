#!/usr/bin/python

# This script load the index text file, created by dataset_split_class.py first
# and shuffle the list.

import sys
import getopt
import glog as log
import random


def main(argv):
    src_file = None
    dst_file = None
    src_content = []
    help_msg = 'dataset_shuffle_index.py -i <infile> -o <shuffledfile>'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:')
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-i':
            src_file = arg
        elif opt == '-o':
            dst_file = arg

    if src_file is None or dst_file is None:
        print help_msg
        sys.exit(2)

    # Open the files
    try:
        src_fp = open(src_file, 'r')
    except IOError:
        log.fatal('Can not open %s' % src_file)
        sys.exit(2)
    try:
        dst_fp = open(dst_file, 'w')
    except IOError:
        log.fatal('Can not open %s' % dst_file)
        sys.exit(2)

    # Load the src file
    log.info('Loading %s ...' % src_file)
    for line in src_fp.readlines():
        src_content.append(line)
    # shuffle the lines
    log.info('Shuffling lines ...')
    random.shuffle(src_content)
    log.info('Writing %s ...' % dst_file)
    # Write it the dst_file
    for line in src_content:
        dst_fp.writelines(line)
    src_fp.close()
    dst_fp.close()
    log.info('Finished')


if __name__ == '__main__':
    main(sys.argv[1:])
