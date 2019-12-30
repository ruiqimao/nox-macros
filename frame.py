import cv2

class Frame:

    def __init__(self, img, parser):
        self._img = img
        self._gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self._parser = parser

    def crop(self, bounds):
        h, w = self._gray.shape
        x1 = int(max(bounds[0], 0))
        y1 = int(max(bounds[1], 0))
        x2 = int(min(bounds[2], w))
        y2 = int(min(bounds[3], h))

        img = self._img[y1:y2,x1:x2]
        return Frame(img, self._parser)

    def invert(self):
        return Frame(255-self._img, self._parser)

    def threshold_low(self, value):
        img = self._img
        img[self._gray<value] = 0
        return Frame(img, self._parser)

    def threshold_high(self, value):
        img = self._img
        img[self._gray>value] = 255
        return Frame(img, self._parser)

    def pad(self, value):
        img = cv2.copyMakeBorder(self._img, value, value, value, value, cv2.BORDER_REPLICATE)
        return Frame(img, self._parser)

    def scale(self, f):
        img = cv2.resize(self._img, None, fx=f, fy=f)
        return Frame(img, self._parser)

    def count_blobs(self):
        return self._parser.count_blobs(self._gray)

    def match_template(self, template_name, channel=None, asynchronous=False):
        img_channel = self._gray
        if channel is not None:
            img_channel = self._img[:,:,channel]
        return self._parser.match_template(img_channel, template_name, channel, asynchronous)

    def has_template(self, template_name, channel=None):
        return len(self.match_template(template_name, channel)) > 0

    def img(self):
        return self._img

    def gray(self):
        return self._gray

    def parser(self):
        return self._parser

