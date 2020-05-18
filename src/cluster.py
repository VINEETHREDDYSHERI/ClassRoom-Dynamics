from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
import numpy as np
import pandas as pd
import os
import cv2
workers = 0 if os.name == 'nt' else 4

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device,keep_all=True
)

resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

count=0
def detectFacePosition(imagePath):
    image =cv2.imread(imagePath)
    image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    boxes, _ = mtcnn.detect(image)
    return (image,boxes)

def generateFacePart(testImage,positionOfFaces,destinationFolderPath):
    global count
    copyTestImage=cv2.cvtColor(testImage,cv2.COLOR_RGB2BGR)
    for (x,y,w,h) in positionOfFaces:
        if(x>=0 and y>=0):
          temp=copyTestImage[int(y):int(h),int(x):int(w)]
          path="/image-"+str(count)+".png"
          cv2.imwrite(destinationFolderPath+path,temp)
          count=count+1
    return count
def start(imageFolderPath,destinationFolderPath):
    print("started processing......\n")
    for fileName in os.listdir(imageFolderPath):
        if(os.path.isfile(imageFolderPath+"/"+fileName)):
            print("generation of faces in the file" +fileName+"started... \n")
            details=detectFacePosition(imageFolderPath+"/"+fileName)
            c=generateFacePart(details[0],details[1],destinationFolderPath)
            print("completed the generation processing of the file "+fileName+"\n")
    print("processing done.Check the folder "+destinationFolderPath+" for generated images")

def FindTensor(imagePath):
    x=[]
    aligned=[]
    image =cv2.imread(imagePath)
    image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    k,y,z=image.shape
    if k>=100 and y>=100:
      x_aligned, prob = mtcnn(image, return_prob=True)
      if x_aligned is not None:
        aligned=x_aligned
        for i in aligned:
          x.append(i)
        return (image,x,True)
    return(image,x,False)

def enconding(imageFolderPath):
    print("started processing......\n")
    encoded_face=[]
    img=[]
    for fileName in os.listdir(imageFolderPath):
        if(os.path.isfile(imageFolderPath+"/"+fileName)):
            print("generation of faces in the file" +fileName+"started... \n")
            details=FindTensor(imageFolderPath+"/"+fileName)
            if(details[2]==True):
              aligned = torch.stack(details[1]).to(device)
              embeddings = resnet(aligned).detach().cpu()
              encoded_face.extend(embeddings)
              img.append(fileName)
            print("completed the generation processing of the file "+fileName+"\n")
    print("processing done.Check the folder for generated images")
    return encoded_face,img

#def save_cluster(imageFolderPath,images_list):


start("./images_train","./faces")

enc,img=enconding("./faces")
aligned = torch.stack(enc).to(device)

from sklearn.cluster import DBSCAN
clt = DBSCAN(metric="euclidean",eps=0.5,min_samples=3)
clt.fit(aligned)
clt.labels_
labelIDs = np.unique(clt.labels_)
numUniqueFaces = len(labelIDs)
print(numUniqueFaces)
i=0
dir_count=1
for val in clt.labels_:
    if(val==1):
        print(img[i])
    i=i+1
i=0
for val in clt.labels_:
    if(val==-1):
        i=i+1
i
