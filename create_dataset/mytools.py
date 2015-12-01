# This module include all kinds of tool functions related to lmdb database

import lmdb
import shutil
import sys
import os
import glog as log


def open_lmdb(lmdb_file):
    """Check if the lmdb file already exists, and ask whether delete it
    or keep add entries based on it.
    return the lmdb object
    """
    if os.path.exists(lmdb_file):
        print('%s is already exists.' % lmdb_file)
        k = raw_input('Do you want to delete it?[y/n]:')
        if k == 'y' or k == 'Y':
            log.warn('Delete the %s file' % lmdb_file)
            shutil.rmtree(lmdb_file)
        elif k == 'n' or k == 'N':
            log.warn('Keep the %s file, and new entries will be added' %
                     lmdb_file)
        else:
            log.error('Wrong key input, exit the program')
            sys.exit(2)

    db = lmdb.open(lmdb_file, map_size=int(1e12))


