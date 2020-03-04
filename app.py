from flask import Flask, render_template
from flask import jsonify, request, make_response
from flask import send_file, send_from_directory, safe_join, abort
import os
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

@app.route("/pacient/update", methods=['PUT'])
def pacient_update():
    new_pacient = request.form
    if (auth.current_user is None):
        return make_response(jsonify({'message': 'not logged'}), 401)
    if (auth.usr_type != "pacient"):
        return make_response(jsonify({'message': 'you must be logged as pacient'}), 403)
    valid, new_pacient = validate_pacient(new_pacient, "update")
    if (not valid):
        return make_response(jsonify({'message': new_pacient + " not valid"}), 400)
    else:
        db.child("pacients").child(auth.usr_cc).update(new_pacient)
        return make_response(jsonify("updated data"), 200)

@app.route("/hospital/update", methods=['PUT'])
def hospital_update():
    new_hospital = request.form
    if (auth.current_user is None):
        return make_response(jsonify({'message': 'not logged'}), 401)
    if (auth.usr_type != "hospital"):
        return make_response(jsonify({'message': 'you must be logged as hospital'}), 403)
    valid, new_hospital = validate_hospital(new_hospital, "update")
    if (not valid):
        return make_response(jsonify({'message': new_hospital + " not valid"}), 400)
    else:
        db.child("hospitals").child(auth.usr_cc).update(new_hospital)
        return make_response(jsonify("updated data"), 200)

@app.route("/doctor/update", methods=['PUT'])
def doctor_update():
    new_doctor = request.form
    if (auth.current_user is None):
        return make_response(jsonify({'message': 'not logged'}), 401)
    if (auth.usr_type != "doctor"):
        return make_response(jsonify({'message': 'you must be logged as doctor'}), 403)
    valid, new_hospital = validate_hospital(new_doctor, "update")
    if (not valid):
        return make_response(jsonify({'message': new_doctor + " not valid"}), 400)
    else:
        db.child("doctors").child(auth.usr_cc).update(new_doctor)
        return make_response(jsonify("updated data"), 200)
    
    
    
@app.route("/login", methods=['POST'])
def login():
    user = request.form
    auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
    user_email, user_type, user_cc = get_type_user(db, user)
    if user_email is None:
        return make_response(jsonify({'message': 'no identificaction found'}), 404)
    try:
        user = auth.sign_in_with_email_and_password(user_email, user['password'])
    except requests.exceptions.HTTPError as e:
            return make_response(jsonify(get_http_error(e)), 400)
    except TypeError as e:
            return make_response(jsonify({'message': "TyperError"}), 500)
    except requests.exceptions.ConnectionError:
        return make_response(jsonify({'message': 'Conection failed'}), 504)
    except Exception as e:
            return make_response(jsonify({'message': "Error"}), 400)
    verified = auth.get_account_info(user['idToken'])['users'][0]['emailVerified']
    if (not verified):
        auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
        return make_response(jsonify({'message': 'verify your email'}), 401)
    else:
        auth.usr_email, auth.usr_type, auth.usr_cc = user_email, user_type, user_cc
        updated = auth.get_account_info(user['idToken'])['users'][0]['passwordUpdatedAt']
        created = auth.get_account_info(user['idToken'])['users'][0]['createdAt']
        if auth.usr_type == "doctor" and str(updated) == str(created):
            auth.send_password_reset_email(auth.usr_email)
            auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
            return make_response(jsonify({'message': 'reset your password'}), 401)
        return make_response(jsonify({'status': "logged"}), 200)


@app.route("/new-pacient/add", methods=['POST'])
def add_new_pacient():
    data = request.form
    valid, new_pacient = validate_pacient(data)
    if (not valid):
        return make_response(jsonify({'message': new_pacient + " not valid"}), 400)
    try:
        test = db.child("pacients").child(new_pacient['usr_cc']).get().val()
        if test is not None:
            return  make_response(jsonify({'message': 'identification not valid'}), 400)
        user = auth.create_user_with_email_and_password(new_pacient['usr_email'], 
                                                        data['usr_password'])
        auth.send_email_verification(user['idToken'])
        db.child("pacients").child(new_pacient['usr_cc']).set(new_pacient)
        return make_response(jsonify("pacient " + new_pacient['usr_email'] + " created" ), 200)
    except requests.exceptions.HTTPError as e:
        return make_response(jsonify(get_http_error(e)), 500)
    except TypeError as e:
        return make_response(jsonify({'message': "TyperError"}), 500)
    except Exception as e:
        return make_response(jsonify({'message': "Error"}), 500)
    
