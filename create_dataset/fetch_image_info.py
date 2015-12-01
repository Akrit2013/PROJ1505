#!/usr/bin/python

# This script use flickrapi to fetch image information from the flickr webset
# First, it will read the config file from the flickr.xml, and then search
# the flickr webset according to the selected key word.
#
# The program will check each fetched image info, and get exif info of certain
# photos
# The exif information will also be screened, and the remaining exif info will
# be stored in lmdb database.

import myxml
import getopt
import glog as log
import sys
import lmdbtools as lt
import toolbox as tb
import fliclrapi
import math


def main(argv):
    config_file = 'flickr.xml'
    db_file = 'flickr_info_lmdb'
    helpmsg = """fetch_image_info.py -c <configfile> -o <lmdbfile>"""

    try:
        opts, args = getopt.getopt(argv, "hc:o:")
    except getopt.GetoptError:
        print helpmsg
        sys.exit(2)

    for opt, arg in opts:
        if opts == '-h':
            print helpmsg
            sys.exit()
        elif opts == '-c':
            config_file = arg
        elif opts == '-o':
            db_file = arg
        else:
            print helpmsg
            sys.exit(2)

    # Parse the xml config file
    config = myxml.xmlconfig(config_file)

    # Create the lmdb database
    # Check if the lmdb file is already exist
    db = lt.open_db(db_file)
    # Start to use flickrapi walk through the flickr server
    flickr = fliclrapi.FlickrAPI(config.key, config.secret)

    time_start_num = float(config.time_start)
    time_end_num = float(config.time_end)
    time_current_num = time_start_num

    log.info('The start time is %s' % tb.unixtime_to_datearr(time_start_num))
    log.info('The end time is %s' % tb.unixtime_to_datearr(time_end_num))
    if config.time_dynamic:
        log.info('The timing mode is dynamic')
        time_interval_num = float(config.time_interval_init)
    else:
        log.info('The timing mode is fixed')
        time_interval_num = float(config.time_interval)

    log.info('Time interval is %s' %
             tb.unixtime_to_datearr(time_interval_num))

    scenes_list = config.get_scenes_labels()
    lens_list = config.get_lens_labels()
    log.info('The scenes list is %s' % str(scenes_list))
    log.info('The lens list is %s' % str(lens_list))
    # Start to loop the data
    log.info('Start to fetch the photo info')

    # Globel counter
    # This count the flickr hit times
    g_hit_counter = 0
    # Count the total photos fetched
    g_photo_counter = 0
    # Count the photos which pass the screen procedure
    g_qualified_counter = 0

    while time_current_num < time_end_num:
        start_time = str(time_current_num)
        end_time = str(time_current_num + time_interval_num)
        text_str = None
        db_size = 0
        extra_str = config.urls + ', ' + 'tags'
        # Counter in this time slice
        photo_counter = 0
        qualified_counter = 0
        batch_counter = 0
        # Loop the labels
        for lens_label in lens_list:
            for scenes_label in scenes_list:
                batch_counter += 1
                text_str = lens_label + ', ' + scenes_label
                log.info('Fetch date %s-%s, label: %s, db_size: %d' %
                         (tb.unixtime_to_datearr(start_time),
                          tb.unixtime_to_datearr(end_time),
                          text_str, db_size))
                # Search the photos according to the label
                # A list to store all the fetched photos
                for photo in flickr.walk(tag_mode='all',
                                         text=text_str,
                                         min_upload_date=start_time,
                                         max_upload_date=end_time,
                                         privacy_filter=1,
                                         content_type=1,
                                         extras=extra_str,
                                         per_page=int(config.page_size)):
                    # Store all the photos into a list
                    photo_counter += 1
                    # Check the photo, and fetch the exif if needed
                    exif = tb.get_exif(photo)
                    # If photo info and exif is invalid, return None
                    if exif is None:
                        continue
                    else:
                        qualified_counter += 1
                    # Write the exif, photo info, label into db
                    # The database size should be returned
                    db_size = lt.write_db(db, exif, photo, text_str)
        # Finish the data slice loop, re-adjust the time_interval_num
        if config.time_dynamic:
            # Dynamically adjust the time interval
            mean_fetch_size = int(photo_counter/float(len(lens_list)*len(scenes_list)))
            if 


if __name__ == "__main__":
    main(sys.argv[1:])
