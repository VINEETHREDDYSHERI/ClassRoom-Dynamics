import boto3
from botocore.exceptions import ClientError
import cv2
import urllib
import json
from datetime import datetime
from time import sleep
import pymysql

def capture_images(path,id):
    obj=datetime.now()
    name="image_"+str(id)+"_"+str(obj.year)+"_"+str(obj.month)+"_"+str(obj.day)+"_"+str(obj.hour)+"_"+str(obj.minute)+"_"+str(obj.second)+".jpeg"
    webcam=cv2.VideoCapture(0)
    ret,frame=webcam.read()
    print("writing images..")
    cv2.imwrite(path+name,frame)
    webcam.release()
    return (path,name,id)

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
    except ClientError as e:
        print(str(e))
        #logging.error(e)
        return False
    return True

def main():
    host="major-project.csgfvfcvbaj9.ap-south-1.rds.amazonaws.com"
    port=3306
    dbname="majorProject"
    user="admin"
    password="admin12345678"
    i=10
    path="../aws_images_uploads/"
    connection = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname)
    cursor=connection.cursor()
    while i:
        tuple=capture_images(path,1)
        print("capturing done...")
        flag=upload_file(path+tuple[1],'major-project-classroom-images',tuple[1])
        print("aws uploading is done....")
        if flag:
            print("inserting into the images table...")
            cursor.execute("insert into images values(%s,%s,%s,%s)",(tuple[1],1,1,0))
            cursor.execute("commit")
            '''cursor.execute(INSERT INTO `images`(`name`, `class_id`, `period`, `isprocessed`)
                              VALUES (%s,
                                      %s,
                                      %s,
                                      %s),(tuple[1],1,1,0))'''
            print("done inserting into the images table....")
        i=i-1
        sleep(5)

if __name__ == '__main__':
    main()
    print("main function is done....")