@app.route("/new-hospital/add", methods=['POST'])
def add_new_hospital():
    data = request.form
    valid, new_hospital = validate_hospital(data)
    if (not valid):
        return make_response(jsonify({'message': new_hospital + " not valid"}), 400)
    try:
        test = db.child("hospitals").child(new_hospital['hosp_cc']).get().val()
        if test is not None:
            return  make_response(jsonify({'message': 'identification not valid'}), 400)
        user = auth.create_user_with_email_and_password(new_hospital['hosp_email'], 
                                                        new_hospital['hosp_password'])
        auth.send_email_verification(user['idToken'])
        db.child("hospitals").child(new_hospital['hosp_cc']).set(new_hospital)
        return make_response(jsonify("hospital " + new_hospital['hosp_email'] + " created" ), 200)
    except requests.exceptions.HTTPError as e:
        return make_response(jsonify(get_http_error(e)), 500)
    except TypeError as e:
        return make_response(jsonify({'message': "TyperError"}), 500)
    except Exception as e:
        return make_response(jsonify({'message': "Error"}))


@app.route("/new-doctor/add", methods=['POST'])
def add_new_doctor():
    if auth.usr_type != "hospital":
        return make_response(jsonify({'message': 'you must be logged as hospital'}), 401)
    new_doctor = request.form
    valid, new_doctor = validate_doctor(new_doctor)
    if (not valid):
        return make_response(jsonify({'message': new_doctor + " not valid"}), 403)
    try:
        test = db.child("doctors").child(new_doctor['doc_cc']).get().val()
        if test is not None:
            return  jsonify({'message': 'identification not valid'})
        hosp_cc = auth.usr_cc
        user = auth.create_user_with_email_and_password(new_doctor['doc_email'], 
                                                        new_doctor['doc_password'])
        new_doctor['hosp_cc'] = hosp_cc
        db.child("doctors").child(new_doctor['doc_cc']).set(new_doctor)
        db.child("hospitals").child(hosp_cc).child("doctors_cc").update({new_doctor['doc_cc']: new_doctor['doc_cc']})
        auth.send_email_verification(user['idToken'])
        return make_response(jsonify("doctor " + new_doctor['doc_email'] + " created" ), 200)
    except requests.exceptions.HTTPError as e:
        return jsonify(get_http_error(e))
    except TypeError as e:
        return make_response(jsonify({'message': "TyperError"}), 500)
    except Exception as e:
        return make_response(jsonify({'message': "Error"}), 500)

@app.route("/account/reset-password", methods=['POST'])
def reset_password():
    auth.current_user, auth.usr_email, auth.usr_type, auth.usr_cc = None, None, None, None
    data = request.form
    user_email, user_type, user_cc = get_type_user(db, data)
    if (user_email is None):
        return make_response(jsonify({'message': 'no account found'}), 400)
    try:
        auth.send_password_reset_email(user_email)
    except Exception:
        return make_response(jsonify({'message': 'error'}), 500)
    return make_response(jsonify({'message': 'mail sended'}), 200)
    
@app.route("/medical-observations/add", methods=['POST'])
def add_medical_observation():
    data = request.form
    if (auth.usr_type != "doctor"):
        return make_response(jsonify({'message': 'you must be logged as doctor user'}), 403)
    valid, new_obs = validate_obs(db, data)
    if (not valid):
        return make_response(jsonify({'message': 'data ' + new_obs + ' invalid'}), 400)
    try:
        new_obs['doc_cc'] = auth.usr_cc
        key = db.generate_key()
        db.child('medical_observations').child(key).set(new_obs)
        db.child('doctors').child(new_obs['doc_cc']).child('observations').update({key: key})
        db.child('pacients').child(new_obs['usr_cc']).child('observations').update({key: key})
        db.child('pacients').child(new_obs['usr_cc']).update({'health': new_obs['health']})
    except Exception as e:
        return make_response(jsonify({'message': 'error'}), 500)
    return make_response(jsonify({'message': 'new observation created'})  , 200)

@app.route("/medical-observations", methods=['GET'])
def get_medical_observations():
    if auth.usr_cc is None:
        return make_response(jsonify({'message': 'you must be logged'}), 401)
    data_obs = get_obs_data(db, auth.usr_type, auth.usr_cc)
    if (data_obs is None):
        return make_response(jsonify({'message': 'Error'}), 404)
    return make_response(jsonify(data_obs), 200)

@app.route("/medical-observations/<cc>", methods=['GET'])
def get_pdf_observations(cc):
    if auth.usr_cc is None:
        return make_response(jsonify({'message': 'you must be logged'}), 401)
    if auth.usr_type != "doctor":
        return make_response(jsonify({'message': 'you must be logged as doctor user'}), 403)
    route = get_pdf_pacient(db, cc)
    if (route is None):
        return make_response(jsonify({'message': 'Error'}), 404)
    try:
        return send_from_directory(os.getcwd(), "pacient.pdf", as_attachment=True)
    except Exception:
        abort(404)
    return send_file(route)

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 3000)