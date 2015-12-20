#!/usr/bin/python

# This script read the index text file created by dataset_create_imagelist.py
# and convert the focal length to corresponding class label according to the
# setting in the classifier.xml

import myxml
import getopt
import sys
import glog as log
import crash_on_ipy


def get_class(focal_dict, focal):
    """Return the class label which the focal belongs to
    """
    for label in focal_dict:
        if focal >= focal_dict[label][0] and focal <= focal_dict[label][1]:
            return label
    else:
        return None


def main(argv):
    src_file = None
    dst_file = None
    config_file = None
    result_dict = {}
    help_msg = 'dataset_split_class.py -i <indexfile> -o <output> -c <config>\n\
-i <file>           The input index text file\n\
-o <file>           The output index text file\n\
-c <file>           The configure xml file'

    try:
        opts, args = getopt.getopt(argv, 'hi:c:o:')
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
        elif opt == '-c':
            config_file = arg
        else:
            print help_msg
            sys.exit(2)

    if src_file is None or dst_file is None or config_file is None:
        print help_msg
        sys.exit(2)

    # Check the config file
    log.info('Parsing configure file: %s' % config_file)
    config = myxml.parse_classifier_xml(config_file)
    result_dict = dict.fromkeys(config)
    if config is None:
        log.fatal('Parse configure file %s error' % config_file)
        sys.exit(2)
    # Check the src_file
    log.info('Opening %s' % src_file)
    try:
        src_fp = open(src_file, 'r')
    except IOError:
        log.fatal('Can not open %s' % src_file)
        sys.exit(2)
    # Open the dst file
    log.info('Opening %s' % dst_file)
    try:
        dst_fp = open(dst_file, 'w')
    except IOError:
        log.fatal('Can not open %s' % dst_file)
        sys.exit(2)

    # loop the src_file
    for line in src_fp.readlines():
        element = line.split(' ')
        if len(element) != 2:
            log.warn('\033[31mWARNING:\033[0m Extra space in %s' % line)
            continue
        focal_length = int(element[-1])
        image_path = element[0]
        # Get the label
        label = get_class(config, focal_length)
        if label is None:
            log.warn('\033[32mSKIP:\033[0m %s' % line)
            continue
        if result_dict[label] is None:
            result_dict[label] = 1
        else:
            result_dict[label] += 1
        # Write the new file
        dst_fp.writelines(image_path + ' %d\n' % label)

    src_fp.close()
    dst_fp.close()
    log.info('Final result: %s' % str(result_dict))
    log.info('Finished')


if __name__ == '__main__':
    main(sys.argv[1:])
