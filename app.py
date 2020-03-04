from flask import Flask, render_template
from flask import jsonify
from flask import request
import pyrebase
import sys
import requests
from utils import *

config = {
    "apiKey": "AIzaSyAVy33QJh9z09h4CH1pJIdLBKTK8NYkEdE",
    "authDomain": "heippi.firebaseapp.com",
    "databaseURL": "https://heippi.firebaseio.com",
    "projectId": "heippi",
    "storageBucket": "heippi.appspot.com",
    "messagingSenderId": "439469049579",
    "appId": "1:439469049579:web:53a89e0e3d29b20ecfe0ae"
  }
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
app = Flask(__name__)
auth.usr_email = None
auth.usr_type = None
auth.usr_cc = None

@app.route("/")
def home():
    return "Home page"

@app.route("/new-pacient")
def new_pacient():
    return render_template("new_pacient.html")

@app.route("/pacient/update", methods=['PUT'])
def pacient_update():
    new_pacient = request.form
    if (auth.current_user is None):
        return jsonify({'message': 'not logged'})
    if (auth.usr_type != "pacient"):
        return jsonify({'message': 'you must be logged as pacient'})
    valid, new_pacient = validate_pacient(new_pacient, "update")
    if (not valid):
        return jsonify({'message': new_pacient + " not valid"})
    else:
        db.child("pacients").child(auth.usr_cc).update(new_pacient)
        return jsonify("updated data")

@app.route("/hospital/update", methods=['PUT'])
def hospital_update():
    new_hospital = request.form
    if (auth.current_user is None):
        return jsonify({'message': 'not logged'})
    if (auth.usr_type != "hospital"):
        return jsonify({'message': 'you must be logged as hospital'})
    valid, new_hospital = validate_hospital(new_hospital, "update")
    if (not valid):
        return jsonify({'message': new_hospital + " not valid"})
    else:
        db.child("hospitals").child(auth.usr_cc).update(new_hospital)
        return jsonify("updated data")

@app.route("/doctor/update", methods=['PUT'])
def doctor_update():
    new_doctor = request.form
    if (auth.current_user is None):
        return jsonify({'message': 'not logged'})
    if (auth.usr_type != "doctor"):
        return jsonify({'message': 'you must be logged as doctor'})
    valid, new_hospital = validate_hospital(new_doctor, "update")
    if (not valid):
        return jsonify({'message': new_doctor + " not valid"})
    else:
        db.child("doctors").child(auth.usr_cc).update(new_doctor)
        return jsonify("updated data")
    
    
    
@app.route("/login", methods=['POST'])
def login():
    user = request.form
    auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
    user_email, user_type, user_cc = get_type_user(db, user)
    if user_email is None:
        return jsonify({'message': 'no identificaction found'})
    try:
        user = auth.sign_in_with_email_and_password(user_email, user['password'])
    except requests.exceptions.HTTPError as e:
            return jsonify(get_http_error(e))
    except TypeError as e:
            return jsonify({'message': "TyperError"})
    except Exception as e:
            return jsonify({'message': "Error"})
    verified = auth.get_account_info(user['idToken'])['users'][0]['emailVerified']
    if (not verified):
        auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
        return jsonify({'message': 'verify your email'})
    else:
        auth.usr_email, auth.usr_type, auth.usr_cc = user_email, user_type, user_cc
        updated = auth.get_account_info(user['idToken'])['users'][0]['passwordUpdatedAt']
        created = auth.get_account_info(user['idToken'])['users'][0]['createdAt']
        if auth.usr_type == "doctor" and str(updated) == str(created):
            auth.send_password_reset_email(auth.usr_email)
            auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
            return jsonify({'message': 'reset your password'})
        return jsonify({'status': "logged"})


