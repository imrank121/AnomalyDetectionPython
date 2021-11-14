import sys
import cv2
import os
import numpy as num

#Adapted from Threshholding 'experiments' script
def getcontours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    (t, binary) = cv2.threshold(blur, 1, 255, cv2.THRESH_BINARY)
    # Find contours.
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (0, 0, 255), 5)
    cv2.namedWindow(sys.argv[0], cv2.WINDOW_NORMAL)
    ny, nx, nc = img.shape
    cv2.resizeWindow(sys.argv[0], nx // 2, ny // 2)
    cv2.imshow(sys.argv[0], img)

    return contours


def findcolours(img_left,img_right,masks):
#Find mask ranges from generate masks within frames
    hsv_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2HSV)
    hsv_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2HSV)
#Converting to HSV so mask ranges can be applied
    for mask in masks.items():
        colour = mask[0]
        m_left = cv2.inRange(hsv_left,mask[1][0],mask[1][1])
        m_right = cv2.inRange(hsv_right, mask[1][0], mask[1][1])

        res_left = cv2.bitwise_and(img_left, img_left, mask=m_left)
        res_right = cv2.bitwise_and(img_right, img_right, mask=m_right)

        cont_left = getcontours(res_left)
        cont_right = getcontours(res_right)
        #Applying contours to left and right frames
        getcentre(cont_left,"left",colour)
        getcentre(cont_right,"right",colour)
        #Retrieving centre value of each contour



def generateMasks():
    #Generating HSV ranges for masking using colour as a key in dict masks
    masks = {}
    low_red = num.array([0, 50, 20])
    high_red = num.array([10, 255, 255])
    masks["red"] = (low_red,high_red)

    low_blue = num.array([105, 0, 20])
    high_blue = num.array([123, 255, 255])
    masks["blue"] = (low_blue, high_blue)

    low_yellow = num.array([25, 100, 3])
    high_yellow = num.array([30, 255, 255])
    masks["yellow"] = (low_yellow, high_yellow)

    low_green = num.array([40, 60, 72])
    high_green = num.array([62, 255, 255])
    masks["green"] = (low_green, high_green)

    low_white = num.array([0, 0, 200])
    high_white = num.array([255, 0, 255])
    masks["white"] = (low_white, high_white)

    low_orange = num.array([12, 100, 20])
    high_orange = num.array([24, 255, 255])
    masks["orange"] = (low_orange, high_orange)

    low_cyan = num.array([87, 0, 0])
    high_cyan = num.array([94, 255, 255])
    masks["cyan"] = (low_cyan, high_cyan)

    return masks

coordinates = {
        "blue":{"left":(),"right":()},"red": {"left": (), "right": ()},
        "green": {"left": (), "right": ()},"white": {"left": (), "right": ()},
        "orange": {"left": (), "right": ()},"yellow": {"left": (), "right": ()},
        "cyan": {"left": (), "right": ()}
                   }

def getcentre(cont,side,colour):
    #Adapted from https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    if len(cont) == 0:
        coordinates[colour][side] += ((5000, 5000),)
        return
    for c in cont:

        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        coordinates[colour][side] += ((cX,cY),)

    return coordinates

def findistance():
    #Adapted from ALL THE NOTES - CHAPTER9. VISIONINA3DWORLD
    print("frame identity distance")
    for x in range (0,49):
        for c in coordinates.keys():
            left = coordinates[c]['left'][x]
            right = coordinates[c]['right'][x]

            if(left[0] == 5000 or right[0] == 5000):
                continue

            currentleft = left[0] - 320
            currentright = right[0] - 320
            #Section 9.5 applied

            calc = (currentleft - currentright)*0.00001
            dist = (12 * 3500) / calc
            print("{:5} {:8} {:8.2e}".format(x,c,dist))
            #Formatting output to scientific notation as per notes

def findangle():
    #Identifying the meteors and objects
    #Function identifies what isnt relaticely moving straight
    anomaly = ()
    #Holds values of left and right angles relative to colour Key
    angles = {
        "blue": {"left": (), "right": ()}, "red": {"left": (), "right": ()},
        "green": {"left": (), "right": ()}, "white": {"left": (), "right": ()},
        "orange": {"left": (), "right": ()}, "yellow": {"left": (), "right": ()},
        "cyan": {"left": (), "right": ()}
    }
    for x in range (1, 49):
        for c in coordinates.keys():
            right = coordinates[c]['right'][x-1]
            new_right = coordinates[c]['right'][x - 1]
            if(right[0] ==5000 or new_right[0] ==5000):
                continue

            if (right[1] == 5000 or new_right[1] == 5000):
                continue

            angles[c]["right"] += ((right[0],right[1],new_right[0],new_right[1]),)

    for c in angles.keys():

        count = 0
        for i in range(1,len(angles[c]["right"])-1):
            current = angles[c]["right"][i]
            last = angles[c]["right"][i-1]
            first = abs(current[0] - last[0])
            second = abs(current[1] - last[1])
            third = abs(current[2] - last[2])
            fourth = abs(current[3] - last[3])

            maxdiff = 8
            if(first>maxdiff or second>maxdiff or third>maxdiff or fourth>maxdiff):
                count+=1

        if(count>5):
             anomaly+=((c),)

    return anomaly


masks = generateMasks()
#Taken from brief
nframes = int (sys.argv[1])
for frame in range (0, nframes):
    fn_left = sys.argv[2] % frame
    fn_right = sys.argv[3] % frame
    img_left = cv2.imread(fn_left)
    img_right = cv2.imread(fn_right)
    findcolours(img_left, img_right, masks)
findistance()
ufo_tracking = ()
print("UFO: " + ",".join(findangle()))



