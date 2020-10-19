import numpy as np
import cv2
import time

import imutils
from imutils.video import FileVideoStream, VideoStream

from utils import *

# -----Paste the output of Setup.ipynb here (if want to change the default values) ----------------

bbox_body = (200, 95, 100, 100)  # bbox of face
bbox_switch = [(342, 75, 72, 69), (319, 270, 80, 81)] # bbox of switches (0-punch, 1-kick)

# -------------------------------------------------------------------------------------------------


center_point = get_centroid(bbox_body) # center of face
n = len(bbox_switch) # no. of switches
buttons_data = [bbox_body, center_point, n, bbox_switch]
        
THRESH = 1000 # Threshold for a action to be registered. Lower thresh will lead to more pressing of switch.

class Switch():
    
    def __init__(self, bbox_body, bbox_switch=None, THRESH=THRESH):
        self.THRESH = THRESH
        self.last_switch = time.time()        
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))
        self.backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
        
        if bbox_switch: # if bbox already calculated, then use it
            self.bbox = bbox_switch
        else:  # if the region of switch isn't caluculated
            self.setup(bbox_body) # bbox body is the face region.
        

    def setup(self, bbox_body):
        fvs = FileVideoStream(path).start() #vs Video Stream
        TIMER_SETUP = TIMER_POSE # timer for capturing base image, get reading in posture
        t = time.time()

        while True:
            frame = get_frame(fvs)
            if frame is None:
                break
            curr = (time.time() - t)
            if curr > TIMER_SETUP:
                break
            cv2.putText(frame, str(int(TIMER_SETUP - curr)+1), POS_SCREEN, cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_RED, 4)
            drawbox(True, bbox_body, frame)
            cv2.imshow("Setup", frame)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

        cv2.putText(frame, 'Select Region', POS_SCREEN, cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
        self.bbox = cv2.selectROI(frame, False) 
        cv2.destroyAllWindows()
    
    def update(self, frame):
        # Take the switch region of the frame and apply the background subtractor there  
        try: # this is to manage the case, when bbox goes outside frame
            x, y, w, h = self.bbox
            region = frame[y:y+h, x:x+w]
            fgmask = self.backgroundobject.apply(region)            
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_ERODE, self.kernel, iterations = 2)
        except:
            return False
        switch_thresh = np.sum(fgmask==255)
        cv2.putText(frame, str(switch_thresh), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
        drawbox(True, self.bbox, frame)

        if time.time() - self.last_switch < 0.05:
            drawbox(True, self.bbox, frame)
        if switch_thresh>THRESH and time.time() - self.last_switch > 0.2: 
            drawbox(True, self.bbox, frame)
            self.last_switch = time.time()
            return True
        return False
        

class Buttons:
    
    def __init__(self, n=0, bbox_body=(), training=False):
        self.training = training
        if not training: # automatically set the buttons values if not training mode
            self.set_buttons()
        else:
            self.n = n
            self.bbox_switch = []
            self.bbox_body = bbox_body
            self.center_point = get_centroid(self.bbox_body) # center point of face

        self.buttons_bbox_init()
        self.action = Actions(self.center_point) # calling the Actions object

    
    def set_buttons(self):
        self.bbox_body, self.center_point, self.n, self.bbox_switch = buttons_data

    
    def buttons_bbox_init(self): # to setup the regions of action (bbox of switch)
        self.switches = [] # the switch object
        self.bbox_center = [] # the coordinates of bbox of switch wrt to the face
        
        for i in range(self.n):
            if not self.training: # copy the switch data, if already done the setup
                bbox = self.bbox_switch[i]
                s = Switch(self.bbox_body, bbox)
            else: # else, select the region for switch
                s = Switch(self.bbox_body)
                self.bbox_switch.append(s.bbox)
            self.switches.append(s)
            self.bbox_center.append(self.bbox_wrt_center(s.bbox)) #now bbox is wrt origin            
            
        if self.training: # prints the values of bbox of body and switch
            print(f'bbox_body = {self.bbox_body} \nbbox_switch = {self.bbox_switch}')
    
    # Calculates the distance of bbox from center point (face). Then this is used to get new position
    # of switch when the positoin of face changes.
    def bbox_wrt_center(self, bbox):
        center_x, center_y = self.center_point #starting center point, find switch pos, wrt starting bbox
        x, y, w, h = bbox
        dx, dy = x - center_x, y - center_y
        return dx, dy, w, h
    
    # updates to the new position of bbox switch, wrt to face
    def bbox_update(self, bbox):
        curr_x, curr_y = self.curr_center #cetner curr point of body
        dx, dy, w, h = bbox
        x = dx + curr_x
        y = dy + curr_y
        return x, y, w, h
        
    
    def run(self, frame, curr_center):
        self.curr_center = curr_center
        for i in range(self.n):
            s, bbox = self.switches[i], self.bbox_center[i]
            s.bbox = self.bbox_update(bbox)
            pressed = s.update(frame)
            if pressed:
                self.action.press_val(i)
        self.action.action_movement(curr_center)
        
    

from directkeys import *
# import pyautogui

# The Actions to be performed on Virtual key press, will be handled by this.
class Actions():

    def __init__(self, center):
        self.center = center # center of face
        self.thresh_move = 2 
        self.prev = center
        self.mid = center
        self.key_horizontal = None # key for left / right
        self.key_vertical = None # key for up / down
        self.headline = center[1] # horizontal line through face, to track jump and down
        self.delta_vertical = 40 # to jump / down when change is more than delta
        self.delta_horizontal = 10 # same for left / right
        self.val2key = { # mapping the switch index to a certain action in game
            0: O, # using O to High Punch
            1: L, # for High Kick
            2: K # for Power Move
        }

    def press_val(self, val):
        if self.key_horizontal != None:
            return
        
        key = self.val_to_key(val)
        self.press_and_release_key(key)

    def val_to_key(self, val):
        key = self.val2key[val]
        return key

    def press_and_release_key(self, key, cont=False):
        PressKey(key)
        if cont:
            pass # no delay
        else:
            time.sleep(0.07) # min gap btw press and release
            ReleaseKey(key)
        # 0.35 for perfect cont, 0.01 will some cont in many attemps
        time.sleep(0.01) # min gap time for continous press
    
    def action_movement(self, pos):
        self.curr = pos  
        # print(pos)
        # return
        delta_x = self.curr[0] - self.prev[0]
        delta_y = self.curr[1] - self.headline
        
        if abs(self.curr[0] - self.mid[0]) > self.delta_horizontal: # move this from center, then steps will be recorded
            i = 1
            if delta_x > 0:
                i = 2
            for j in range(i):
                self.action_horizontal(delta_x)
            
        if abs(delta_y) > self.delta_vertical:
            self.action_vertical(delta_y)
        
            
        self.prev = pos
            
    def action_horizontal(self, delta):
        
        if abs(delta) < self.thresh_move:
            self.mid = self.curr
            if self.key_horizontal != None:                
                ReleaseKey(self.key_horizontal)
                self.key_horizontal = None
            return
        # elif self.key_horizontal != None:     
        #     return
        # sensitivity = 0.1 #0 - 1
        # n_press = delta * sensitivity
        
        if delta < 0:
            self.key_horizontal = A
        else:
            self.key_horizontal = D
            
        self.press_and_release_key(self.key_horizontal, True)
        

        
    def action_vertical(self, delta):       
        #to release down press
        if delta < 50 and self.key_vertical == S:                
            ReleaseKey(self.key_vertical)
            self.key_vertical= None
            # return
    
        cont = False  
        if delta < 0 and delta < -25:                  
            self.key_vertical= W
        elif delta > 50:
            self.key_vertical= S
            cont = True
        else:
            return
            
        # self.press_and_release_key(self.key_vertical, cont)
        self.press_and_release_key(self.key_vertical, cont)