import cv2

class Preprocessor:

    def __init__(self):
        self.face_haar_file = "config/haarcascade_frontalface_alt.xml"
        self._initialize_haar_classifiers()

    def _initialize_haar_classifiers(self):
        self.face_classifier = cv2.CascadeClassifier()
        self.face_classifier.load(self.face_haar_file)

    def _get_faces(self, img):
        '''
        Using trained face classifier find out all faces in the image
        '''
        faces = self.face_classifier.detectMultiScale(img, 1.2, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (50, 50))
        if len(faces) == 0:
            return []
        return faces

    def remove_faces(self, img, color=(0, 0, 0)):
        '''
        Blacken out the faces in the image
        '''
        faces = self._get_faces(img)
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), color, cv2.cv.CV_FILLED)

    def process(self, img):
        self.remove_faces(img)

