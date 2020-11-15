from threading import Thread
import cv2

class VideoGetAndShow:
    """
    Class that continuously gets and shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.getAndShow, args=()).start()
        return self

    def getAndShow(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if (self.grabbed):
                    cv2.imshow("Video", self.frame)

    def stop(self):
        self.stopped = True