@app.route("/new-pacient/add", methods=['POST'])
def add_new_pacient():
    data = request.form
    valid, new_pacient = validate_pacient(data)
    if (not valid):
        return jsonify({'message': new_pacient + " not valid"})
    try:
        user = auth.create_user_with_email_and_password(new_pacient['usr_email'], 
                                                        data['usr_password'])
        auth.send_email_verification(user['idToken'])
        db.child("pacients").child(new_pacient['usr_cc']).set(new_pacient)
        return jsonify("pacient " + new_pacient['usr_email'] + " created" )
    except requests.exceptions.HTTPError as e:
        return jsonify(get_http_error(e))
    except TypeError as e:
        return jsonify({'message': "TyperError"})
    except Exception as e:
        print(e)
        return jsonify({'message': "Error"})
    
@app.route("/new-hospital/add", methods=['POST'])
def add_new_hospital():
    data = request.form
    valid, new_hospital = validate_hospital(data)
    if (not valid):
        return jsonify({'message': new_hospital + " not valid"})
    try:
        user = auth.create_user_with_email_and_password(new_hospital['hosp_email'], 
                                                        new_hospital['hosp_password'])
        auth.send_email_verification(user['idToken'])
        db.child("hospitals").child(new_hospital['hosp_cc']).set(new_hospital)
        return jsonify("hospital " + new_hospital['hosp_email'] + " created" )
    except requests.exceptions.HTTPError as e:
        return jsonify(get_http_error(e))
    except TypeError as e:
        return jsonify({'message': "TyperError"})
    except Exception as e:
        return jsonify({'message': "Error"})


@app.route("/new-doctor/add", methods=['POST'])
def add_new_doctor():
    if auth.usr_type != "hospital":
        return jsonify({'message': 'you must be logged as hospital'})
    new_doctor = request.form
    valid, new_doctor = validate_doctor(new_doctor)
    if (not valid):
        return jsonify({'message': new_doctor + " not valid"})
    try:
        hosp_cc = auth.usr_cc
        user = auth.create_user_with_email_and_password(new_doctor['doc_email'], 
                                                        new_doctor['doc_password'])
        new_doctor['hosp_cc'] = hosp_cc
        db.child("doctors").child(new_doctor['doc_cc']).set(new_doctor)
        db.child("hospitals").child(hosp_cc).child("doctors_cc").update({new_doctor['doc_cc']: new_doctor['doc_cc']})
        auth.send_email_verification(user['idToken'])
        return jsonify("doctor " + new_doctor['doc_email'] + " created" )
    except requests.exceptions.HTTPError as e:
        return jsonify(get_http_error(e))
    except TypeError as e:
        return jsonify({'message': "TyperError"})
    except Exception as e:
        return jsonify({'message': "Error"})

@app.route("/account/reset-password", methods=['POST'])
def reset_password():
    auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
    data = request.form
    user_email, user_type, user_cc = get_type_user(db, data)
    if (user_email is None):
        return jsonify({'message': 'no account found'})
    try:
        auth.send_password_reset_email(user_email)
    except Exception:
        return jsonify({'message': 'error'})
    return jsonify({'message': 'mail sended'})
    
@app.route("/medical-observations/add", methods=['POST'])
def add_medical_observation():
    data = request.form
    if (auth.usr_type != "doctor"):
        return jsonify({'message': 'you must be logged as doctor user'})
    valid, new_obs = validate_obs(db, data)
    if (not valid):
        return jsonify({'message': 'data ' + new_obs + ' invalid'})
    try:
        new_obs['doc_cc'] = auth.usr_cc
        key = db.generate_key()
        db.child('medical_observations').child(key).set(new_obs)
        db.child('doctors').child(new_obs['doc_cc']).child('observations').update({key: key})
        db.child('pacients').child(new_obs['usr_cc']).child('observations').update({key: key})
        db.child('pacients').child(new_obs['usr_cc']).update({'health': new_obs['health']})
    except Exception as e:
        print(e)
        return jsonify({'message': 'error'})
    return jsonify({'message': 'new observation created'})  

@app.route("/medical-observations", methods=['GET'])
def get_medical_observations():
    if auth.usr_cc is None:
        return jsonify({'message': 'you must be logged'})
    data_obs = get_obs_data(db, auth.usr_type, auth.usr_cc)
    if (data_obs is None):
        return jsonify({'message': 'Error'})
    return jsonify(data_obs)

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 3000)