# USAGE
# python detect_mask_video_test.py
import RPi.GPIO as GPIO  

flag = 0

GPIO.setmode(GPIO.BCM)  
  
# GPIO 23 set up as input. It is pulled up to stop false signals  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
   
# now the program will do nothing until the signal on port 23   
# starts to fall towards zero. This is why we used the pullup  
# to keep the signal high and prevent a false interrupt   

def my_callback(channel):
    print("interrupt detected")
    flag = 1

GPIO.add_event_detect(23, GPIO.RISING, callback=my_callback) 

while True:
    # loop over the frames from the video stream

    if GPIO.input(23) == GPIO.HIGH:
        print("Button pushed!")

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()