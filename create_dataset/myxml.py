# This model contains the functions need to parse the flickr.xml
# configure file.

import xml.etree.ElementTree as et
import glog as log
import time
import datetime
from lxml import etree


class xmlconfig():
    """This class read the flickr config xml file and parse the
    the information from the config file.
    All kinds of information can be retrived from the provided
    functions.
    """
    def __init__(self, config):
        self.config = config
        self.root = et.parse(self.config).getroot()
        try:
            self.version = float(self.root.attrib['ver'])
        except:
            log.warn('The xml config file does not contains a version')
            self.version = None
        # Parse the whole xml file to check whether it is intact
        self.auth = self.root.find('auth')
        if self.auth is None:
            log.error('The xml config file has no auth section')

        self.time = self.root.find('time')
        if self.time is None:
            log.error('The xml config file has no time section')

        self.fetch = self.root.find('fetch')
        if self.fetch is None:
            log.error('The xml config file has no fetch section')

        self.hitcontrol = self.root.find('hitcontrol')
        if self.hitcontrol is None:
            log.error('This xml config file has no hitcontrol section')

        self.photoscreen = self.root.find('photoscreen')
        if self.photoscreen is None:
            log.error('This xml config file has no photoscreen section')

        # Init the members of this class
        self.key = self.get_key()
        self.secret = self.get_secret()
        self.time_end = self.get_end_time()
        self.time_start = self.get_start_time()
        self.time_interval = self.get_interval()
        self.time_interval_min = self.get_interval_min()
        self.time_interval_max = self.get_interval_max()
        self.time_interval_init = self.get_interval_init()
        self.time_dynamic = self.is_dynamic_time()
        self.time_show = self.get_show_time()
        self.hit_limit = self.get_hit_limit()
        self.page_size = self.get_page_size()
        self.max_size = self.get_max_size()
        self.batch_size = self.get_batch_size()
        self.urls = self.__combine_list_to_string(self.get_urls())

    def get_key(self):
        if self.auth is None:
            return None
        else:
            return self.auth.attrib['key']

    def get_secret(self):
        if self.auth is None:
            return None
        else:
            return self.auth.attrib['secret']

    def is_dynamic_time(self):
        tp = self.time.attrib['type']
        if tp.lower() == 'dynamic':
            return True
        elif tp.lower() == 'fixed':
            return False
        else:
            log.error('Can not tell whether the time type is dynamic or fixed')
            return None

    def convert_flickrdate_to_unix(self, datestr):
        """To make it simpler, only take 'YYYY-MM-DD' as input parameter
        """
        d = datetime.datetime.strptime(datestr, "%Y-%m-%d")
        unix_stamp = time.mktime(d.timetuple())
        return unix_stamp

    def __get_time(self, namestr):
        timestr = self.time.find(namestr).attrib['val']
        try:
            fmt = self.time.find(namestr).attrib['format']
        except:
            log.warn('Can not tell the date format, return directly')
            return timestr

        if fmt.lower() == 'flickr':
            return self.convert_flickrdate_to_unix(timestr)
        elif fmt.lower() == 'unix':
            return timestr
        else:
            log.warn('Can not tell the date format, return directly')
            return timestr

    def get_start_time(self):
        return self.__get_time('time_start')

    def get_end_time(self):
        return self.__get_time('time_end')

    def get_interval(self):
        return self.__get_time('time_interval')

    def get_interval_min(self):
        return self.__get_time('time_interval_min')

    def get_interval_max(self):
        return self.__get_time('time_interval_max')

    def get_interval_init(self):
        return self.__get_time('time_interval_init')

    def get_show_time(self):
        return self.__get_time('time_show')

    def get_scenes_labels(self):
        """Get all scene labels from the xml config file, return them
        into a list
        """
        return self.__get_labels('scenes')

    def get_lens_labels(self):
        """Get all lens labels from the xml config file, return them
        into a list
        """
        return self.__get_labels('lens')

    def __get_labels(self, label_type):
        labels_vec = self.fetch.findall('labels')
        target_labels = None
        for labels in labels_vec:
            if labels.attrib['type'] == label_type:
                target_labels = labels

        if target_labels is None:
            log.error('Can not find the %s labels' % label_type)
            return None

        label_vec = target_labels.findall('label')
        label_list = []
        for label in label_vec:
            label_list.append(label.text)

        return label_list

    def get_urls(self):
        """Get the targeted urls, and return as a list
        """
        urls = self.fetch.find('urls')
        url_vec = urls.findall('url')
        url_list = []
        for url in url_vec:
            url_list.append(url.text)

        return url_list

    def get_hit_limit(self):
        return self.hitcontrol.find('hit_limit').text

    def get_page_size(self):
        return self.fetch.find('page').attrib['size']

    def get_max_size(self):
        return self.fetch.attrib['maxsize']

    def get_batch_size(self):
        return self.fetch.attrib['batchsize']

    def __combine_list_to_string(self, var):
        """This function combine a list into a string
        e.g. ['ab', 'cd'] will be converted into 'ab, cd'
        """
        if var is None:
            return None
        combstr = ''
        for ele in var:
            combstr = combstr + str(ele) + ', '
        # Delete the last ','
        return combstr[:-2]

    def get_camera_model(self):
        """
        The return value is a list of list, for example:
        [[model1, focal1], [model2, focal2], ...]
        """
        if self.photoscreen is None:
            return None
        model_list = self.photoscreen.find('camera').findall('model')
        rst = []
        for model in model_list:
            rst.append([model.text, model.attrib['focal']])

        return rst

    def get_lwratio(self):
        """
        The return value is a list of list. Which means:
        [[ratio1, error1, pos1], [ratio2, error2, pos2] ...]
        """
        if self.photoscreen is None:
            return None

        ratio_list = self.photoscreen.find('LWratio').findall('ratio')
        rst = []
        for ratio in ratio_list:
            rst.append([ratio.text, ratio.attrib['error'],
                       ratio.attrib['pos']])

        return rst


def parse_xml_to_etree(xml_str):
    """This function parse the given xml string to etree object
    """
    try:
        etree_obj = et.fromstring(xml_str)
    except et.ParseError:
        # Try to ignore the error
        parser = etree.XMLParser(recover=True)
        etree_obj = et.fromstring(xml_str, parser=parser)

    return etree_obj


def parse_classifier_xml(config):
    """This function load the classifier xml file and parse the content
    a dict will be returned. The key is the int class number: 0~N
    the corresponding val is a list: [min_focal, max_focal]. e.g.
    {0: [10. 24], 1: [35, 50]. 2: [100. 200]}
    NOTE: All return values are int type

    If error, return None
    """
    try:
        root = et.parse(config).getroot()
    except:
        log.error('%s can not be parsed' % config)
        return None
    try:
        classes = root.findall('class')
    except:
        log.error('Can not find class section in %s' % config)
        return None
    rst = {}
    for cl in classes:
        try:
            class_id = int(cl.get('id'))
            class_min_focal = int(cl.get('minfocal'))
            class_max_focal = int(cl.get('maxfocal'))
            if class_max_focal < class_min_focal:
                log.warn('maxfocal must larger than minfocal in %s' %
                         et.tostring(cl))
        except:
            log.error('Error in parsing %s' % et.tostring(cl))
            return None
        rst[class_id] = [class_min_focal, class_max_focal]
    return rst
