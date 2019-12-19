import numpy as np
import cv2

def lp_finder_3(car):
    
    '''Function which returns list of 3 licence plate images, cropped from image of a car.
    Uses template matching, with 3 different template shapes of white rectange with black edges.
    
    Params:
    car - image of a car'''
    

    #changing car image to RGB
    car = cv2.cvtColor(car, cv2.COLOR_BGR2GRAY)
    #resizing to 600x400
    car_r = cv2.resize(car, (600,400))
    #thresholding using Otsu binarization
    car_th = cv2.threshold(car_r, 0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    #getting canny
    car_canny = cv2.Canny(car_th, 200,400)
    
    #3 different lp sizes
    sizes = [(150,56),(187,65),(225,74)]
    
    #creating lp mask - white rectangle with black edges
    lp = np.zeros((56,150), dtype=np.uint8)
    lp = cv2.rectangle(lp, (3,3), (147,53), 255, -1)
    # list of thresholded plates in all sizes
    plates = []
    for i in range(0, len(sizes)):
        plates.append(cv2.resize(lp, sizes[i]))

    #matching car with each LP size
    matches = []
    #list of matches for each size
    for i in plates:
        matches.append(cv2.matchTemplate(car_canny, i, cv2.TM_CCOEFF))
    
    #appends location of matched squares to list, inverted to (x,y), for thresh
    #minMaxLoc finds maximum for each match
    locs = []
    for i in range(0, len(matches)):
        locs.append(tuple(cv2.minMaxLoc(matches[i])[3]))
    
    
    #creates masks for images, where only LP remains
    masks = []
    for i in range(0,len(plates)):
        black = np.zeros(car_r.shape, dtype=np.uint8)
        black = cv2.rectangle(black, locs[i], (locs[i][0]+plates[i].shape[1], locs[i][1]+plates[i].shape[0]), 255, -1)
        masks.append(black)
    
    #keeping only LP - cropped list contains all cropped images of LPs
    cropped = []
    for i in range(0,len(plates)):
        masked = cv2.bitwise_and(car_r, car_r, mask=masks[i])
        x,y = np.where(masked!=0)
        topx = x.min()
        bottomx = x.max()
        topy=y.min()
        bottomy=y.max()
        crop = masked[topx:bottomx,topy:bottomy]
        cropped.append(crop)
        
    return(cropped)