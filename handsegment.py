import cv2

class HandSegment:

    def __init__(self, ftype="canny"):
        self.type = ftype

    def _get_pointer_canny(self, frame, x, y, w, h, window):
        # finding out ROI
        new_x = x
        new_w = (7 * w) / 6
        new_y = max(y-int(3*h/4.0), 0)
        new_h = y + int(3*h/4.0) - new_y
        target = frame[new_y:new_y+new_h, new_x:new_x+new_w]
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

        # Finding out canny edges
        canny_img = cv2.Canny(target_gray, 100, 200)
        contours, hierarchy = cv2.findContours(canny_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_img = cv2.cvtColor(target_gray, cv2.COLOR_GRAY2BGR)

        # cv2.drawContours(contours_img, contours, -1, (0, 0, 255), 1)
        # Finding finger tip
        top_cnt = []
        rects = []
        min_y = 100000
        for cnt in contours:
            (rectx, recty, rectw, recth) = cv2.boundingRect(cnt)
            if recty < min_y:
                top_cnt = cnt
        rects.append(cv2.boundingRect(top_cnt))

        # Drawing rectangle
        for rect in rects:
            x, y, w, h = rect
            cv2.rectangle(contours_img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow(window, contours_img)

        return x, y

    def _get_pointer_color(self, frame, x, y, w, h, window):
        # Getting hand model
        hand_model = frame[y+h/4:y+3*h/4, x+w/4:x+3*w/4]
        cv2.imshow("hand model", hand_model)
        handmodel_hsv = cv2.cvtColor(hand_model, cv2.COLOR_BGR2HSV)
        handmodel_hist = cv2.calcHist([handmodel_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(handmodel_hist, handmodel_hist, 0, 255, cv2.NORM_MINMAX)

        # Finding out target region
        new_x = x
        new_w = (5 * w) / 4
        new_y = max(y-h, 0)
        new_h = y + int(3*h/4.0) - new_y
        target = frame[new_y:new_y+new_h, new_x:new_x+new_w]
        target_hsv = cv2.cvtColor(target, cv2.COLOR_BGR2HSV)

        #
        dst = cv2.calcBackProject([target_hsv], [0, 1], handmodel_hist, [0, 180, 0, 256], 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cv2.filter2D(dst, -1, disc, dst)
        ret, threshold = cv2.threshold(dst, 50, 255, 0)
        tres = threshold.copy()
        threshold = cv2.merge((threshold, threshold, threshold))


        kernel = np.ones((6, 6), np.uint8)
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        # cv2.imshow("threshold", threshold)
        result = cv2.bitwise_and(target, threshold)

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

        # cv2.imshow(window, result)
        return x, y

    def get_pointer(self, frame, x, y, w, h, window="threshold"):
        '''
        Helper function for finding out pointer
        '''
        if self.type == "canny":
            return self._get_pointer_canny(frame, x, y, w, h, window)
        else:
            return self._get_pointer_color(frame, x, y, w, h, window)