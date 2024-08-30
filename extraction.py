import cv2
import numpy as np
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
from boxdetect import config
from boxdetect.pipelines import get_checkboxes
from fastapi import FastAPI, UploadFile

app = FastAPI()

# pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'



def pdf_to_images(pdf_path):
    """ Convert each pages of the PDF to an Images. """
    # return convert_from_path(pdf_path, dpi=900, poppler_path=r'\poppler-21.11.0\Library\bin')
    return convert_from_path(pdf_path, dpi=900)


def image_reshaping(img_np):
    """ Resize image to specific dimensions. """
    resize_width = 2550
    resize_height = 3300
    img_np = cv2.resize(img_np, (resize_width, resize_height))
    return img_np





def extract_key_values(pdf_path):

    """ used for extraction of required data from image """

    my_dict = {'Shipper Name': '', 'Shipper Address': '', 'Consignee Name': '', 'Consignee Address': '',
               'Notify party Name': '', ' Notify Address': '',
               'Pre-carriage': '', 'Also Notify Party Name': '', 'Also Notify Party Address': '',
               'Place of Receipt': '', 'Port of Loading': '',
               'Intended Vessel': '', 'Port of Discharge': '', 'Place of Delivery': '',
               'Country of Origin of Goods': '', 'Export License No.': '', 'Shipping type': '',
               'Freight Term': '', 'Marks & Number': '', 'No. of Packages': '', 'Description of Goods': '',
               'Kgs (weight)': '', 'CBM (volume)': '', 'REMARK:': ''
               }


    images = pdf_to_images(pdf_path)
    img = np.array(images[0])
    # original_image = img
    img = image_reshaping(img)
    d = pytesseract.image_to_data(img, output_type=Output.DICT, config='--psm 4')
    n_boxes = len(d['level'])

    for i in range(n_boxes):
        if ('Shipper' in d['text'][i]) and (d['left'][i] < 250 and d['top'][i] < 105):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 8, y + h, h + 220, w + 900
            roi = img[y:y + h, x:x + w]
            Shipper_area = pytesseract.image_to_string(roi).split('\n')
            my_dict['Shipper Name'] = Shipper_area[0]
            my_dict['Shipper Address'] = ''.join(Shipper_area[1:])

        elif ('Consignee' in d['text'][i]) and (d['left'][i] < 250 and d['top'][i] < 400):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 211, w + 830
            roi = img[y:y + h, x:x + w]
            consignee_area = pytesseract.image_to_string(roi).split('\n')
            my_dict['Consignee Name'] = consignee_area[0]
            my_dict['Consignee Address'] = ''.join(consignee_area[1:])


        elif ('Notify' in d['text'][i]) and (d['left'][i] < 250 and d['top'][i] < 700):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 8, y + h, h + 215, w + 900
            roi = img[y:y + h, x:x + w]
            Notify_area = pytesseract.image_to_string(roi).split('\n')
            my_dict['Notify party Name'] = Notify_area[0]
            if my_dict['Notify party Name'] == 'SAME AS CONSIGNEE':
                my_dict[' Notify Address'] = 'SAME AS CONSIGNEE'
            else:
                my_dict[' Notify Address'] = ' '.join(Notify_area[1:])


        elif ('Pre-carriage' in d['text'][i]) and (d['left'][i] < 250 and d['top'][i] < 960):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 50, w + 850
            roi = img[y:y + h, x:x + w]
            Pre_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Pre-carriage'] = Pre_area

        elif ('Also' in d['text'][i]) and (d['left'][i] < 1200 and d['top'][i] < 700):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 217, w + 1200
            roi = img[y:y + h, x:x + w]
            Party_area = pytesseract.image_to_string(roi).split('\n')
            my_dict['Also Notify Party Name'] = Party_area[0]
            my_dict['Also Notify Party Address'] = ' '.join(Party_area[1:])

        elif ('Place' in d['text'][i]) and (d['left'][i] < 1200 and d['top'][i] < 970):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 53, w + 400
            roi = img[y:y + h, x:x + w]
            Place_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Place of Receipt'] = Place_area

        elif ('Port' in d['text'][i]) and ((1300 < d['left'][i] < 1700) and (d['top'][i] < 990)):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 53, w + 800
            roi = img[y:y + h, x:x + w]
            Port_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Port of Loading'] = Port_area

        elif ('Intended' in d['text'][i]) and (d['left'][i] < 150 and d['top'][i] < 1100):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 48, w + 890
            roi = img[y:y + h, x:x + w]
            Intended_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Intended Vessel'] = Intended_area

        elif ('Port' in d['text'][i]) and (d['left'][i] < 1200 and d['top'][i] < 1100):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 48, w + 400
            roi = img[y:y + h, x:x + w]
            Discharge_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Port of Discharge'] = Discharge_area

        elif ('Place' in d['text'][i]) and ((1400 <d['left'][i] < 1800) and d['top'][i] < 1200):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 5, y + h, h + 48, w + 750
            roi = img[y:y + h, x:x + w]
            Pod_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Place of Delivery'] = Pod_area

        elif (('CY' in d['text'][i] or 'cy' in d['text'][i]) and (d['left'][i] < 300 and d['top'][i] < 1300)):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                x2, y2, h2, w2 = x - 10, y - 51, h + 15, w + 240
                roi = img[y2:y2 + h2, x2:x2 + w2]
                Cog_area2 = pytesseract.image_to_string(roi).split('\n')
                my_dict['Country of Origin of Goods'] = Cog_area2[0]
                x1, y1, h1, w1 = x + 540, y - 60, h + 0, w + 240
                roi2 = img[y1:y1 + h1, x1:x1 + w1]
                Export_area = pytesseract.image_to_string(roi2).split('\n')
                my_dict['Export License No.'] = Export_area[0]

        elif (('Marks' in d['text'][i]) and (d['left'][i] < 350 and d['top'][i] < 1400)) or (('REMARK:' in d['text'][i]) and (d['left'][i] < 300 and d['top'][i] < 2500)):
            if ('Marks' in d['text'][i]):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                x1, y1, h1, w1 = x - 130, y + 45, h + 400, w + 390
                roi = img[y1:y1 + h1, x1:x1 + w1]
                Marks_area1 = pytesseract.image_to_string(roi).replace('\n', ' ')
                my_dict['Marks & Number'] = Marks_area1
                x2, y2, h2, w2 = x - 145, y + 1150, h + 200, w + 2350
                roi2 = img[y2:y2 + h2, x2:x2 + w2]
                Remark_area = pytesseract.image_to_string(roi2).replace('\n', ' ')
                my_dict['REMARK:'] = Remark_area
            else:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                x, y, h, w = x - 5, y - 5, h + 194, w + 2350
                roi2 = img[y:y + h, x:x + w]
                Remark_area = pytesseract.image_to_string(roi2).replace('\n', ' ')
                my_dict['REMARK:'] = Remark_area
        elif ('Packages' in d['text'][i]) and (d['left'][i] < 810 and d['top'][i] < 1400):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x, y, h, w = x - 135, y + 60, h + 400, w + 150
            roi = img[y:y + h, x:x + w]
            package_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            package_area = package_area.replace('\"', ' ')
            my_dict['No. of Packages'] = package_area
        elif ('Description' in d['text'][i]) and (d['left'][i] < 1310 and d['top'][i] < 1400):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x1, y1, h1, w1 = x - 350, y + 45, h + 340, w + 788
            roi = img[y1:y1 + h1, x1:x1 + w1]
            Dog_area = pytesseract.image_to_string(roi).replace('\n', ' ')
            my_dict['Description of Goods'] = Dog_area
            x2, y2, h2, w2 = x + 600, y - 25, h + 400, w + 100
            roi2 = img[y2:y2 + h2, x2:x2 + w2]
            weight_area = pytesseract.image_to_string(roi2).replace('\n', ' ')
            my_dict['Kgs (weight)'] = weight_area
            x3, y3, h3, w3 = x + 850, y - 20, h + 400, w + 150
            roi3 = img[y3:y3 + h3, x3:x3 + w3]
            Cbm_area = pytesseract.image_to_string(roi3).replace('\n', ' ')
            my_dict['CBM (volume)'] = Cbm_area

    my_dict=box(img,my_dict)
    return my_dict


