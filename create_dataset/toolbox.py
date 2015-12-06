# This toolbox contains tool functions could be used in general perpose

import time
import glog as log


def unixtime_to_datearr(timestamp):
    """This function convert the unix time stamp into the normal readable
    data array.
    The input can be a string or a int/float number
    """
    timeArray = time.localtime(float(timestamp))
    timeArray = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return timeArray


def check(rsp):
    """Check if the flickr request return ok"""
    if rsp.attrib['stat'] == 'ok':
        return True
    else:
        return False


def exif_camera(exif):
    """Get the camera model from exif info, if can not find one
    return None
    """
    camera = exif.get('camera')
    if camera is not None:
        return camera

    exifs = exif.findall('exif')
    for info in exifs:
        if info.get('label') == 'Model':
            return info.find('raw').text
    else:
        return None


def exif_focal(exif):
    """Get the focal length from exif info, if not exists return None
    """
    exifs = exif.findall('exif')
    for info in exifs:
        if info.get('label') == 'Focal Length' or\
                info.get('tag') == 'FocalLength':
            return info.find('raw').text
    pass


def exif_lens(exif):
    """Get lens type, return string or None
    """
    exifs = exif.findall('exif')
    for info in exifs
    pass


def exif_aperture(exif):
    """Get aperture info, return string or None
    """
    pass


def exif_exposure(exif):
    """Get shutter speed, return string of None
    """
    pass


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


def check_exif(exif, config):
    """Check if the exif is legal according to the config
    return True or False
    """
    pass


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

    if width is None or height is None:
        # Indicate the target url do not exist
        return None

    # Check if the length edge/short edge fit the config
    lwrate = max(height, width) / min(height, width)
    # load the config
    lwratio_list = config.get_lwratio()
    # iter the config
    for lwratio in lwratio_list:
        ratio = lwratio[0]
        error = lwratio[1]
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
    exif = flickr.photos.getExif(photo_id=photo.get('id'))
    # If exif return none, give warning
    if exif is None or exif.get('stat') != 'ok':
        log.error('The exif of photo: %s is None' % photo.get('id'))
        return None
    exif = exif.find('photo')
    # Check if the exif content is legal
    if check_exif(exif, config):
        # Disp the exif info
        log.info('Accept: %s, %s' % (exif_camera(exif), exif_focal(exif)))
        return exif
    else:
        log.info('Denied: %s, %s' % (exif_camera(exif), exif_focal(exif)))
        return None
