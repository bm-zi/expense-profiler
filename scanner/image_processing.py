import pytesseract
import cv2
from imutils.perspective import four_point_transform
import re
import difflib

def simplifyContourFurther(contour, cornerCount=4):
    """
    Tries to find epsilon such that new simplified contour have specified corner count,
    returns unchanged contour on fail, else simplified contour 
    """
    i, maxIterations = 0, 100
    lowerBound, upperBound = 0., 1.
    perimeter = cv2.arcLength(contour, closed=True)
    
    while True:
        i+=1
        if i > maxIterations:
            return contour
        
        k = (lowerBound+upperBound)/2
        eps = k * perimeter
        approx = cv2.approxPolyDP(contour, eps, closed= True)
        if len(approx) > cornerCount: 
            lowerBound = (lowerBound+upperBound)/2.0
        elif len(approx) < cornerCount:
            upperBound = (lowerBound+upperBound)/2.0
        else:
            return approx


def findDocumentContour(img):
    """
    Finds contour of a scanned document, returns contour and thresholded image
    """
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #blurring imgae to remove noise before thresholding
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 0)
    #calculating threshold of an image using Otsu method
    _, threshold = cv2.threshold(imgBlur,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #detecting contours: contour - list of points that enclose an object 
    contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #sorting contours by their area - largest first
    contoursSorted = sorted(contours, key=cv2.contourArea, reverse=True)

    for contour in contoursSorted:
        area = cv2.contourArea(contour)
        if area > 1000:
            #perimeter of closed contour
            perimeter= cv2.arcLength(contour, True)
            #calculating approximated contour
            approxContour = cv2.approxPolyDP(curve=contour, epsilon=0.02 * perimeter, closed= True)
            if len(approxContour) > 4:
                #if contour is still not simplified enough we try to bissect epsilon till it is
                newApproxContour = simplifyContourFurther(approxContour)
                if len(newApproxContour) != 4:
                    continue
                else:
                    return newApproxContour
                    
            elif len(approxContour) == 4:
                return approxContour
            else:
                continue
    return None
    
def covert2Gray(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(imgGray,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshold

def scan(image):
    img = cv2.imread(image)

    documentContour = findDocumentContour(img)
    
    imgWarped = four_point_transform(img, documentContour.reshape(4,2))
    # Cutting 50 pixels from the top, sometimes the image has black pixels at the top because of eg. folded receipt
    imgWarped = imgWarped[50:imgWarped.shape[0], 0:imgWarped.shape[1]]
    
    # calculating new threshold for receipt without backround
    imgWarped = covert2Gray(imgWarped)
    
    options = "--psm 6"
    data = pytesseract.image_to_string(imgWarped, lang='pol', config=options)
    
    company_name = data.split("\n")[0]
    
    # \b is a word boundary. It matches the beginning and ending of a word
    addressRegex = r'(\b[0-9]{2}\-[0-9]{3}\b)'
    address = None 
    
    # two formats of saving data on the receipts
    dateRegex = r'(\b[0-9]{2}\-[0-9]{2}\-[0-9]{4}\b|\b[0-9]{4}\-[0-9]{2}\-[0-9]{2}\b)'
    date = None 
    
    priceRegex = r'([0-9]+[\,\.][0-9]{2})'
    items = None

    total_value = None
    
    flag = 0 #indication of beginning and end of items on the receipt
    tmp_description = '' #will be used when description and price of an item are in the different rows

    for row in data.split("\n"):
        if re.search(addressRegex, row) is not None and address is None:
            address = row
        if re.search(dateRegex, row) is not None:
            date = re.search(dateRegex, row).group(1) # taking only the date out of the date row
           
        # Searching for total value
        totalSynonyms = ["SUMA", "SUM", "TOTAL", "CAD","PRICE", "PLN", "$"]
        temp = [difflib.get_close_matches(synonym, row.upper().split(), n=1) for synonym in totalSynonyms]
        isTotal = any(temp)
        if (isTotal):
            try:
                total_value = float(re.findall(priceRegex, row)[0].replace(",", "."))
                continue
            except Exception as e:
                continue
            
        # Looking for rows containing prices
        match = re.search(priceRegex, row)
        
        tmp = row.upper().split()
        if difflib.get_close_matches('SPRZED', tmp, n=1) or difflib.get_close_matches('RAZEM', tmp, n=1) or difflib.get_close_matches('PTU', tmp, n=1):
            flag = 0
            
        if match is None and flag == 1:
            tmp_description = row
        
        if match and flag == 1 and 'Rabat' not in row:
            items = [] if items == None else items
            
            price_index = row.find(match.group())
            description = row[:price_index]
            description = tmp_description if tmp_description != '' else description
            tmp_description = ''
            
            temp = (re.findall(priceRegex, row)[-1].replace(",", ".")) 
            price = float(temp)
            items.append({'description': description, 'price': price})
            
        if difflib.get_close_matches('PARAGON', row.split(), n=1):
            flag = 1
            
    context = {'company': company_name, 'address': address, 'date': date, 'full_price': total_value, 'items': items}

    return context 