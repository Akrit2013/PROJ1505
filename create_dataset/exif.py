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
            self.focal_in35 = None
            self.brand = None
            return
        self.exifs = self.exif.findall('exif')
        self.camera = self.get_camera()
        self.focal_length = self.__get_focal_length()
        self.aperture = self.__get_aperture()
        self.exposure = self.__get_exposure()
        self.lens = self.get_lens()
        self.focal_in35 = self.__get_focal_in35()
        self.brand = self.get_brand()

    def get_focal_length(self):
        for info in self.exifs:
            if info.get('label') == 'Focal Length' or\
                    info.get('tag') == 'FocalLength':
                return info.find('raw').text

    def __get_focal_length(self):
        """Return the pure focal length like '18' '35' '50' instead of
        '18.0mm' or '35mm'
        """
        focal = self.get_focal_length()
        rst = focal.split(' ')[0]
        return rst.split('.')[0]

    def __get_focal_in35(self):
        """Get the focal length in 35mm camera
        """
        for info in self.exifs:
            if info.get('label') == 'Focal Length (35mm format)' or\
                    info.get('tag') == 'FocalLengthIn35mmFormat':
                focal = info.find('raw').text
                return focal.split(' ')[0]
        else:
            return None

    def get_camera(self):
        camera = self.exif.get('camera')
        if camera is not None:
            return camera

        for info in self.exifs:
            if info.get('label') == 'Model':
                return info.find('raw').text
        else:
            return None

    def get_lens(self):
        for info in self.exifs:
            if info.get('label') == 'Lens Info' or\
                    info.get('tag') == 'LensInfo':
                return info.find('raw').text
        else:
            return None

    def get_brand(self):
        for info in self.exifs:
            if info.get('label') == 'Make' or\
                    info.get('tag') == 'Make':
                return info.find('raw').text
        else:
            return None

    def get_exposure(self):
        for info in self.exifs:
            if info.get('label') == 'Exposure' or\
                    info.get('tag') == 'ExposureTime':
                return info.find('raw').text
        else:
            return None

    def __get_exposure(self):
        """Return exposure as number like '200', '60' instead of '1/200'
        or '1/60'
        """
        exp = self.get_exposure()
        rst = exp.split('/')
        return rst[-1]

    def get_aperture(self):
        for info in self.exifs:
            if info.get('label') == 'Aperture' or\
                    info.get('tag') == 'FNumber':
                return info.find('raw').text
        else:
            return None

    def __get_aperture(self):
        """Return pure aperture number like '2.8' '3.5' instead of 'f2.8' or
        '1/2.8'
        In this case, it is the same as the self.get_aperture
        """
        for info in self.exifs:
            if info.get('label') == 'Aperture' or\
                    info.get('tag') == 'FNumber':
                return info.find('raw').text
        else:
            return None
