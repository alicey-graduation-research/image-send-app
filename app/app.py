from dotenv import load_dotenv
import requests
import logging
import time
import uuid
import cv2
load_dotenv()

DEVICE_ID = 2
INTERVAL = 2
INTERVAL_2 = 2
TMP_DIR = './tmp'

def get_image(path:str) -> str:
    capture = cv2.VideoCapture(DEVICE_ID)
    time.sleep(2)
    ret, frame = capture.read()
    cv2.imwrite(path, frame)
    capture.release()
    return path

def motion_detection(threshold=200):
    capture = cv2.VideoCapture(DEVICE_ID)
    cnt = 0
    time.sleep(2)
    before_img = None

    while True:
        print(cnt)
        ret, frame = capture.read()
        if ret == False:
            break

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if before_img is None:
            before_img = gray_img.astype("float")
            continue

        cv2.accumulateWeighted(gray_img, before_img, 0.5)
        frameDelta = cv2.absdiff(gray_img, cv2.convertScaleAbs(before_img))
        thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(thresh,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)[0]

        detection = False
        for target in contours:
            x, y, w, h = cv2.boundingRect(target)
            if w > threshold:
                detection = True
                break

        if detection:
            path = f"{TMP_DIR}/{uuid.uuid4()}.png"
            cv2.imwrite(path, frame)
            before_img = gray_img.astype("float")
            cnt = 0
            time.sleep(INTERVAL_2)
            continue

        if cnt > 100:
            before_img = gray_img.astype("float")
            cnt = 0
            continue

        cnt += 1
        
    capture.release()



def main():
    motion_detection()


if __name__ == '__main__':
    main()