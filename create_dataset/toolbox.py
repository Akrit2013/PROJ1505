# This toolbox contains tool functions could be used in general perpose

import time


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


def checkphoto(rsp):
    """Check if the given photo info is qualified, and whether the photo
    is taken in horizontal position or vertical position.
    If horizontal,                  return 1
    If vertical,                    return 2
    If the photo is unqualified,    return 0
    """
    pass


def pause(hit_limit=3600, record=[]):
    """According to the flickr limit, and the last time it been called,
    pause a certain mount of time, to avoid the flickr server over hit.
    """
    pass
