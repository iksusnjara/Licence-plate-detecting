import numpy as np
import cv2
import pytesseract as tess
import string

def read_lp(lps):
    
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
        
        

    #preporcessing plates images for tesseract
    regs = []
    #adding thresholded images, with Otsu
    for i in lps:
        regs.append(cv2.threshold(i, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
    # adding median filtering (denoiser) for each image
    for i in range(len(lps)):
        regs.append(cv2.medianBlur(lps[i], 5))
    # adding original images
    for i in lps:
        regs.append(i)
        
        

    #making list of all things tesseract reads
    all_regs = []
    #reading each image
    for i in range(len(regs)):
        all_regs.append(tess.image_to_string(regs[i]))
        #uppercasing
        for j in range(len(all_regs)):
            all_regs[j] = all_regs[j].upper()
    #getting rid of all non sucessful reads (i.e. if empty string is returned)
    all_regs_clean = []
    for i in all_regs:
        if i != '':
            all_regs_clean.append(i)
            
            
            
    #removing all not allowed characters (those not in char)
    for i in range(len(all_regs_clean)):
        for j in all_regs_clean[i]:
            if j not in char:
                all_regs_clean[i] = all_regs_clean[i].replace(j,'')
    #remowing all reads shorter than 3
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
            if j == '3':
                city[i] = city[i].replace(j,'G')
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
    #keeping only those from cro cities list
    city2 = []
    for i in city:
        if i in cro_cities:
            city2.append(i)
    #reading city as 2nd and 3rd characters if first 2 did not return anything
    if city2 == []:
        for i in all_regs_clean:
            city.append(i[1:3])
          #more cleaning
        for i in range(len(city)):
            for j in city[i]:
                if j == '1':
                    city[i] = city[i].replace(j,'I')
                if j == '2':
                    city[i] = city[i].replace(j,'G')
                if j == '3':
                    city[i] = city[i].replace(j,'B')
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
         #keeping only reads which exist in croatia
        city2 = []
        for i in city:
            if i in cro_cities:
                city2.append(i)
                
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
    #final list of possible cities
    city = list(set(city2))

    
    
    
       #ending 2 letters segment
    #keeping only ones with length of 2
    end = []
    #appending last 2 chars
    for i in all_regs_clean:
        end.append(i[-2:])
        #cleaning numbers and letters
    for i in range(len(end)):
        for j in end[i]:
            if j == '1':
                end[i] = end[i].replace(j,'I')
            if j == '2':
                end[i] = end[i].replace(j,'Z')
            if j == '3':
                end[i] = end[i].replace(j,'B')
            if j == '4':
                end[i] = end[i].replace(j,'A')
            if j == '5':
                end[i] = end[i].replace(j,'S')
            if j == '6':
                end[i] = end[i].replace(j,'G')
            if j == '7':
                end[i] = end[i].replace(j,'Z')
            if j == '8':
                end[i] = end[i].replace(j,'B')
            if j == '9':
                end[i] = end[i].replace(j,'')
            if j == '0':
                end[i] = end[i].replace(j,'O')
    #removing if not 2 long
    for i in end:
        if len(i) != 2:
            end.remove(i)
    # D and O
    for i in range(len(end)):
        if 'O' in end[i]:
            end.append(end[i].replace('O', 'D'))
        if 'D' in end[i]:
            end.append(end[i].replace('D', 'O'))
            
      #final list of all possibilities for last segment

    end = list(set(end))
    
    #cleaning last two elements from numbers

    numbers_last = []

    # -2:-1 char
    #cleaning letters and numbers
    for i in range(len(all_regs_clean)):
        a = list(all_regs_clean[i])
        for j in range(1,3):
            if a[-j] == '1':
                a[-j] = 'I'
            if a[-j] == '2':
                a[-j] = 'Z'
            if a[-j] == '3':
                a[-j] = 'B'
            if a[-j] == '4':
                a[-j] = 'A'
            if a[-j] == '5':
                a[-j] = 'S'
            if a[-j] == '6':
                a[-j] = 'G'
            if a[-j] == '7':
                a[-j] = 'Z'
            if a[-j] == '8':
                a[-j] = 'B'
            if a[-j] == '0':
                a[-j] = 'O'
        b = ''.join(a)
        numbers_last.append(b)
    numbers_last = list(set(numbers_last))
    
    #if last two char are in numbers_last, remove them
    for i in range(len(numbers_last)):
        if ''.join(list(numbers_last[i][-2:])) in numbers_last:
            numbers_last[i] = numbers_last[i][:-2]

    #removing shorter than 3
    for i in numbers_last:
        if len(i) < 3:
            numbers_last.remove(i)
    numbers_last = list(set(numbers_last))
    
    #list for cleaning numbers
    #here we remove first letters from original reads
    # last are already removed
    numbers = []
    #first char
    #appending it to numbes list
    for i in range(len(numbers_last)):
        a = list(numbers_last[i])
        if a[0] == '1':
            a[0] = 'I'
        if a[0] == '2':
            a[0] = 'Z'
        if a[0] == '3':
            a[0] = 'B'
        if a[0] == '4':
            a[0] = 'A'
        if a[0] == '5':
            a[0] = 'S'
        if a[0] == '6':
            a[0] = 'G'
        if a[0] == '7':
            a[0] = 'Z'
        if a[0] == '8':
            a[0] = 'B'
        if a[0] == '0':
            a[0] = 'O'
        b = ''.join(a)
        numbers.append(b)

    # changing second char after the first has already been changed
    # appending to numbers list
    # so both versions - with only first changed as well as with both first and second changed
    # are kept
    for i in range(len(numbers)):
        a = list(numbers[i])
        if a[1] == '1':
            a[1] = 'I'
        if a[1] == '2':
            a[1] = 'Z'
        if a[1] == '3':
            a[1] = 'B'
        if a[1] == '4':
            a[1] = 'A'
        if a[1] == '5':
            a[1] = 'S'
        if a[1] == '6':
            a[1] = 'G'
        if a[1] == '7':
            a[1] = 'Z'
        if a[1] == '8':
            a[1] = 'B'
        if a[1] == '0':
            a[1] = 'O'
        b = ''.join(a)
        numbers.append(b)

    #0:3 char
    # same as above
    # at the end keeps versions where only first is changed
     # first and second are changed
      # all 3 are changed
    for i in range(len(numbers)):
        a = list(numbers[i])
        if a[2] == '1':
            a[2] = 'I'
        if a[2] == '2':
            a[2] = 'Z'
        if a[2] == '3':
            a[2] = 'B'
        if a[2] == '4':
            a[2] = 'A'
        if a[2] == '5':
            a[2] = 'S'
        if a[2] == '6':
            a[2] = 'G'
        if a[2] == '7':
            a[2] = 'Z'
        if a[2] == '8':
            a[2] = 'B'
        if a[2] == '0':
            a[2] = 'O'
        b = ''.join(a)
        numbers.append(b)
    numbers = list(set(numbers))

    ## throwing letters out after changing first 3 chars
     # keeps only numbers
     # if they were originally letters, they are removed
      # if they were originally numbers which are misread, they are converted to letters and removed
    numbers2 = numbers.copy()
    for i in range(len(numbers2)):
        for j in numbers2[i]:
            if j not in numchar:
                numbers2[i] = numbers2[i].replace(j,'')


    #keeping only numbers with length 3 or 4
    numbers34 = []
    for i in numbers2:
        if len(i) == 3 or len(i) == 4:
            numbers34.append(i)
    numbers34 = set(list(numbers34))
    
    
    final = []
    final2 = []
    #combining city with every possible number
    for i in city:
        for j in numbers34:
            final.append(i + '-' +j)
    #combining all city-numbers with each possible ending 
    for i in final:
        for j in end:
            final2.append(i + '-' + j)
    #removing duplicates
    final2 = set(final2)
    final2 = list(final2)
    final2
    
    # final list of all posible licence plates
    return(final2)