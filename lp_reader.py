import numpy as np
import cv2
import pytesseract as tess
import string

class lp_reader():

    cropped = None
    
    def detect(self, car):
        self.car = car

        '''Function which returns list of 3 licence plate images, cropped from image of a car.
        Uses template matching, with 3 different template shapes of white rectange with black edges.

        Params:
        car - image of a car'''


        #changing car image to grayscale
        car = cv2.cvtColor(car, cv2.COLOR_BGR2GRAY)
        #resizing to 600x400
        car_r = cv2.resize(car, (400,400))
        #thresholding using Otsu binarization
        car_th = cv2.threshold(car_r, 0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        #getting canny
        car_canny = cv2.Canny(car_th, 200,400)

        #3 different lp sizes
        sizes = [(120,25),(130,30),(140,35)]

        #creating lp kernel for template matching - white rectangle with black edges
        lp = np.zeros((56,150), dtype=np.uint8)
        lp = cv2.rectangle(lp, (3,3), (147,53), 255, -1)
        # list of thresholded plates in all sizes
        plates = []
        for i in range(len(sizes)):
            plates.append(cv2.resize(lp, sizes[i]))

        #matching car with each LP size
        matches = []
        #list of matches for each size
        for i in plates:
            matches.append(cv2.matchTemplate(car_canny, i, cv2.TM_CCOEFF))

        #appends location of matched squares to list, inverted to (x,y), for thresh
        #minMaxLoc finds maximum for each match
        locs = []
        for i in range(len(matches)):
            locs.append(tuple(cv2.minMaxLoc(matches[i])[3]))


        #creates masks for images, where only LP remains
        masks = []
        for i in range(len(plates)):
            black = np.zeros(car_r.shape, dtype=np.uint8)
            black = cv2.rectangle(black, locs[i], (locs[i][0]+plates[i].shape[1], locs[i][1]+plates[i].shape[0]), 255, -1)
            masks.append(black)

        #returning masks to original input image size
        #this way, original size of LP is returned
        masks_r = []
        for i in masks:
            masks_r.append(cv2.resize(i, tuple([car.shape[1], car.shape[0]])))

        #keeping only LP - cropped list contains all cropped images of LPs
        cropped = []
        for i in range(len(plates)):
            masked = cv2.bitwise_and(car, car, mask=masks_r[i])
            x,y = np.where(masked!=0)
            topx = x.min()
            bottomx = x.max()
            topy=y.min()
            bottomy=y.max()
            crop = masked[topx:bottomx,topy:bottomy]
            cropped.append(crop)

        lp_reader.cropped = cropped

    def read(self):
        '''Function which reads and cleans text from detected images, using PyTesseract'''

        #allowed characters in plates
        #letters
        char = list(string.ascii_uppercase)
        #numbers
        for i in range (0,10):
            char.append(str(i))
         #removing non croatian letters
        char.remove('Q')
        char.remove('W')
        char.remove('X')
        char.remove('Y')


        #city segment of licence plate
        city = []
        #list of all croatain cities, including some common misreads (O and D)
        cro_cities = ['BJ', 'BM', 'CK', 'DA', 'OA', 'DE', 'OE', 'DJ', 'OJ', 'DU', 'OU', 'GS',
                     'IM', 'KA', 'KC', 'KR', 'KT', 'KZ', 'MA', 'NA',
                     'NG', 'OG', 'DG', 'OS', 'DS', 'PU', 'PZ', 'RI', 'SB', 'SK','SL',
                      'ST', 'SI', 'VK', 'VT', 'VU', 'VZ', 'ZD', 'ZO', 'ZG', 'ZU']

        #list of allowed numeric characters (0-9)
        numchar = []
        for i in range(10):
            numchar.append(str(i))




        #making thresholded plates for tesseract
        regs = []
        for i in lp_reader.cropped:
            regs.append(cv2.threshold(i, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
        # adding median filtering (denoiser) for each image
        for i in range(len(lp_reader.cropped)):
            regs.append(cv2.morphologyEx(cv2.medianBlur(lp_reader.cropped[i], 5), op=cv2.MORPH_OPEN, kernel=(7,7)))
        # adding original images
        for i in lp_reader.cropped:
            regs.append(i)



        #making list of all things tesseract reads
        all_regs = []
        #reading each image
        for i in range(len(regs)):
            all_regs.append(tess.image_to_string(regs[i], config='--psm 7'))
            #uppercasing
            for j in range(len(all_regs)):
                all_regs[j] = all_regs[j].upper()
        #getting rid of all non sucessful reads (i.e. if empty string is returned)
        all_regs_clean = []
        for i in all_regs:
            if i != '':
                all_regs_clean.append(i)



        #basic cleaning
        for i in range(len(all_regs_clean)):
            for j in all_regs_clean[i]:
                if j == '|':
                    all_regs_clean[i] = all_regs_clean[i].replace(j,'I')
                elif j == '(':
                    all_regs_clean[i] = all_regs_clean[i].replace(j,'C')

        #removing all not allowed characters (those not in char)
        for i in range(len(all_regs_clean)):
            for j in all_regs_clean[i]:
                if j not in char:
                    all_regs_clean[i] = all_regs_clean[i].replace(j,'')
        for i in all_regs_clean:
            if len(i) < 3:
                all_regs_clean.remove(i)


        #city as first 2 letters read
        for i in all_regs_clean:
            city.append(i[0:2])
        #replacing numbers with letters
        for i in range(len(city)):
            for j in city[i]:
                if j == '1':
                    city[i] = city[i].replace(j,'I')
                if j == '2':
                    city[i] = city[i].replace(j,'Z')
                if j == '4':
                    city[i] = city[i].replace(j,'A')
                if j == '5':
                    city[i] = city[i].replace(j,'S')
                if j == '6':
                    city[i] = city[i].replace(j,'G')
                if j == '7':
                    city[i] = city[i].replace(j,'Z')
                if j == '8':
                    city[i] = city[i].replace(j,'B')
                if j == '0':
                    city[i] = city[i].replace(j,'O')
        #some more cleaning:
        for i in range(len(city)):
            if city[i] == 'ZC':
                city[i] = 'ZG'
        #keeping only those from cro cities list
        city2 = []
        for i in city:
            if i in cro_cities:
                city2.append(i)
        #reading 2nd and 3rd characters if 1st and 2nd fail
        if city2 == []:
            #third variable - tells if 1and2 or 2and3 are used as city letters
            third = True
            for i in all_regs_clean:
                city.append(i[1:3])
            for i in range(len(city)):
                for j in city[i]:
                    if j == '1':
                        city[i] = city[i].replace(j,'I')
                    if j == '2':
                        city[i] = city[i].replace(j,'Z')
                    if j == '4':
                        city[i] = city[i].replace(j,'A')
                    if j == '5':
                        city[i] = city[i].replace(j,'S')
                    if j == '6':
                        city[i] = city[i].replace(j,'G')
                    if j == '7':
                        city[i] = city[i].replace(j,'Z')
                    if j == '8':
                        city[i] = city[i].replace(j,'B')
                    if j == '0':
                        city[i] = city[i].replace(j,'O')
            city2 = []
            for i in city:
                if i in cro_cities:
                    city2.append(i)
        #third set to false if first two letters are used
        else:
            third = False
        #cleaning D and O
        for i in range(len(city2)):
            if city2[i] == 'OA':
                city2[i] = 'DA'
            if city2[i] == 'OU':
                city2[i] = 'DU'
            if city2[i] == 'OE':
                city2[i] = 'DE'
            if city2[i] == 'OJ':
                city2[i] = 'DJ'
            if city2[i] == 'DS':
                city2[i] = 'OS'
            if city2[i] == 'DG':
                city2[i] = 'OG'
            if city2[i] == 'ZO':
                city2[i] = 'ZD'

        #most frequent
        if city2 != []:
            city = max(set(city2), key=city2.count)
        else:
            city = ''

        #ending 2 letters segment

        #removing all shorter than 7: 
        # if shorter than 7, last 2 letters are probably not present on cropped image
        last = []
        for i in all_regs_clean:
            if len(i) >= 7:
                last.append(i)

        #taking last 2 letters
        for i in range(len(last)):
            last[i] = last[i][-2:]


            #cleaning numbers and letters
        for i in range(len(last)):
            for j in last[i]:
                if j == '1':
                    last[i] = last[i].replace(j,'I')
                if j == '2':
                    last[i] = last[i].replace(j,'Z')
                if j == '4':
                    last[i] = last[i].replace(j,'A')
                if j == '5':
                    last[i] = last[i].replace(j,'S')
                if j == '6':
                    last[i] = last[i].replace(j,'G')
                if j == '7':
                    last[i] = last[i].replace(j,'Z')
                if j == '8':
                    last[i] = last[i].replace(j,'B')
                if j == '0':
                    last[i] = last[i].replace(j,'O')
        #throwing out all containing 3 and 9
        last2 = []
        for i in last:
            if '3' not in i:
                last2.append(i)
        last = []
        for i in last2:
            if '9' not in i:
                last.append(i)

        # D and O
        for i in range(len(last)):
            if 'O' in last[i]:
                last.append(last[i].replace('O', 'D'))
            if 'D' in last[i]:
                last.append(last[i].replace('D', 'O'))

        #deduplicating and sorting by frequency (most frequent first)

        #if list contains 3 or less solutions, keeping them all
        if len(last) <= 3:
            last = list(set(last))
        else:
            #deduplicating and sorting by frequency (most frequent first)
            last2 = sorted(last, key=last.count, reverse=True)
            #if most common solution accounts for more than 50% possibilities, keeping it
            if last2.count(last2[0])/len(last2) > 0.5:
                last = [last2[0]]
            else:
                #keeping first 3 possibilites
                last = []
                for i in last2:
                    if i not in last:
                        last.append(i)
                #keeping only first 3 solutions
                last = last[:3]



        # numbers

            #list of allowed numeric characters (0-9)
        numchar = []
        for i in range(10):
            numchar.append(str(i))
            numbers = []
        for i in all_regs_clean:
            # if longer than 7, throwing off both first and last letters
            if len(i) >= 7:
                #if city is infered from first 2 chars:
                #remove first 2 chars and last 2 chars
                if third == False:
                    numbers.append(i[2:][:-2])
                #if city is inferred from first 3 chars:
                #remove first 3 and last 2 chars
                else:
                    numbers.append(i[3:][:-2])
            #if shorter than 7, throwing off only first 2 chars
            #again with third, depending if city is inferred from 2 or 3 chars
            else:
                if third == False:
                    numbers.append(i[2:])
                else:
                    numbers.append(i[3:])
        #throwing out all non numeric characters
        for i in range(len(numbers)):
            for j in numbers[i]:
                if j not in numchar:
                    numbers[i] = numbers[i].replace(j,'')

        #if item is 5 long, probably contains some misread caused by croatian coat of arms
        #removing this and keeping rest
        for i in range(len(numbers)):
            if len(numbers[i]) == 5:
                numbers[i] = numbers[i][1:]
        #throwing out all not long 3 or 4
        numbers2 = []
        for i in numbers:
            if len(i) == 3 or len(i) == 4:
                numbers2.append(i)  
        #if list contains 3 or less solutions, keeping them all
        if len(numbers2) <= 3:
            numbers = list(set(numbers2))
        else:
            #deduplicating and sorting by frequency (most frequent first)
            numbers3 = sorted(numbers2, key=numbers2.count, reverse=True)
            #if most common solution accounts for more than 65% possibilities, keeping it
            if numbers3.count(numbers3[0])/len(numbers3) > 0.65:
                numbers = [numbers3[0]]
            else:
                #keeping first 2 possibilites
                numbers = []
                for i in numbers2:
                    if i not in numbers:
                        numbers.append(i)
                #keeping only first 2 solutions
                numbers = numbers[:2]

        #final
        final = []
        for i in last:
            for j in numbers:
                final.append(city + '-' + j + '-' + i)

        return(final)
    


    