import numpy as np
import cv2
import time
import imutils
from imutils.video import FileVideoStream, VideoStream


path = 0 # 0 for webcam   
SIZE_WIDTH = 600
SIZE_HEIGHT = 600
COLOR_RED = (0, 0, 255)
TIMER_SETUP = 7
TIMER_POSE = 7
POS_SCREEN = (50, 50)


def get_centroid(bbox):  # center point of rectangle
    x, y, w, h = bbox
    centx = int(x + w // 2)
    centy = int(y + h // 2)
    return (centx, centy)


def get_framecv2(fvs): # reads from cv2
    _, frame = fvs.read()
    if frame is None:
        return None
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=SIZE_WIDTH, height=SIZE_HEIGHT)
    return frame

def get_frame(fvs): # reads from imutils
    frame = fvs.read()
    if frame is None:
        return
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=SIZE_WIDTH, height=SIZE_HEIGHT)
    return frame


def drawbox(ret, bbox, frame):  # draws rectangle from bbox
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)

