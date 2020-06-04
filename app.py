from flask import Flask,request,render_template,url_for,session,redirect
import bcrypt
import pymongo
from pymongo import MongoClient
from keras.models import load_model
global model,graph
import tensorflow as tf
import numpy as np

model=load_model("models/mpg_predict.h5")
graph = tf.get_default_graph()

app = Flask(__name__)
cluster = MongoClient("mongodb+srv://goutham:gnq316@cluster0-hjfqn.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["db"]
collection = db["user"]
collection_vehicle = db["vehicle"]

@app.route('/',methods=['POST','GET'])
def index():

      if 'username' in session:
            #return 'you are logged in as '+session['username']
            if request.method == 'POST':
                  collection_vehicle.insert_one({'mpg':request.form['mpg'],'cylinders':request.form['cylinders'],'displacement':request.form['displacement'],'horsepower':request.form['horsepower'],'weight':request.form['weight'],'accelaration':request.form['accelaration'],'model year':request.form['model_year'],'origin':request.form['origin']})
                  return render_template('show_data.html',results = collection_vehicle.find())
            return render_template('show_data.html',results = collection_vehicle.find(),task="database")
      return render_template('login.html',flag=0,task="database")

@app.route('/predict',methods=['POST','GET'])
def predict():
      if request.method == 'POST':
                global graph
                with graph.as_default():
                   y_predict = model.predict(np.array([[request.form['cylinders'],request.form['displacement'],request.form['horsepower'],request.form['weight'],request.form['accelaration'],request.form['model_year'],request.form['origin']]]))   
                   return render_template('predict.html',predicted_value=str(y_predict[0][0]),task="predict")
      else:
            return render_template("predict.html",task="predict")

@app.route('/delete')
def delete():
      collection.remove({"username":session['username']})
      return render_template("login.html")

@app.route('/settings',methods=['POST','GET'])
def settings():
      if request.method == 'POST':
            collection.update_one({"username":session["username"]},{"$set":{'username':request.form['username'],'first_name':request.form['first_name'],'last_name':request.form['last_name']}})
            session['username'] = request.form['username']
            if(request.form['phone'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"phone":request.form['phone']}})
            if(request.form['city'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"city":request.form['city']}})
            if(request.form['state'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"state":request.form['state']}})
            if(request.form['address'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"address":request.form['address']}})
            res = collection.find({"username":session['username']})
            return render_template("settings.html",res=res,res2=res,task="settings")
      res = collection.find({"username":session['username']})
      return render_template("settings.html",res=res,res2=res,task="settings")



@app.route('/login',methods=['POST'])
def login():
      user = collection.find_one({'username':request.form['username']})

      if user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),user['password']) == user['password']:
                  session['username'] = request.form['username']
                  return redirect(url_for('index'))
      return render_template('login.html',flag=1)
      
@app.route('/register',methods=['POST','GET'])
def register():
      if request.method == 'POST':
            existing_user = collection.find({"username":request.form['username']})
            
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
            collection.insert_one({'username':request.form['username'],'password':hashpass,'first_name':request.form['first_name'],'last_name':request.form['last_name']})
            if(request.form['phone'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"phone":request.form['phone']}})
            if(request.form['city'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"city":request.form['city']}})
            if(request.form['state'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"state":request.form['state']}})
            if(request.form['address'] != ""):
                  collection.update_one({"username":request.form['username']},{"$set":{"address":request.form['address']}})
            
            session['username'] = request.form['username']
            return redirect(url_for('index'))
      #return 'Username already exists!'
      return render_template('register.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run()