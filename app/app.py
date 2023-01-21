from dotenv import load_dotenv
import requests
import logging
import time
import uuid
import cv2
import base64
import json
import os
import socket
load_dotenv()

DEVICE_ID = int(os.getenv('DEVICE_ID'))
INTERVAL = int(os.getenv('INTERVAL'))
INTERVAL_CAPTURE = int(os.getenv('INTERVAL_CAPTURE'))
TMP_DIR = str(os.getenv('TMP_DIR'))
POST_URL = str(os.getenv('POST_URL'))
HOST_NAME = str(socket.gethostname())

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
            post_img_file(POST_URL, path) #Post
            os.remove(path)
            before_img = gray_img.astype("float")
            cnt = 0
            time.sleep(INTERVAL_CAPTURE)
            continue

        if cnt > 100:
            before_img = gray_img.astype("float")
            cnt = 0
            continue

        cnt += 1
        
    capture.release()

def post_img_file(send_url:str, img_file_path:str):
    try:
        with open(img_file_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        #print(img_base64, type(img_base64))
        headers = { "Content-Type": "application/json" }
        data = {"name":"%s" % HOST_NAME,"img_base64": img_base64}
        response = requests.post(send_url, data=json.dumps(data), headers=headers)
        return False
    except:
        return True


def main():
    try:
        os.mkdir(TMP_DIR)
    except:
        pass
    motion_detection()

if __name__ == '__main__':
    main()