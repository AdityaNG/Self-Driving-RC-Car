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

data = open("data.csv", "r")
#data = open("new_data.csv", "r")
data = data.read()

data_imagefile, steering_angle, speed, throttle, brakes = list(range(5))

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

def drow_the_lines(img, lines):
    img = np.copy(img)
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(blank_image, (x1,y1), (x2,y2), (0, 255, 0), thickness=10)

    img = cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)
    return img

# = cv2.imread('road.jpg')
#image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
def process(image):
	try:
	    #print(image.shape)
	    height = image.shape[0]
	    width = image.shape[1]
	    region_of_interest_vertices = [
	        (0, height),
	        (0, 300),
	        (width-20, 300),
	        (width-20, height)
	    ]
	    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	    canny_image = cv2.Canny(gray_image, 60, 80)
	    cropped_image = region_of_interest(canny_image,
	                    np.array([region_of_interest_vertices], np.int32),)
	    return canny_image
	    lines = cv2.HoughLinesP(cropped_image,
	                            rho=2,
	                            theta=np.pi/180,
	                            threshold=50,
	                            lines=np.array([]),
	                            minLineLength=40,
	                            maxLineGap=100)
	    image_with_lines = drow_the_lines(image, lines)
	    return image_with_lines
	except:
		print("err")
		return image

while True:
	for line in data.split('\n'):
		if line:
			instance = line.split(",")
			print(instance[data_imagefile])
			
			#myCsvRow = ",".join(list(map(str, [IMAGES[0], instance[steering_angle], instance[speed], instance[throttle], instance[brakes]])))
			#IMAGES.pop(0)
			#with open('new_data.csv', 'a') as fd: # Append to file
			#	fd.write(myCsvRow + '\n')
			
			img = cv2.imread(instance[data_imagefile])
			img = process(img)
			img = cv2.putText(img, 'steering_angle ' + instance[steering_angle], (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE) 
			img = cv2.putText(img, 'throttle       ' + instance[throttle], (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE) 
			cv2.imshow('vid', img)
			#cv2.waitKey(0) # waits until a key is pressed
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break

cv2.destroyAllWindows() # destroys the window showing image
