# import the necessary packages
import numpy as np
import argparse
import cv2
import glob
import os
import json


def saveFaceCoords(filename, coords):
    filename = filename[:-3] + "json"
    jdata = {
        f"{filename}": {
            "x1": int(coords[0]),
            "y1": int(coords[1]),
            "x2": int(coords[2]),
            "x3": int(coords[3]),
        }
    }

    print(jdata)

    with open(f"./images_json/{filename}", "w") as f:
        json.dump(jdata, f)


def boxTheFace(confidence, image, coords):
    imageBox = image.copy()
    startX, startY, endX, endY = coords
    # draw the bounding box of the face along with the associated
    # probability
    text = "{:.2f}%".format(confidence * 100)
    y = startY - 10 if startY - 10 > 10 else startY + 10
    cv2.rectangle(imageBox, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.putText(
        imageBox, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2
    )
    # show the output image
    cv2.imshow("Output", imageBox)
    cv2.waitKey(0)


def cropImg(image, filename, coords, show=False, save=True):

    startX, startY, endX, endY = coords
    print(f"{startX}, {startY}, {endX}, {endY}")

    # img[start_row:end_row, start_col:end_col]

    cropped_image = image[startY:endY, startX:endX]

    # Save or display the cropped image
    if save:
        print(f"saving: {filename}")
        cv2.imwrite(f"./images_cropped/{filename}", cropped_image)
    # or
    if show:
        cv2.imshow("Cropped Image", cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# Location of two items necessary for the cv2 dnn (deep neural net)
# I don't have a clue ... black box mentality for now
prototxt = "./deploy.prototxt.txt"
model = "./res10_300x300_ssd_iter_140000.caffemodel"

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# read images using glob which does wildcard matching of files
images = glob.glob("./images/*.jpg")

# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it

# process each augmented image done in augment.py
for image in images:
    fname = os.path.basename(image)

    image = cv2.imread(image)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    )

    # pass the blob through the network and obtain the detections and

    net.setInput(blob)
    detections = net.forward()
    count = 0

    max_confidence = 0  # I only want to match with the highest score
    index = -1  # remember which location in the array it exists

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        if confidence > max_confidence:
            max_confidence = confidence
            index = i

    # This code draws a box on the image and displays it. The location of the face
    # isn't saved anywhere, but in the future it should be (obviously).

    # compute the (x, y)-coordinates of the bounding box for the object
    box = detections[0, 0, index, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")

    boxTheFace(max_confidence, image, (startX, startY, endX, endY))
    cropImg(image, fname, (startX, startY, endX, endY), False, True)
    saveFaceCoords(fname, (startX, startY, endX, endY))
