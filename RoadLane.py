# import matplotlib.pyplot as plt
import cv2
import numpy as np
import winsound

# cap = cv2.VideoCapture(0)

# ip = "http://192.168.1.101:8080/shot.jpg"

def make_coordinates(img, line_parameters):
    slope, intercept = line_parameters
    y1 = img.shape[0]
    y2 = int(y1*(3/5))
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(img, lines):
    left_fit = []
    right_fit = []
    for line in lines: 
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1] 
        if slope > 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    left_line = make_coordinates(img, left_fit_average)
    right_line = make_coordinates(img, right_fit_average)
    return np.array([left_line, right_line])

# pre-processing the frame using canny edge detector
def canny(img):
    # convert the frame into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Apply GaussianBlur to the grayscale frame
    blur = cv2.GaussianBlur(gray, (5 ,5), 0)
    canny = cv2.Canny(blur, 50, 150)
    # return canny
    return canny

def display_lines(img, lines):
    line_img = np.zeros_like(img)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_img, (x1, y1), (x2 ,y2), (255, 0, 0), 10)
    return line_img

def region_of_interest(img):
    height = img.shape[0]
    polygons = np.array([
        [(200, height), (1100, height), (550, 250)]
    ])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, polygons, 255)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

def beep_sound(lines, height, width):
    left_line = lines[0]
    right_line = lines[1]

    # Find the midpoint of the frame
    mid_x = width // 2
    
    # Find the y-coordinate of the lines at the midpoint
    left_y = int((left_line[0]*mid_x + left_line[1])//1)
    right_y = int((right_line[0]*mid_x + right_line[1])//1)

    # If the car is outside the lines, produce a beep sound
    if height < left_y or height < right_y:
        winsound.Beep(frequency=2000, duration=1000)

cap = cv2.VideoCapture("test2.mp4")
while(cap.isOpened()):
    ret, frame = cap.read()
    canny_image = canny(frame)
    cropped_img = region_of_interest(canny_image)
    # detect lines using HoughLine method
    lines = cv2.HoughLinesP(cropped_img, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
    averaged_lines = average_slope_intercept(frame,lines)
    line_img = display_lines(frame, averaged_lines)
    combo_img = cv2.addWeighted(frame, 0.8, line_img, 1, 1)
    cv2.imshow('road', combo_img)
    height, width, _ = frame.shape
    beep_sound(averaged_lines, height, width)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
