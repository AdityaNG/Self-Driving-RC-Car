"""
	Place this file within the generatd data folder

	data_folder/
		- data.csv
		- player.py 	<== Like such
		- images/
			- 1589202544.57268.jpg
			- 1589202545.33127.jpg
			...
			- 1589203451.23581.jpg
"""

import cv2
import os
import numpy as np
import traceback
import time
import math

data = open("data.csv", "r")
#data = open("new_data.csv", "r")
data = data.read()

data_imagefile, steering_angle, speed, throttle, brakes = list(range(5))
throttle = speed
brakes = speed

IMAGES = os.listdir('images')
IMAGES.sort()

BLUE = (255, 0, 0) 


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    #channel_count = img.shape[2]
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def sigmoid(x):
  return 1 / (1 + math.exp(-x))


def drow_the_lines(img, lines):
    img = np.copy(img)
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    total_angle = 0
    no_of_angle = 0
    if lines is not None:
        
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(blank_image, (x1,y1), (x2,y2), (0, 255, 0), thickness=10)


        for line in lines:
            for x1, y1, x2, y2 in line:
                if abs(x2-x1) >0.01:
                    t = math.atan(float(y2-y1)/float(x2-x1))
                    if abs(t) * 180/math.pi > 0: # 10 Degrees
                        total_angle += t
                        no_of_angle += 1

    avg_angle = 0
    if no_of_angle!=0:
        avg_angle = total_angle/no_of_angle
    old = avg_angle
    #avg_angle = sigmoid(avg_angle) * math.pi *2 - math.pi
    avg_angle *= -1

    if abs(round(avg_angle * 180/math.pi)) * 3 >5:
        #avg_angle *= 3
        avg_angle = 20 * math.pi / 180 * avg_angle/abs(avg_angle) + avg_angle * 3
    
    #print(round(old * 180/math.pi), "=>" , round(avg_angle * 180/math.pi))
    p_angle = avg_angle * 180/math.pi
    p_angle = p_angle / 60
    #if abs(p_angle)>0.5:
    #    p_angle = 1 * p_angle/abs(p_angle)
    #else:
    #    p_angle = 0
        
    #print(p_angle)
    x1, y1 = img.shape[1]//2, img.shape[0]//2 # Center of image
    r = math.sqrt(x1**2 + y1**2)/4
    x2, y2 = int(x1 + r*math.cos(avg_angle)), int(y1 + r*math.sin(avg_angle))
    cv2.line(blank_image, (x1,y1), (x2,y2), (255, 0, 0), thickness=10)
    x2, y2 = int(x1 - r*math.cos(avg_angle)), int(y1 - r*math.sin(avg_angle))
    cv2.line(blank_image, (x1,y1), (x2,y2), (255, 0, 0), thickness=10)
    x2, y2 = int(x1 - r*math.cos(avg_angle - math.pi/2)), int(y1 - r*math.sin(avg_angle - math.pi/2))
    cv2.line(blank_image, (x1,y1), (x2,y2), (255, 0, 0), thickness=10)

    cv2.circle(blank_image, (x1,y1), int(r), (255, 0, 0), thickness=10)

    img = cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)
    return img, p_angle

# = cv2.imread('road.jpg')
#image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
def process(image):
	try:
	    #print(image.shape)
	    height = image.shape[0]
	    width = image.shape[1]
	    region_of_interest_vertices = [
	        (0, 380),
	        (0, 260),
	        (width-20, 260),
	        (width-20, 380)
	    ]
	    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	    canny_image = cv2.Canny(gray_image, 60, 80)
	    cropped_image = region_of_interest(canny_image,
	                    np.array([region_of_interest_vertices], np.int32),)
	    #return canny_image
	    lines = cv2.HoughLinesP(cropped_image,
	                            rho=2,
	                            theta=np.pi/180,
	                            threshold=50,
	                            lines=np.array([]),
	                            minLineLength=40,
	                            maxLineGap=100)
	    #image_with_lines = drow_the_lines(image, lines)

	    blank_image = np.zeros((height,width,3), np.uint8)
	    blank_image = image
	    #blank_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2RGB)
	    image_with_lines, p_angle = drow_the_lines(blank_image, lines)
	    return image_with_lines, p_angle
	except:
		traceback.print_exc()
		return image, 0

while True:
	for line in data.split('\n'):
		if line:
			instance = line.split(",")
			#print(instance[data_imagefile])
			
			#myCsvRow = ",".join(list(map(str, [IMAGES[0], instance[steering_angle], instance[speed], instance[throttle], instance[brakes]])))
			#IMAGES.pop(0)
			#with open('new_data.csv', 'a') as fd: # Append to file
			#	fd.write(myCsvRow + '\n')

			filename = instance[data_imagefile].split("/")[1]
			current_frame = filename.split(".")[0] + "." + filename.split(".")[1][:3]
			
			img = cv2.imread(instance[data_imagefile])
			#img = cv2.flip(img, 1)
			img, p_angle = process(img)
			img = cv2.putText(img, 'steering_angle ' + instance[steering_angle], (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE)
			img = cv2.putText(img, 'steering_error ' + str(round(float(instance[steering_angle]) - p_angle, 3)), (220,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255)) 
			img = cv2.putText(img, 'throttle       ' + instance[throttle], (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE) 
			img = cv2.putText(img, 'time           ' + current_frame, (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE) 
			if np.array(img).any():
				if img.shape[0]>0 and img.shape[1]>0:
					cv2.imshow('player.py', img)
					#cv2.waitKey(0) # waits until a key is pressed
					if cv2.waitKey(25) & 0xFF == ord('q'):
						break
					time.sleep(0.05)

cv2.destroyAllWindows() # destroys the window showing image
