import util

import cv2
import numpy as np

import multiprocessing as mp

TEMPLATES = [
    ('downloads', 0.01, (1.0,), None),
]

_worker_templates = {}
def _worker_init():
    global _worker_templates

    # Load templates.
    for name, threshold, scales, center in TEMPLATES:
        template = cv2.imread('templates/'+name+'.png', cv2.IMREAD_COLOR)

        # Scale the template.
        imgs = {}
        for scale in scales:
            scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
            scaled_template_gray = cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY)

            imgs[scale] = (scaled_template, scaled_template_gray)

        _worker_templates[name] = (imgs, threshold, center)

def _worker_match(img, template_name, channel):
    global _worker_templates

    if template_name not in _worker_templates:
        return []

    # Store bounding boxes.
    boxes = []

    # Get the template.
    template_images, threshold, center = _worker_templates[template_name]

    for scale, (template_color, template_gray) in template_images.items():
        # Select a channel.
        template = template_gray
        if channel is not None:
            template = template_color[:,:,channel]

        # Find the center.
        w, h = template.shape[::-1]
        scaled_center = None
        if center is None:
            scaled_center = (w//2, h//2)
        else:
            scaled_center = (center[0]*scale, center[1]*scale)

        # Make sure the template is smaller than the image.
        if w >= img.shape[1] or h >= img.shape[0]:
            continue

        # Search for the template.
        res = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED)

        # Threshold the result.
        match_locations = np.where(res<=threshold)

        # Find all locations.
        for (x, y) in zip(match_locations[1], match_locations[0]):
            v = res[y,x]
            x = int(x+scaled_center[0])
            y = int(y+scaled_center[1])

            boxes.append((x-w//2,y-h//2,x+w//2,y+h//2))

    # Run non maximum suppression.
    boxes = util.nms(np.asarray(boxes), 0.0)
    if len(boxes) == 0:
        return []

    # Return the centers of the boxes.
    centers_x = (boxes[:,2] + boxes[:,0]) / 2
    centers_y = (boxes[:,3] + boxes[:,1]) / 2
    centers = list(zip(centers_x, centers_y))

    return centers

class TemplateMatcher:

    def __init__(self):
        # Create a multiprocessing pool.
        self._pool = mp.Pool(initializer=_worker_init)

    def match(self, img, template_name, channel=None, asynchronous=False):
        # Send the job to the pool.
        res = self._pool.apply_async(_worker_match, (img, template_name, channel))

        # If the call is synchronous, wait for the result.
        if not asynchronous:
            return res.get()

        return res
