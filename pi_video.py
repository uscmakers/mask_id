from threading import Thread
import cv2
import imutils

class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True

class VideoGetAndShow:
    """
    Class that continuously gets and shows frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self):
        self.video_getter = VideoGet(0).start()
        self.video_shower = VideoShow(self.video_getter.frame).start()
        self.frame = self.video_getter.frame
        self.stopped = False

    def start(self):    
        Thread(target=self.getAndShow, args=()).start()
        return self

    def getAndShow(self):
        while not self.stopped:
            self.frame = self.video_getter.frame
            # frame = putIterationsPerSec(frame, cps.countsPerSec())
            self.video_shower.frame = self.frame

    def getFrame(self):
        return self.frame

    def stop(self):
        self.stopped = True
