#!/usr/bin/env python3

import time
import cv2
import json
import copy
import img2pdf
import pre_process as pp
import parse_name as pn
import numpy as np


class coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class boundingBox:
    bound_text = ''
    box_type = ''
    tl = coordinate(0, 0)
    tr = coordinate(0, 0)
    br = coordinate(0, 0)
    bl = coordinate(0, 0)

    def __init__(self, tl, tr, bl, br, bound_text, box_type):

        """
        :param tl: coordinates of top left
        :param tr: coordinates of top right
        :param bl: coordinates of bottom left
        :param br: coordinates of bottom right
        :param bound_text: The text inside the box
        :param box_type: categorize the box as line(L)/word(W)
        """

        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.bound_text = bound_text
        self.box_type = box_type

    def __repr__(self):  # object definition
        return "<boundingBox box_type:%s bound_text:%s tl:(%s,%s) tr:(%s,%s) bl:(%s,%s) br:(%s,%s)>" % (self.box_type,
            self.bound_text, self.tl.x, self.tl.y, self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y)

    def __str__(self):  # print statement
        return "box_type:%s \nbound_text:%s \ntl:(%s,%s) \ntr:(%s,%s) \nbl:(%s,%s) \nbr:(%s,%s)" % (self.box_type,
            self.bound_text, self.tl.x, self.tl.y, self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y)


def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    :return: out_image: processed image in cv2 format
    """
    pp.notescan_main(input_image)
    out_image = cv2.imread("output.png")
    return out_image


def get_names(in_str):
    """
    calls extract from parse_name module
    :param in_str: input string
    :return: list containing names present in the input string
    """
    return pn.extract(in_str)


def get_azure_ocr(input_image):
    azure_json = {}
    return azure_json


def parse_azure_json(azure_json):
    """
    extract data from json created by Azure
    :param azure_json: path to the json file
    :return llist: list of boundings boxes of words
    """

    data = json.load(open(azure_json))
    sentence = data["recognitionResult"]["lines"]
    slen = len(sentence)

    # initialize
    c = coordinate(0, 0)
    bb = boundingBox(c, c, c, c, "", "W")
    llist = []
    for i in range(slen):
        line = sentence[i]["words"]
        line_box = sentence[i]["boundingBox"]
        bb.bound_text = sentence[i]["text"]
        bb.box_type = "L"
        bb.bl = coordinate(line_box[0], line_box[1])
        bb.br = coordinate(line_box[2], line_box[3])
        bb.tr = coordinate(line_box[4], line_box[5])
        bb.tl = coordinate(line_box[6], line_box[7])
        llist.append(copy.deepcopy(bb))
        llen = len(line)
        for j in range(llen):
            word_box = line[j]["boundingBox"]
            word = line[j]["text"]
            bb.box_type = "W"
            bb.bl = coordinate(word_box[0], word_box[1])
            bb.br = coordinate(word_box[2], word_box[3])
            bb.tr = coordinate(word_box[4], word_box[5])
            bb.tl = coordinate(word_box[6], word_box[7])
            bb.bound_text = word
            llist.append(copy.deepcopy(bb))
    return llist


def img_to_pdf(image):  # name of the image as input
    pdf_bytes = img2pdf.convert([image])
    date_string = time.strftime("%Y-%m-%d-%H:%M:%S.pdf")
    file = open(date_string, "wb")
    file.write(pdf_bytes)
    file.close()
    return date_string


def get_parallel_boxes(bounding_boxes):
    list_of_boxes = []
    return list_of_boxes


def get_lexigram(bounding_boxes):
    lexigram_json = {}
    return lexigram_json


def fix_spelling(bounding_box):
    # return bounding box
    return bounding_box


def draw_box(in_img, l_boxes):
    """
    draw red bounding boxes for line ('L') box_types
    :param in_img: input image in opencv format
    :param l_boxes: list of bounding boxes to be drawn
    :return: in_img: image (in opencv format) after drawing boxes in red
    """
    red = (0, 0, 255)  # opencv follows bgr pattern
    for box in l_boxes:
        if box.box_type == 'L':
            vertices = np.array([[box.tl.x, box.tl.y], [box.tr.x, box.tr.y], [box.br.x, box.br.y],
                                 [box.bl.x, box.bl.y]], np.int32)
            cv2.polylines(in_img, [vertices], True, red, thickness=1, lineType=cv2.LINE_AA)

    # uncomment below lines while debugging
    # cv2.imshow("debug", in_img)
    # cv2.waitKey(0)

    return in_img
    

def put_text(in_img, l_boxes):
    """
    put extracted text (in black) over the place of original text
    :param in_img: cleaned image in opencv format
    :param l_boxes: list of bounding boxes
    :return: out_img: a separate image with text placed at right places
    """
    out_img = in_img
    font = cv2.FONT_HERSHEY_DUPLEX
    font_color = (0, 0, 0)
    # multiplying factor used to calculate font_scale in relation to height
    factor = .03

    for box in l_boxes:
        if box.box_type == 'W':

            height = box.bl.y - box.tl.y
            width = box.tr.x - box.tl.x

            font_scale = factor * height
            text_size = cv2.getTextSize(box.bound_text, font, font_scale, thickness=1)
            # to put text in middle of the bounding box
            text_x_center = int(box.bl.x + ((width / 2) - (text_size[0][0] / 2)))
            text_y_center = int(box.bl.y - ((height / 2) - (text_size[0][1] / 2)))

            cv2.putText(out_img, box.bound_text, (text_x_center, text_y_center), font, font_scale, font_color,
                        thickness=1, lineType=cv2.LINE_AA)

    # while debugging and calibrating, uncomment below lines
    # cv2.imshow("test", out_img)
    # cv2.waitKey(0)

    return out_img


if __name__ == '__main__':
    print("Hello!")
