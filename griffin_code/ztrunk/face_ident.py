import cv2

# Assuming 'deploy.prototxt' and 'res10_300x300_ssd_iter_140000.caffemodel' are in your current directory
prototxt_path = "deploy.prototxt"
caffemodel_path = "res10_300x300_ssd_iter_140000.caffemodel"

# Load the pre-trained Caffe model
face_net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)


# Load the augmented image
image = cv2.imread("augmented_image_0.jpg")  # Example for the first augmented image

# Prepare the image for the model
blob = cv2.dnn.blobFromImage(
    cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
)

# Perform face detection
face_net.setInput(blob)
detections = face_net.forward()

# Draw bounding boxes around detected faces
for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence > 0.5:  # Consider detection as a face if confidence > 0.5
        box = detections[0, 0, i, 3:7] * np.array(
            [image.shape[1], image.shape[0], image.shape[1], image.shape[0]]
        )
        (startX, startY, endX, endY) = box.astype("int")
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

# Display the image with detected faces
cv2.imshow("Detected Faces", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
