from datetime import datetime
from flask import Flask,render_template,request,Response,flash,request,redirect,url_for
import cv2
import requests
import os,sys
import urllib.request
from werkzeug.utils import secure_filename
from random import randint
global capture, switch
capture=0
switch=0


try:
    directory = "shots"
    parent_dir = "C:/Users/Gautham/OneDrive/Desktop/PINAK/static"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
except OSError as error:
    pass



app=Flask(__name__)
UPLOAD_FOLDER='static/shots'
app.secret_key='cropdisease'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']=16*1024*1024
ALLOWED_EXTENSIONS=set(['png','jgp','jpeg','gif'])
camera=cv2.VideoCapture(0)
variable_name = randint(0, 100)
variable_name=str(variable_name)
def generate_frames():
    global capture
    while True:
        success,frame=camera.read()
        if success:
            if(capture):
                capture = 0                
                p=os.path.sep.join(['static/shots',"{}.png".format(variable_name)])
                cv2.imwrite(p,frame)

            try:
                ret,buffer=cv2.imencode('.jpg',cv2.flip(frame,1))
                frame=buffer.tobytes()
                yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'+ frame + b'\r\n')
            except Exception as e:
                pass
        else:
            pass  


# app = Flask(__name__) # to make the app run without any


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/input")
def input():
    return render_template("input.html")

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=[ 'POST','GET'])
def tasks():
    global switch,camera
    if request.method =='POST':
        if request.form.get('click')=='Capture Image':
            global capture
            capture=1
        elif  request.form.get('stop') == 'Stop/Start':

                    if(switch==1):
                        switch=0
                        camera.release()
                        cv2.destroyAllWindows()

                    else:
                        camera = cv2.VideoCapture(0)
                        switch=1
        return redirect("/display")
    elif request.method=='GET':
        return render_template('display.html')      
                          
    return render_template('display.html')   

@app.route('/upload',methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)
    file=request.files['file']
    if file.filename == '':
        flash("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename=secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        flash("Image succesfully uploaded and displayed below")
        return render_template('display.html',filename=filename)
    else:
        flash("Allowed image types are - png,jpg,jpeg,gif.")
        return redirect(request.url)

@app.route('/display')
def display_image():
    # files = os.listdir(path)
    # paths = [os.path.join(path, basename) for basename in files]
    # dis_file=max(paths, key=os.path.getctime)
    # print(dis_file)
    return render_template('display.html', variable_name = variable_name)

if __name__ == '__main__':
    app.run(debug=True)