import cv2
import numpy as np
import argparse
import time

def cucaracha(x):
    pass


def findMaxCountour(contours):
    sorted(cnts, key = cv2.contourArea, reverse = True)

    for i in contours:
        area = cv2.contourArea(i)
        peri = cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, 0.02 * peri, True)

        if len(approx) == 4 and area > 4000:
            return approx, area
    
    return np.array([]), 0


def orderPoints(points):
    points = points.reshape((4, 2))
    pointsOrdered = np.zeros((4, 2), dtype = 'float32')

    s = points.sum(axis = 1)
    pointsOrdered[0] = points[np.argmin(s)]
    pointsOrdered[2] = points[np.argmax(s)]

    diff = np.diff(points, axis = 1)
    pointsOrdered[1] = points[np.argmin(diff)]
    pointsOrdered[3] = points[np.argmax(diff)]

    return pointsOrdered


def getNewDimensions(points):
    (topLeft, topRight, bottomRight, bottomLeft) = points

    # Max distance between top and bottom x-coordinate points distance
    widthA = np.sqrt(((bottomRight[0] - bottomLeft[0]) ** 2) + ((bottomRight[1] - bottomLeft[1]) ** 2))
    widthB = np.sqrt(((topRight[0] - topLeft[0]) ** 2) + ((topRight[1] - topLeft[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Max distance between left and right y-coordinate points distance
    heightA = np.sqrt(((topRight[0] - bottomRight[0]) ** 2) + ((topRight[1] - bottomRight[1]) ** 2))
    heightB = np.sqrt(((topLeft[0] - bottomLeft[0]) ** 2) + ((topLeft[1] - bottomLeft[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    pointsFinal = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype = 'float32')

    return pointsFinal, maxWidth, maxHeight

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = False,
	help = "Path to the image to be scanned")
arguments = vars(ap.parse_args())

W = 640
H = 480
cap = cv2.VideoCapture(0)
cap.set(3, W)
cap.set(4, H)

cv2.namedWindow('Adjust detection')
cv2.resizeWindow('Adjust detection', 640, 240)
cv2.createTrackbar('Threshold 1', 'Adjust detection', 200, 255, cucaracha)
cv2.createTrackbar('Threshold 2', 'Adjust detection', 200, 255, cucaracha)

while True:
    if arguments['image'] == None:
        ret, frame = cap.read()
    else:
        frame = cv2.imread(arguments['image'])

    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frameBlured = cv2.GaussianBlur(frameGray, (5, 5), 0)

    t1 = cv2.getTrackbarPos('Threshold 1', 'Adjust detection')
    t2 = cv2.getTrackbarPos('Threshold 2', 'Adjust detection')

    frameEdge = cv2.Canny(frameBlured, t1, t2)

    frameEdge = cv2.dilate(frameEdge, None, iterations=3)
    frameEdge = cv2.erode(frameEdge, None, iterations=2)

    cnts = cv2.findContours(frameEdge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0]

    frameShow = frame.copy()

    if len(cnts) > 0:
        roi, roiArea = findMaxCountour(cnts)
        
        if roi.size > 0:
            cv2.drawContours(frameShow, roi, -1, (255, 0, 0), 15)

            roi = orderPoints(roi)

            roiFinal, width, height = getNewDimensions(roi)

            transformationMatrix = cv2.getPerspectiveTransform(roi, roiFinal)
            frameWarped = cv2.warpPerspective(frame, transformationMatrix, (width, height))
            retVal, frameBinary = cv2.threshold(frameWarped, 128, 255, cv2.THRESH_BINARY)

            if cv2.waitKey(1) & 0xFF == ord('s'):
                # cv2.imwrite('./Assets/Scanned/ImageNormal.jpg', frameWarped)
                cv2.imwrite('./Assets/Scanned/ImageBin.jpg', frameBinary)
                cv2.imshow('Warped', frameWarped)
                break

    cv2.imshow('Image', frameShow)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()