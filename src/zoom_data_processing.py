import sys
import cv2
from keras.models import load_model
import numpy as np
import boto3
from botocore.exceptions import ClientError
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.inference import load_image
from utils.preprocessor import preprocess_input
from utils.inference import get_image
from utils.inference import getKeypoints
from utils.inference import getValidPairs
from utils.inference import getPersonwiseKeypoints
from utils.inference import raisedHand
from utils.inference import turnedBack
from utils.inference import leftHeadTurn
from utils.inference import rightHeadTurn
from utils.inference import classStatus
import pymysql
from queue import Queue



def main():

    protoFile = "C:\\Users\\asus\\Documents\\major_project\\Project\\openpose-master\\openpose-master\\models\\pose\\coco\\pose_deploy_linevec.prototxt"
    weightsFile = "C:\\Users\\asus\\Documents\\major_project\\Project\\openpose-master\\openpose-master\\models\\pose\\coco\\pose_iter_440000.caffemodel"
    nPoints = 18
    # COCO Output Format
    keypointsMapping = ['Nose', 'Neck', 'R-Sho', 'R-Elb', 'R-Wr', 'L-Sho', 'L-Elb', 'L-Wr', 'R-Hip', 'R-Knee', 'R-Ank', 'L-Hip', 'L-Knee', 'L-Ank', 'R-Eye', 'L-Eye', 'R-Ear', 'L-Ear']

    POSE_PAIRS = [[1,2], [1,5], [2,3], [3,4], [5,6], [6,7],
                  [1,8], [8,9], [9,10], [1,11], [11,12], [12,13],
                  [1,0], [0,14], [14,16], [0,15], [15,17],
                  [2,17], [5,16] ]

    # index of pafs correspoding to the POSE_PAIRS
    # e.g for POSE_PAIR(1,2), the PAFs are located at indices (31,32) of output, Similarly, (1,5) -> (39,40) and so on.
    mapIdx = [[31,32], [39,40], [33,34], [35,36], [41,42], [43,44],
              [19,20], [21,22], [23,24], [25,26], [27,28], [29,30],
              [47,48], [49,50], [53,54], [51,52], [55,56],
              [37,38], [45,46]]

    colors = [ [0,100,255], [0,100,255], [0,255,255], [0,100,255], [0,255,255], [0,100,255],
             [0,255,0], [255,200,100], [255,0,255], [0,255,0], [255,200,100], [255,0,255],
             [0,0,255], [255,0,0], [200,200,0], [255,0,0], [200,200,0], [0,0,0]]

    detection_model_path = 'C:\\Users\\asus\\Documents\\major_project\\Project\\face_classification-master\\face_classification-master\\trained_models\\detection_models\\haarcascade_frontalface_default.xml'
    emotion_model_path = 'C:\\Users\\asus\\Documents\\major_project\\Project\\face_classification-master\\face_classification-master\\trained_models\\emotion_models\\fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')
    font = cv2.FONT_HERSHEY_SIMPLEX
    # hyper-parameters for bounding boxes shape
    emotion_offsets = (20, 40)
    emotion_offsets = (0, 0)
    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)
    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    for vin in range(15):
        # parameters for loading data and images
        image_path = 'C:\\Users\\asus\\Documents\\major_project\\test_zoom_data\\test'+str(vin+1)+'.png' #sys.argv[1]

        # loading images
        rgb_image = load_image(image_path, grayscale=False)
        gray_image = load_image(image_path, grayscale=True)
        gray_image = np.squeeze(gray_image)
        gray_image = gray_image.astype('uint8')

        faces = detect_faces(face_detection, gray_image)
        cat_count={'angry':0,'disgust':0,'fear':0,'happy':0,'sad':0,'surprise':0,'neutral':0}
        total_count=0
        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]

            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
            emotion_text = emotion_labels[emotion_label_arg]
            cat_count[emotion_text]=cat_count[emotion_text]+1
            total_count=total_count+1
            color=(255,0,0)
            draw_bounding_box(face_coordinates, rgb_image, color)
            draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -50, 1, 2)
        #cv2.imwrite("../pose_images/"+image_name,rgb_image)
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite('C:\\Users\\asus\\Documents\\major_project\\zoom_processed\\test_e_p'+str(vin+1)+'.png', bgr_image)


        #pose estimation code........
        image1=cv2.imread(image_path)
        frameWidth=image1.shape[1]
        frameHeight=image1.shape[0]
        #t = time.time()
        net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

        # Fix the input Height and get the width according to the Aspect Ratio
        inHeight = 368
        inWidth = int((inHeight/frameHeight)*frameWidth)

        inpBlob = cv2.dnn.blobFromImage(image1, 1.0 / 255, (inWidth, inHeight),
                                  (0, 0, 0), swapRB=False, crop=False)

        net.setInput(inpBlob)
        output = net.forward()
        #print("Time Taken in forward pass = {}".format(time.time() - t))

        detected_keypoints = []
        keypoints_list = np.zeros((0,3))
        keypoint_id = 0
        threshold = 0.1
        keypoint_location={}
        for part in range(nPoints):
            probMap = output[0,part,:,:]
            probMap = cv2.resize(probMap, (image1.shape[1], image1.shape[0]))
            keypoints = getKeypoints(probMap, threshold)
            print("Keypoints - {} : {}".format(keypointsMapping[part], keypoints))
            keypoints_with_id = []
            for i in range(len(keypoints)):
                keypoints_with_id.append(keypoints[i] + (keypoint_id,))
                keypoints_list = np.vstack([keypoints_list, keypoints[i]])
                keypoint_location[keypoint_id]=keypoints[i]
                keypoint_id += 1
            detected_keypoints.append(keypoints_with_id)


        frameClone = image1.copy()
        for i in range(nPoints):
            for j in range(len(detected_keypoints[i])):
                cv2.circle(frameClone, detected_keypoints[i][j][0:2], 5, colors[i], -1, cv2.LINE_AA)
                        #cv2.imshow("Keypoints",frameClone)

        valid_pairs, invalid_pairs = getValidPairs(output,frameWidth,frameHeight,mapIdx,detected_keypoints,POSE_PAIRS)
        personwiseKeypoints = getPersonwiseKeypoints(valid_pairs, invalid_pairs,keypoints_list,mapIdx,POSE_PAIRS)
        for i in range(17):
            for n in range(len(personwiseKeypoints)):
                index = personwiseKeypoints[n][np.array(POSE_PAIRS[i])]
                if -1 in index:
                    continue
                B = np.int32(keypoints_list[index.astype(int), 0])
                A = np.int32(keypoints_list[index.astype(int), 1])
                cv2.line(frameClone, (B[0], A[0]), (B[1], A[1]), colors[i], 3, cv2.LINE_AA)
        cv2.imwrite("C:\\Users\\asus\\Documents\\major_project\\zoom_processed\\test_p_p"+str(vin+1)+".png",frameClone)
        class_status=classStatus(personwiseKeypoints,keypoint_location)
        with open('C:\\Users\\asus\\Documents\\major_project\\zoom_processed\\test_m'+str(vin+1)+".txt",'a') as f:
            for key in class_status.keys():
                f.write(key+":"+str(class_status[key])+"\n")
        print(class_status)


if __name__ == '__main__':
    main()
