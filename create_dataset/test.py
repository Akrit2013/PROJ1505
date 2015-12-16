#!/usr/bin/python

import easyprogressbar
import glog as log
from requests.exceptions import ConnectionError


def tt():
    a = 1
    b = 2
    raise ConnectionError
    return a, b


def main():
    pb = easyprogressbar.EasyProgressBar()
    pb.start()
    for i in range(100):
        print i
        pb.update(i)
    pb.finish()
    try:
        tt()
    except ConnectionError as e:
        print e
        log.error('Error: %s' % e)
    print 'finish'


if __name__ == "__main__":
    main()
