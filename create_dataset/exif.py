#!/usr/bin/python

# This module define a exif class, and parse the exif information from the exif
# etree retrieved from flickr server by using flickr.photo.getExif method
import glog as log


class exif():
    def __init__(self, root):
        # Judge is the exif include the rst node
        stat = root.attrib['stat']
        if stat is None:
            self.exif = root
        elif stat == 'ok':
            self.exif = root.find('photo')
        else:
            log.error('The stat is not OK')
            self.camera = None
            self.focal_length = None
            self.aperture = None
            self.exposure = None
            self.lens = None
            return
        self.camera = self.get_camera()
        self.focal_length = self.__get_focal_length()
        self.aperture = self.__get_aperture()
        self.exposure = self.__get_exposure()
        self.lens = self.get_lens()

    def get_focal_length(self):
        pass

    def __get_focal_length(self):
        """Return the pure focal length like '18' '35' '50' instead of
        '18.0mm' or '35mm'
        """

    def get_camera(self):
        pass

    def get_lens(self):
        pass

    def get_brand(self):
        pass

    def get_exposure(self):
        pass

    def __get_exposure(self):
        """Return exposure as number like '200', '60' instead of '1/200'
        or '1/60'
        """
        pass

    def get_aperture(self):
        pass

    def __get_aperture(self):
        """Return pure aperture number like '2.8' '3.5' instead of 'f2.8' or
        '1/2.8'
        """
        pass
