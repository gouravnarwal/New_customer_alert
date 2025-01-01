import cv2
import os
import time
import glob
from emailing import send_email
from threading import Thread#threads are used to keep the threads of programm ready to use

video = cv2.VideoCapture(0)
time.sleep(1)

#video.read() takes two variables because it returns two values one as camera captured or not another is what it captured

count = 1
first_frame=None
status_list=[]

def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)

while True:
    status = 0
    check,frame = video.read()
    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_frame_blur = cv2.GaussianBlur(gray_frame,(21,21),0)

    if first_frame is None:
        first_frame=gray_frame_blur

    delta_frame=cv2.absdiff(first_frame,gray_frame_blur)

    thresh_frame=cv2.threshold(delta_frame,60,255,cv2.THRESH_BINARY)[1]#the pixels below 60 will become zero and above become255.binary makes them below as 0 and above as 1
    dil_frame = cv2.dilate(thresh_frame,None,iterations=2)
    

    contours,check = cv2.findContours(dil_frame,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 20000:
            continue
        x,y,w,h = cv2.boundingRect(contour)#x,y,w,h are the x cordinates,y cordinates,w:width,h:height
        rectangle=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

        if rectangle.any():
            status=1
            cv2.imwrite(f"images/{count}.png",frame)
            count = count+1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images)/2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list=status_list[-2:]

    if status_list[0]==1 and status_list[1]==0:
        email_thread = Thread(target=send_email,args=(image_with_object, ))#The comma in (image_with_object, ) ensures that args is correctly interpreted as a tuple with one element, which is required by the Thread constructor. Without the comma, it would not work as intended.
        email_thread.start() #threading is used to keep a function ready to use for example the send_email function and args passes the arguement
        email_thread.join()#it means the below code only will start after this process is complete
        clean_thread = Thread(target=clean_folder)
        clean_thread.start()


    print(status_list)

    cv2.imshow("video",frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break


video.release()#it will release the camera of pc

