import numpy as np
import cv2
from pykeyboardas import PyKeyboard
from preprocessor import Preprocessor
from handsegment import HandSegment
import math
import sys

keyboard = PyKeyboard()

class HandDetection:

    def __init__(self):
        self.hand_haar_file = "config/haarcascade_hand_alt.xml"
        # self.hand_haar_file = "../config/palm.xml"
        self._initialize_haar_classifiers()

    def _initialize_haar_classifiers(self):
        self.hand_classifier = cv2.CascadeClassifier()
        self.hand_classifier.load(self.hand_haar_file)
        # print "Initialized HAAR Classifiers"

    def get_hands(self, img, gray = False):
        '''
        Get all hands in the frame as found by a haar classifier
        '''
        if gray is True:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_gray = cv2.equalizeHist(img_gray)
            hands = self.hand_classifier.detectMultiScale(img_gray, 1.2, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
        else:
            hands = self.hand_classifier.detectMultiScale(img, 1.2, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
            if len(hands) == 0:
                return []
        return hands

    def get_biggest_hand(self, img, prev_x, prev_y, prev_w, prev_h):
        '''
        find out the biggest hand by area among
        all the hands found out

        '''
        hands = []
        # Search in vicinity provided hand previously found
        if prev_w != 0 and prev_h != 0:
            new_x = max(prev_x - prev_w/4, 0)
            new_y = max(prev_y - prev_h/4, 0)
            new_w = (3 * prev_w) / 2
            new_h = (3 * prev_h) / 2
            temp = img[new_y:new_y+new_h, new_x:new_x+new_w]
            # print temp
            hands = self.get_hands(temp)
            if len(hands) > 0:
                hands = [[new_x+x, new_y+y, w, h] for x, y, w, h in hands]
            else:
                hands = []
        # Search the entire image for hands
        if hands == []:
            hands = self.get_hands(img)
            if len(hands) == 0:
                return []
        maxArea = 0
        maxHand = []
        for x, y, w, h in hands:
            if w*h > maxArea:
                maxHand = [x, y, w, h]
        return maxHand

    def motion(self, positions, hand_width, hand_height):
        '''
        Find which motion has taken place
        '''
        max_window_size = 7
        min_window_size = 6
        # window_size = 6
        tolerance = 2
        if len(positions) < 4 * max_window_size / 3:
            return 0
        if len(positions) > max_window_size * 2:
            positions.pop(0)
        for window_size in range(max_window_size, min_window_size, -1):
            num_presses = ( max_window_size - min_window_size ) * 2 + 1
            for start in range(0, len(positions) - window_size + 1):
                # line fitting the x, y co-ordinates
                end = start+window_size
                positions_interest = positions[start:end]
                if positions_interest.count([-1, -1]) <= tolerance:
                    # Fit x co-ordinates
                    positionsx = np.array([x for x, y in positions_interest if x != -1 and y != -1])
                    # Fit y co-ordinates
                    positionsy = np.array([480 - y for x, y in positions_interest if x != -1 and y != -1])
                    base = range(0, len(positionsx))
                    fitx = np.polyfit(base, positionsx, 1)
                    fity = np.polyfit(base, positionsy, 1)
                    fitxy = np.polyfit(positionsx, positionsy, 1)
                    # print "x: ", positionsx
                    # print "y: ", positionsy
                    # print "x:", fitx, " y: ", fity, " xy: ", fitxy
                    # print "x: ", fitx[1], " y: ", fity[1], " xy: ", fitxy[1]
                    flag = False
                    # If
                    if math.fabs(fity[0]) < 0.75 and math.fabs(fitx[0]) > 1.5:
                        if math.fabs(positionsx[0] - positionsx[len(positionsx)-1]) > (3 * hand_width / 4):
                            num_presses = 1
                            flag = True
                            print "HORIZONTAL ",
                            if fitx[0] < 0:
                                print "RIGHTWARD"
                                keyboard.tap_key(keyboard.right_key, num_presses)
                            else:
                                print "LEFTWARD"
                                keyboard.tap_key(keyboard.left_key, num_presses)
                    elif math.fabs(fitx[0]) < 1 and math.fabs(fity[0]) > 1.5:
                        if math.fabs(positionsy[0] - positionsy[len(positionsy)-1]) > (2 * hand_height / 4):
                            num_presses = 1
                            flag = True
                            print "VERTICAL ",
                            if fity[0] < 0:
                                print "DOWNWARD"
                                keyboard.tap_key(keyboard.down_key, num_presses)
                            else:
                                print "UPWARD"
                                keyboard.tap_key(keyboard.up_key, num_presses)
                    if flag == True:
                        del positions[:]
                        return 2
        return 0

    def get_frame(self, cam):
        '''
        Get frame from video source
        accounts for delays in frame processing
        also skips frames on request

        @return frame if found
                else None
        '''
        retval, frame = cam.read()
        if type(frame) == type(None):
            print "frame not captured"
            return
        self.count += 1
        if (self.count % 9 == 0) or (self.skip_frames > 0):
            self.skip_frames = self.skip_frames - 1
            self.count = self.count % 9
            return
        return frame

    def _draw_motion(self, frame, positions):
        '''
        Plot the motion of the hand as per positions of hand
        Draws a line over the positions

        @return None
        '''
        if len(positions) != 0:
            temp = [[x, y] for x, y in positions if x > -1 and y > -1]
            temp = np.array([temp])
            if len(temp[0]) != 0:
                cv2.polylines(frame, [temp], 0, (255, 0, 0))


    def find_hand(self, frame, prev):

        # Preparing ROI
        x, y, w, h = increase_locality(prev)
        # Get localised ROI
        target = frame[y:y+h, x:x+w]
        cv2.imshow("target", target)
        target_hsv = cv2.cvtColor(target, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([target_hsv], [0, 1], handmodel_hist, [0, 180, 0, 256], 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cv2.filter2D(dst, -1, disc, dst)
        ret, threshold = cv2.threshold(dst, 50, 255, 0)
        tres = threshold.copy()
        threshold = cv2.merge((threshold, threshold, threshold))
        # kernel = np.ones((4, 4), np.uint8)
        # threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        kernel = np.ones((7, 7), np.uint8)
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        cv2.imshow("threshold", threshold)

        result = cv2.bitwise_and(target, threshold)

        #Finding contours
        contours, hierarchy = cv2.findContours(tres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        maxcnta = 0
        maxcnt = 0
        for i in range(0, len(contours)):
            area = cv2.contourArea(contours[i])
            if area > maxcnta:
                maxcnta = area
                maxcnt = i

        for i in range(0, len(contours)):
            if i != maxcnt:
                cv2.fillPoly(result, [contours[i]], (0, 0, 0))

        # BOunding Rectangle
        if maxcnt < len(contours):
            x, y, w, h = cv2.boundingRect(contours[maxcnt])
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.imshow("result", result)
            return x, y, w, h

        cv2.imshow("result", result)

        # return x, y, w, h
        return []

    def _initialize_windows(self):
        cv2.namedWindow("display", cv2.CV_WINDOW_AUTOSIZE)
        # cv2.namedWindow("pointer", cv2.CV_WINDOW_AUTOSIZE)
        cv2.namedWindow("threshold", cv2.CV_WINDOW_AUTOSIZE)
        cv2.moveWindow('threshold', 900, 0)
        # cv2.namedWindow("hand model", cv2.CV_WINDOW_AUTOSIZE)
        # cv2.moveWindow("hand model", 900, 0)
        #

    def track(self):
        print sys.argv
        cam = cv2.VideoCapture(int(sys.argv[1]))
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
        self._initialize_windows()

        p = Preprocessor()
        hs = HandSegment()

        positions = []
        self.count = 0
        self.skip_frames = 0
        x, y, w, h = 0, 0, 0, 0
        prev_x, prev_y, prev_w, prev_h = 0, 0, 0, 0
        while True:
            frame = self.get_frame(cam)
            if type(frame) == type(None):
                continue
            p.process(frame)


            hand = self.get_biggest_hand(frame, prev_x, prev_y, prev_w, prev_h)
            # print hand
            if not hand == []:
                x, y, w, h = hand
                prev_x, prev_y, prev_w, prev_h = hand
                centerx = x + w / 2
                centery = y + h / 2
                # Drawing rectangle around the hand
                cv2.rectangle(frame, (x, y), (x+w, y+w), (0, 0, 0), 1)

                # pointerx, pointery = hs.get_pointer(frame, x, y, w, h)

                # cv2.imshow("pointer", frame[max(y-h, 0):y+h, x:x+w+w/4])
            else:
                x, y, w, h = -1, -1, prev_w, prev_h
                centerx = -1
                centery = -1
            positions.append([centerx, centery])
            # Action
            skip_frames = self.motion(positions, w, h)
            # Drawing line of motion
            self._draw_motion(frame, positions)
            cv2.imshow("display", frame)


            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    x = HandDetection()
    x.track()
