import numpy as np
import cv2
import uinput

class HandDetection:

    def __init__(self):
        self.face_haar_file = "../config/haarcascade_frontalface_alt.xml"
        self.hand_haar_file = "../config/haarcascade_hand_alt.xml"
        self.device = uinput.Device([uinput.REL_X, uinput.REL_Y, uinput.BTN_LEFT, uinput.BTN_RIGHT])
        self._initialize_haar_classifiers()

    def _initialize_haar_classifiers(self):
        self.hand_classifier = cv2.CascadeClassifier()
        self.face_classifier = cv2.CascadeClassifier()
        self.hand_classifier.load(self.hand_haar_file)
        self.face_classifier.load(self.face_haar_file)
        print "Initialized HAAR Classifiers"

    def _get_faces(self, img):
        faces = self.face_classifier.detectMultiScale(img, 1.1, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
        if len(faces) == 0:
            return []
        return faces

    def remove_faces(self, img, color=(0, 0, 0)):
        faces = self._get_faces(img)
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), color, cv2.cv.CV_FILLED)

    def get_hands(self, img, gray = False):
        if gray == True:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_gray = cv2.equalizeHist(img_gray)
            hands = self.hand_classifier.detectMultiScale(img_gray, 1.1, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
        else:
            hands = self.hand_classifier.detectMultiScale(img, 1.1, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
            if len(hands) == 0:
                return []
        return hands

    def get_biggest_hand(self, img):
        hands = self.get_hands(img)
        if len(hands) == 0:
            return []
        maxArea = 0
        maxHand = []
        for x, y, w, h in hands:
            if w*h > maxArea:
                maxHand = [x, y, w, h]
        return maxHand

    def detect_biggest_hand(self, img):
        hand = get_biggest_hand(img)
        if len(hand) == 0:
            return
        x, y, w, h = hand
        # drawing rectangle aroung the biggest hand
        cv2.rectangle(img, (x, y), (x+w, y+w), (0, 0, 0), 1)

    def move_pointer(self, previous_position, current_position, frame):
        # 4 * hand_width = full_screen
        # 3 * hand_height = full_screen
        frame_width = len(frame[0])
        frame_height = len(frame)
        screen_width = 1600
        screen_height = 900
        prevx, prevy, prevw, prevh = previous_position
        curx, cury, curw, curh     = current_position
        dispx = int (((curx - prevx) * screen_width) / (4 * curw))
        dispy = int (((cury - prevy) * screen_height) / (3 * curh))
        self.device.emit(uinput.REL_X, -1 * dispx)
        self.device.emit(uinput.REL_Y, dispy)
        print dispx, dispy, "displacements"

    def track(self):
        cam = cv2.VideoCapture(0)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
        cv2.namedWindow("display", cv2.CV_WINDOW_AUTOSIZE)

        result = False
        current_state = "none"
        previous_state = "none"
        current_position = []
        previous_position = []
        det_count = 0

        while True:
            retval, frame = cam.read()
            if (type(frame) == type(None)):
                print "frame not captured"
                continue

            self.remove_faces(frame)
            hand = self.get_biggest_hand(frame)
            if hand != []:
                result = True
            else:
                result = False
            if current_state == "none":
                if result == True:
                    previous_state = current_state
                    current_state = "detecting"
                    current_position = hand
                    det_count = 1
                    print "none      -> detecting"
                else:
                    previous_state = current_state
                    current_state = "none"
                    print "none      -> none"
            elif current_state == "detecting":
                if result == True:
                    det_count += 1
                    previous_state = current_state
                    current_state = "detecting"
                    if det_count > 5:
                        current_state = "detected"
                        previous_position = current_position
                        current_position = hand
                        self.move_pointer(previous_position, current_position, frame)
                    print "detecting -> detected"
                else:
                    det_count = 0
                    previous_state = current_state
                    current_state = "none"
                    print "detecting -> none"
            elif current_state == "detected":
                if result == True:
                    previous_state = current_state
                    current_state = "detected"
                    previous_position = current_position
                    current_position = hand
                    self.move_pointer(previous_position, current_position, frame)
                    print "detected  -> detected"
                else:
                    previous_state = current_state
                    current_state = "none"
                    print "detected  -> none"

            if hand != []:
                x, y, w, h = hand
                cv2.rectangle(frame, (x, y), (x+w, y+w), (0, 0, 0), 1)
            cv2.imshow("display", frame)

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    x = HandDetection()
    x.track()
