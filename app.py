from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, os.path
import shutil


from threading import Timer

from flask import make_response

import random
import string

import boto3
import json
import os

import io

from time import sleep

app = Flask(__name__,static_folder=os.path.abspath('static'))


def generate_info(bucketname, filename):
    rekognition_clinet = boto3.client('rekognition', 'us-east-1')
    response = rekognition_clinet.detect_faces(
        Image={
                'S3Object':{
                'Bucket':bucketname,
                'Name':filename
                }
            },
        Attributes=['ALL']
        )
    for face in response['FaceDetails']:
        outputs = json.dumps(face, indent=4,sort_keys=True)
    return outputs


def delete_images(obj,file):
    print('hello')
    os.remove(file)
    obj.delete()
                    

@app.route('/')
def upload_file():
   return render_template('index.html')
    
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        bucketname = 'resultcontent'
        if f:
            filename = secure_filename(f.filename)
            f.save(filename)
            boto_client = boto3.client('s3')

            #uploads file
            boto_client.upload_file(filename, bucketname,filename)
        
        s3 = boto3.resource('s3')
        obj = s3.Object(bucketname, filename)

        


        
        output = generate_info(bucketname, filename)
        y = json.loads(output)
        
        gender = y['Gender']['Value']
        high = y['AgeRange']['High']
        low = y['AgeRange']['Low']

        values = []
        for value in y['Emotions']:
            values.append(value['Confidence'])
        emotion = y['Emotions'][values.index(max(values))]['Type']
        eyeglass = y['Eyeglasses']['Value']


        img_src = f"https://{bucketname}.s3.amazonaws.com/{filename}"

        response = make_response(render_template('result.html', image_names = img_src, gender= gender, high = high, low=low,emotion=emotion, eyeglass=eyeglass))

        t = Timer(20 , lambda: delete_images(obj,filename))
        t.start()


    return response
        

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    app.run(debug = True)