#
def box(img, my_dict):
    cfg = config.PipelinesConfig()
    cfg.width_range = (23, 42)
    cfg.height_range = (24, 40)
    cfg.scaling_factors = [5]
    cfg.wh_ratio_range = (0.1, 7.7)
    cfg.group_size_range = (2, 100)
    cfg.dilation_iterations = 1
    checkboxes = get_checkboxes(img, cfg=cfg, px_threshold=0.2, plot=False, verbose=False)
    list1=[]
    list2=[]
    if len(checkboxes) >= 10:
        cfg.width_range = (30, 42)
        checkboxes = get_checkboxes(img, cfg=cfg, px_threshold=0.2, plot=False, verbose=False)
    keys = ['CY/CY', 'CFS/CFS', 'CFS/CY', 'CY/CFS']
    keys2 = ['Prepaid ', 'Collect']
    dictionary = {key: None for key in keys}
    dictionary2 = {key: None for key in keys2}
    for i in checkboxes:
        if 1100 <= i[0][1] <= 1400 and 1000>i[0][0] <= 1900:
            x, y, w, h = i[0]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if len(dictionary) > 0:
                key = keys.pop(0)
                dictionary[key] = i[1]

        elif  1100 <= i[0][1] <= 1400 and 1000<i[0][0] <= 1900:
            if len(dictionary2) > 0:
                key = keys2.pop(0)
                dictionary2[key] = i[1]

    for index, key in enumerate(dictionary):
        if dictionary[key] == True:
            list1.append(key)

    for index, key in enumerate(dictionary2):
        if dictionary2[key] == True:
            list2.append(key)

    my_dict['Shipping type'] = ', '.join(list1)
    my_dict['Freight Term'] = ', '.join(list2)
    return my_dict



