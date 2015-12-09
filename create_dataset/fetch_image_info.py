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
import flickrapi
import crash_on_ipy
import time


def main(argv):
    config_file = 'flickr.xml'
    db_file = 'flickr_info_lmdb'
    db_file_trash = None
    helpmsg = """fetch_image_info.py -c <configfile> -o <lmdbfile>
 -t[optional] <trashfile>"""

    try:
        opts, args = getopt.getopt(argv, "hc:o:t:")
    except getopt.GetoptError:
        print helpmsg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print helpmsg
            sys.exit()
        elif opt == '-c':
            config_file = arg
        elif opt == '-o':
            db_file = arg
        elif opt == '-t':
            db_file_trash = arg
        else:
            print helpmsg
            sys.exit(2)

    if db_file_trash is None:
        db_file_trash = db_file + '_trash'
    # Parse the xml config file
    config = myxml.xmlconfig(config_file)
    g_time_show_marker = time.time()
    g_time_show = int(config.time_show)

    # Create the lmdb database
    # Check if the lmdb file is already exist
    db = lt.open_db(db_file)
    db_trash = lt.open_db(db_file_trash)
    # Start to use flickrapi walk through the flickr server
    flickr = flickrapi.FlickrAPI(config.key, config.secret)

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

    log.info('Time interval is %d days %d hours %d secs' %
             tuple(tb.seconds_to_days(time_interval_num)))

    scenes_list = config.get_scenes_labels()
    lens_list = config.get_lens_labels()
    log.info('The scenes list is %s' % str(scenes_list))
    log.info('The lens list is %s' % str(lens_list))
    # Start to loop the data
    log.info('Start to fetch the photo info')

    # Globel counter
    # Count the total photos fetched
    g_photo_counter = 0
    # Count the photos which pass the screen procedure
    g_qualified_counter = 0

    db_size = 0
    db_trash_size = 0
    while time_current_num < time_end_num:
        start_time = str(time_current_num)
        end_time = str(time_current_num + time_interval_num)
        text_str = None
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
                log.info('\033[1;33mFetch date %s-%s, label: %s\033[0m' %
                         (tb.unixtime_to_datearr(start_time),
                          tb.unixtime_to_datearr(end_time),
                          text_str))
                log.info('\033[1;33mTime interval: %d days %d hours \
%d secs\033[0m' %
                         tuple(tb.seconds_to_days(time_interval_num)))
                log.info('\033[1;33mFetch Photos: %d, Qualified Photos: %d\
, Db Size: %d, Trash Size: %d\033[0m'
                         % (g_photo_counter, g_qualified_counter,
                            db_size, db_trash_size))
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
                    # Show the overall info if X sec passed
                    if time.time() - g_time_show_marker > g_time_show:
                        g_time_show_marker = time.time()
                        log.info('\033[1;33mFetch date %s-%s, label: %s\033[0m'
                                 % (tb.unixtime_to_datearr(start_time),
                                    tb.unixtime_to_datearr(end_time),
                                    text_str))
                        log.info('\033[1;33mFetch Photos: %d, Qualified Photos:\
%d, Db Size: %d, Trash Size: %d\033[0m' % (g_photo_counter,
                                 g_qualified_counter, db_size, db_trash_size))
                    photo_counter += 1
                    g_photo_counter += 1
                    # Check the database if the photo is already been recorded
                    if lt.check_photo_id(db, photo.get('id')):
                        continue
                    if lt.check_photo_id(db_trash, photo.get('id')):
                        continue
                    # Check the photo, and fetch the exif if needed
                    rst = tb.get_exif(flickr, photo, config)
                    # If photo info and exif is invalid, return None
                    if rst is None:
                        continue
                    else:
                        exif = rst[0]
                        stat = rst[1]
                        if stat:
                            qualified_counter += 1
                            g_qualified_counter += 1
                            db_size = lt.write_db(db, exif, photo,
                                                  text_str, config)
                        else:
                            db_trash_size = lt.write_db(db_trash, exif, photo,
                                                        text_str, config)
                    # Write the exif, photo info, label into db
                    # The database size should be returned
        # Finish the data slice loop, re-adjust the time_interval_num
        if config.time_dynamic:
            # Dynamically adjust the time interval
            mean_fetch_size = float(photo_counter) / batch_counter
            if mean_fetch_size > 1.2 * int(config.batch_size):
                time_interval_num = int(time_interval_num / 1.2)
            elif mean_fetch_size < 0.8 * int(config.batch_size):
                time_interval_num = int(time_interval_num / 0.8)
        # If the photo collected more than enough, make it stop
        if db_size > config.max_size:
            log.info('Total collected photos: %d, stop at %s' %
                     (db_size, tb.unixtime_to_datearr(end_time)))
            break

    # Finish the rest of the things.
    db.close()
    db_trash.close()


if __name__ == "__main__":
    main(sys.argv[1:])
