# This module include all kinds of tool functions related to lmdb database

import lmdb
import shutil
import sys
import os
import glog as log
import toolbox as tb
import xml.etree.ElementTree as ET
import yaml


def open_db(lmdb_file):
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
    return db


def pack(exif, photo, label, config=None):
    """Pack the necessary information into a single string, which should
    be used in write_db function.
    """
    package = {}
    package['label'] = label
    # Get the photo pos
    if config is None:
        pos = None
    else:
        pos = tb.get_photo_pos(photo, config)
    package['pos'] = pos
    # Get the focal in 135 camera
    if config is None or exif is None:
        focal_in35 = None
    else:
        focal_in35 = tb.get_focal_in35(exif, config)
    package['focal_in35'] = focal_in35
    # Convert photo to XML string
    package['photo'] = ET.tostring(photo, encoding='utf8', method='xml')
    # Convert exif to xml string
    if exif is None:
        package['exif'] = None
    else:
        package['exif'] = ET.tostring(exif.exif, encoding='utf8', method='xml')
    # Pack the dict to string
    package = yaml.dump(package)
    return package


def write_db(db, exif=None, photo=None, label=None, config=None):
    """Convert the needed info into string, and store them into a lmdb
    database. The key of each entry is the id of the photo, which will
    avoid the repeated photos.
    Output:
        The return value is the current size of the database
    Input:
        db      The database object
        exif    The exif object in exif.py module
        photo   The etree object of a photo
        label   A string include both scene and lens, like: '35mm, city'
    Howto Orgnize the lmdb content:
        Key     The photo id
        value   A string converted from a dict by YAML. The dict include
                following sections.
    ===================================================================
        label       '35mm, city'
        pos         'hor'/'ver'
        focal_in35  '85'
        photo       The XML string generated by photo etree
        exif        The XML string generated by exif.exif etree
    """
    if exif is not None:
        key = exif.id
    else:
        key = photo.get('id')
    # Pack the needed info into a single string
    value = pack(exif, photo, label, config)
    with db.begin(write=True) as txn:
        txn.put(key, value)
    # Return the size of the dataset
    stat = db.stat()
    return stat['entries']


def check_photo_id(db, photo_id):
    """Check if the lmdb database already have the given photo, if true
    return True, else, return False
    """
    rst = None
    # Don't allow write, and use buffers to avoid memory copy
    with db.begin(write=False, buffers=True) as txn:
        val = txn.get(photo_id)
        if val is None:
            rst = False
        else:
            rst = True
    return rst
