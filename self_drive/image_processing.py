import cv2
import os
import numpy as np
import traceback
import time
import math
import imutils

BLUE = (255, 0, 0) 


global prev_frames, last_dir, last_dir_pts, last_dir_mag, img1_cache, img2_cache
prev_frames = []
last_dir = []
last_dir_pts = []
last_dir_mag = []
img1_cache = False
img2_cache = False
def get_direction(img_in, history_frames=20, frame_skip=0, scale_percent=10):
	"""
		Returns a touple (x, y) giving the direction of motion and its magnitude
	"""
	global prev_frames, last_dir, last_dir_pts, last_dir_mag, img1_cache, img2_cache

	prev_frames.append(img_in)
	h, w, a = img_in.shape

	if len(prev_frames)>=frame_skip + 2:

		#calculate the 50 percent of original dimensions
		width = int(img_in.shape[1] * scale_percent / 100)
		height = int(img_in.shape[0] * scale_percent / 100)

		# dsize
		dsize = (width, height)

		region_of_interest_vertices = [
			(10, 10),
			(10, height-10),
			(width-10, height-10),
			(width-10, 10)
		]

		img2_cache = prev_frames[0]
		img1_cache = prev_frames[-1]

		prev_frames.pop(0)

		if type(img1_cache)==type(img_in) and type(img2_cache)==type(img_in):
			img1 = cv2.resize(img1_cache, dsize)
			img2 = cv2.resize(img2_cache, dsize)

			height = img1.shape[0]
			width = img1.shape[1]

			img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
			img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

			dir_point = minimize_error(img1, img2, region_of_interest_vertices, width, height)

			img1 = region_of_interest(img1, np.array([region_of_interest_vertices], np.int32),)
			img2 = region_of_interest(img2, np.array([region_of_interest_vertices], np.int32),)
			
			
			th = -math.pi/2
			if dir_point[0]!=0:
				th = math.atan(float(dir_point[1])/dir_point[0])
			
			th = -th

			last_dir.append(th)
			current_dir = sum(last_dir)/len(last_dir)

			if len(last_dir)>history_frames:
				last_dir.remove(last_dir[0])


			
			r = 30 * math.sqrt(dir_point[0]**2 + dir_point[1]**2)


			last_dir_mag.append(r)
			current_dir_mag = sum(last_dir_mag)/len(last_dir_mag)

			if len(last_dir_mag)>history_frames:
				last_dir_mag.remove(last_dir_mag[0])


			last_dir_pts.append(dir_point)
			
			x_dir = 0
			y_dir = 0
			for p in last_dir_pts:
				if p[0]!=0:
					x_dir += p[0] #//abs(p[0])
				if p[1]!=0:
					y_dir += p[1] #//abs(p[1])

			#x_dir = x_dir/len(last_dir_pts)
			#y_dir = y_dir/len(last_dir_pts)

			if len(last_dir_pts)>history_frames:
				last_dir_pts.remove(last_dir_pts[0])

			
			x1 = int(current_dir_mag * math.cos(current_dir))
			y1 = int(current_dir_mag * math.sin(current_dir))

			if x_dir<0:
				x1 = int( - current_dir_mag * math.cos(current_dir))
			
			if y_dir<0:
				y1 = int(- current_dir_mag * math.sin(current_dir))
			return (x1, y1)
	return (0, 0)



def minimize_error(img1, img2, region_of_interest_vertices, width, height):
	img1 = region_of_interest(img1, np.array([region_of_interest_vertices], np.int32),)

	offset_x = 0
	offset_y = 0

	res_img = cv2.subtract(img1, img2)
	min_sum = sum(res_img.flatten())
	original_error = min_sum

	for i in range(-10, 10, 2):
		x = i # x<20
		y = 0 #
		region_of_interest_offset = []

		for p in region_of_interest_vertices:
			point = (p[0] + x, p[1] + y)
			region_of_interest_offset.append(point)

		#print(i, region_of_interest_offset)

		b = region_of_interest(img2, np.array([region_of_interest_offset], np.int32),)

		translation_matrix = np.float32([ [1,0,-x], [0,1,-y] ])
		b = cv2.warpAffine(b, translation_matrix, (width, height))

		tmp_img = cv2.subtract(img1, b)
		
		#cv2.imshow('i=' + str(i), b)
		#cv2.waitKey(0)
		
		res = sum(tmp_img.flatten())
		if res<min_sum:
			min_sum = res
			res_img = tmp_img
			offset_x = x

	res_img = cv2.subtract(img1, img2)
	min_sum = sum(res_img.flatten())
	original_error = min_sum

	for i in range(-10, 10, 2):
		x = 0 # x<20
		y = i #
		region_of_interest_offset = []

		for p in region_of_interest_vertices:
			point = (p[0] + x, p[1] + y)
			region_of_interest_offset.append(point)

		#print(i, region_of_interest_offset)

		b = region_of_interest(img2, np.array([region_of_interest_offset], np.int32),)

		translation_matrix = np.float32([ [1,0,-x], [0,1,-y] ])
		b = cv2.warpAffine(b, translation_matrix, (width, height))

		tmp_img = cv2.subtract(img1, b)
		
		#cv2.imshow('i=' + str(i), b)
		#cv2.waitKey(0)
		
		res = sum(tmp_img.flatten())
		if res<min_sum:
			min_sum = res
			res_img = tmp_img
			offset_y = y

	#offset_x = 0

	region_of_interest_offset = []
	for p in region_of_interest_vertices:
		point = (p[0] + offset_x, p[1] + offset_y)
		region_of_interest_offset.append(point)
	
	b = region_of_interest(img2, np.array([region_of_interest_offset], np.int32),)
	translation_matrix = np.float32([ [1,0, -offset_x], [0,1, -offset_y] ])
	b = cv2.warpAffine(b, translation_matrix, (width, height))
	#res_img = cv2.subtract(img1, b)
	dir_point = (offset_x, offset_y)
	return dir_point

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
	except Exception as e:
		print(e)
		return image
