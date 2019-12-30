from PIL import ImageFont

import numpy as np

CAP_SIZE = (1280,720)

FONT = ImageFont.truetype(font='fonts/dos.ttf', size=16)

# Non maximum suppression from
# https://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/.
def nms(boxes, threshold):
    if len(boxes) == 0:
        return []

    # Convert to float.
    if boxes.dtype.kind == 'i':
        boxes = boxes.astype('float')

    # Initialize the pick indices.
    pick = []

    # Get the bounding box coordinates.
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]

    # Compute the areas and sort by bottom right y coordinate.
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # Choose indices.
    while len(idxs) > 0:
        # Pick the last index.
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # Find the largest start and smallest end for the bounding box.
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # Compute the size of the bounding box.
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # Compute the overlap ratio.
        overlap = (w * h) / area[idxs[:last]]

        # Remove all indices that overlap.
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > threshold)[0])))

    # Return the bounding boxes that were picked.
    return boxes[pick].astype('int')
