import cv2
import os
import numpy as np
import traceback
import time

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
	    blank_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2RGB)
	    image_with_lines = drow_the_lines(blank_image, lines)
	    return image_with_lines
	except:
		traceback.print_exc()
		return image
