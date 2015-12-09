# This toolbox contains tool functions could be used in general perpose

import time
import glog as log
import exif as ex
import flickrapi.exceptions


def unixtime_to_datearr(timestamp):
    """This function convert the unix time stamp into the normal readable
    data array.
    The input can be a string or a int/float number
    """
    timeArray = time.localtime(float(timestamp))
    timeArray = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return timeArray


def seconds_to_days(seconds):
    """Convert seconds into days, hours, and seconds, the return val is
    a list, the format is [d, h, s]
    """
    sec = seconds % 3600
    hours = int(seconds/3600)
    hor = hours % 24
    day = int(hours/24)
    return [day, hor, sec]


def check(rsp):
    """Check if the flickr request return ok"""
    if rsp.attrib['stat'] == 'ok':
        return True
    else:
        return False


def pause(hit_limit=3500, last_hit=[0.0]):
    """According to the flickr limit, and the last time it been called,
    pause a certain mount of time, to avoid the flickr server over hit.
    The last_hit record the last time this function was called, and
    according to this timestamp, deside how lang should pause this time
    """
    time_interval = 3600 / float(hit_limit)
    # Get the current time
    time_current = time.time()
    time_elaps = time_current - last_hit[0]
    if time_elaps < time_interval:
        time.sleep(time_interval-time_elaps)
    last_hit[0] = time.time()


def check_exif(exif, config):
    """Check if the exif is legal according to the config
    return True or False.
    1. the focal_length should be found.
    2. the camera model should be recognized.
    """
    if exif.focal_length is None:
        return False
    focal_rate = get_focal_rate(exif, config)
    if focal_rate is None:
        return False

    return True


def match_words(keywords, target):
    """ Find if all the keywords exist in the target string.
    If true, return True
    Note: the keywords match is case in-sensitive, and the whole word
    will be matched. e.g. d700 will match D700, but not d7000
    Input:
        keywords will be a list contain keyword list
        target will be a string of words separated by space
    """
    # First, separate the target string into words
    target_words = target.split(' ')
    # Loop the keywords
    for keyword in keywords:
        for target_word in target_words:
            if keyword.lower() == target_word.lower():
                break
        else:
            return False
    return True


def get_focal_rate(exif, config):
    """ First, determine the focal length rate relative to 135 format
    camera, according to the camera model.
    If the camera model can not be found in config, return None
    """
    camera_model_list = config.get_camera_model()
    if camera_model_list is None:
        log.error('Can not get camera_model in config object')
        return None
    # Split the camera model into several key words, and match it with
    # the camera model in config. Only all key words can be matched, the
    # corresponding focal rate will be returned.
    # Match the keywords with the camera_model_list
    for camera_model in camera_model_list:
        camera_keywords = camera_model[0].split(' ')
        focal_rate = float(camera_model[1])
        if match_words(camera_keywords, exif.camera):
            return focal_rate
    # If nothing can be matched, return None
    return None


def get_photo_pos(photo, config):
    """Return the photo position: 'hor' or 'ver'
    If can not find such info, return None
    """
    url_list = config.get_urls()
    width = None
    height = None
    # Check if the photo support the required url
    for url in url_list:
        addr = photo.get(url)
        if addr is None:
            continue
        # Get the height and width info
        parts = url.split('_')
        ext = parts[-1]
        width_att = 'width_' + ext
        height_att = 'height_' + ext
        width = int(photo.get(width_att))
        height = int(photo.get(height_att))
        break

    if width is None or height is None:
        # Indicate the target url do not exist
        return None
    if width > height:
        return 'hor'
    else:
        return 'ver'


def get_focal_in35(exif, config):
    """ This function convert the focal length in 135mm camera format.
    First, it will attempt to read the FocalLengthIn35mmFormat section,
    if exist, it will be returned as the result.
    If not, it will calculate the 135 format focal length according to
    the config
    """
    if exif is None:
        return None
    if exif.focal_in35 is not None:
        return int(exif.focal_in35)

    if exif.focal_length is None:
        return None

    # Get the conreponding focal rate
    rate = get_focal_rate(exif, config)
    if rate is None:
        return None
    return int(rate*float(exif.focal_length))


def get_exif(flickr, photo, config):
    """First this function will check the basic info of the photo:
    1. If the photo is croped
    2. If the photo have the qualified url link
    If the photo basic info is qualified, the exif information
    of the photo will be retrived.
    Then, the exif info of the photo will be checked:
    1. If the exif record the camera type and the focus length
    If the exif pass the check, it will be returned. Else, the
    function will return None.

    Parameters:
    photo is the etree object only contrain the photo section
    config is a myxml.xmlconfig object
    Return:
    If the photo is illegal and no exif is got, return None
    If the exif is got but contrain no useful info, return [exif, False]
    If the exif fetch is denied, return [None, False]
    If the exif is got and ok, return [exif, True]
    """
    url_list = config.get_urls()
    width = None
    height = None
    # Check if the photo support the required url
    for url in url_list:
        addr = photo.get(url)
        if addr is None:
            continue
        # Get the height and width info
        parts = url.split('_')
        ext = parts[-1]
        width_att = 'width_' + ext
        height_att = 'height_' + ext
        width = int(photo.get(width_att))
        height = int(photo.get(height_att))
        break

    if width is None or height is None:
        # Indicate the target url do not exist
        return None

    # Check if the length edge/short edge fit the config
    lwrate = float(max(height, width)) / min(height, width)
    # load the config
    lwratio_list = config.get_lwratio()
    # iter the config
    for lwratio in lwratio_list:
        ratio = float(lwratio[0])
        error = float(lwratio[1])
        pos = lwratio[2]
        # Check the pos
        if pos.lower() == 'hor':
            if height > width:
                continue
        if pos.lower() == 'ver':
            if height < width:
                continue
        # Check the lwratio
        if lwrate < ratio*(1+error) and lwrate > ratio*(1-error):
            break
    else:
        # Can not find matched config
        return None

    # Start to fetch the exif info
    # Pause if needed
    pause(config.hit_limit)
    try:
        exif = flickr.photos.getExif(photo_id=photo.get('id'))
    except flickrapi.exceptions.FlickrError:
        log.error('Denied: Get EXIF info of photo %s' % photo.get('id'))
        return [None, False]
    # If exif return none, give warning
    if exif is None or exif.get('stat') != 'ok':
        log.error('The exif of photo: %s is None' % photo.get('id'))
        return [None, False]
    myexif = ex.exif(exif)
    # Check if the exif content is legal
    if check_exif(myexif, config):
        # Disp the exif info
        log.info('\033[1;32;40mAccept\033[0m: %s, Focal %s, in35 %d' %
                 (myexif.camera, myexif.focal_length,
                  get_focal_in35(myexif, config)))
        return [myexif, True]
    else:
        log.info('\033[1;31;40mDenied\033[0m: %s, Focal %s' %
                 (myexif.camera, myexif.focal_length))
        return [myexif, False]
