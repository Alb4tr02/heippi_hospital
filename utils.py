from pdf import pdf

def get_http_error(http_error):
    err_json = {}
    err = str(http_error)
    st = err.find("message")
    end = err.find(",", st, (len(err) - 1))
    err = err[st - 1: end]
    st = err.find(":") + 3
    err_json['message'] =  err[st : -1]
    print(err_json)
    return(err_json)

def validate_pacient(data, mode=""):
    contents = ["usr_cc", "usr_date_birth", "usr_name", "usr_addr", "usr_email", "usr_phone"]
    mandatory = ["usr_cc", "usr_email", "usr_phone"]
    optional = ["usr_date_birth","usr_name", "usr_addr"]
    new_data = {}
    keys = list(data.keys())
    if mode == "update":
        for value in optional:
            if (value in keys):
                new_data[value] = data[value]
        return (True, new_data)
    else:
        for value in contents:
            if (value in keys and len(data[value]) > 0):
                new_data[value] = data[value]
            elif value in mandatory:
                return (False, value)
        return (True, new_data)

def validate_doctor(data, mode=""):
    contents = ["doc_cc", "doc_name", "doc_email", "doc_phone", "doc_password"]
    mandatory = ["doc_cc", "doc_email", "doc_phone", "doc_password"]
    optional = ["doc_name"]
    new_data = {}
    keys = list(data.keys())
    if mode == "update":
        for value in optional:
            if (value in keys):
                new_data[value] = data[value]
        return (True, new_data)
    else:
        for value in contents:
            if (value in keys and len(data[value]) > 0):
                new_data[value] = data[value]
            elif value in mandatory:
                return (False, value)
        return (True, new_data)

def validate_hospital(data, mode=""):
    contents = ["hosp_cc", "hosp_services", "hosp_name", "hosp_addr", "hosp_email", "usr_phone", "hosp_password"]
    mandatory = ["hosp_cc", "hosp_email", "hosp_phone"]
    optional = ["hosp_services", "hosp_name", "hosp_addr"]
    new_data = {}
    keys = list(data.keys())
    if mode == "update":
        for value in optional:
            if (value in keys):
                new_data[value] = data[value]
        return (True, new_data)
    else:
        for value in contents:
            if (value in keys and len(data[value]) > 0):
                new_data[value] = data[value]
            elif value in mandatory:
                return (False, value)
        return (True, new_data)

def validate_obs(db, data):
    contents = ['health', 'observations', 'especiality', 'usr_cc']
    keys = list(data.keys())
    new_data = {}
    for value in contents:
        if (value in keys and len(data[value]) > 0):
            new_data[value] = data[value]
        else:
            return (False, value)
    pacient = db.child("pacients").child(new_data['usr_cc']).get()
    if (pacient.val() is None):
        return (False, 'usr_cc') 
    return (True, new_data)

def get_type_user(db, user):
    try:
        cc = user['cc']
    except KeyError:
        return None, None, None
    user_data = db.child("hospitals").child(cc).get()
    if (user_data.val() is not None):
        email = user_data.val()['hosp_email']
        return email, "hospital", cc
    user_data = db.child("pacients").child(cc).get()
    if (user_data.val() is not None):
        email = user_data.val()['usr_email']
        return email, "pacient", cc
    user_data = db.child("doctors").child(cc).get()
    if (user_data.val() is not None):
        email = user_data.val()['doc_email']
        return email, "doctor", cc
    return None, None, None

def get_pacient_obs(db, cc):
    try:
        obs = db.child("pacients").child(cc).child("observations").get()
        name = db.child("pacients").child(cc).get().val()['usr_name']
        obs = obs.val().keys()
        l_dict = []
        for key in obs:
            aux_dict = {}
            aux = db.child("medical_observations").child(key).get().val()
            doctor = db.child("doctors").child(aux['doc_cc']).get().val()
            aux_dict['doctor'] = doctor['doc_name']
            aux_dict['hospital'] = db.child("hospitals").child(doctor['hosp_cc']).get().val()['hosp_name']
            aux_dict['especiality'] = aux['especiality']
            aux_dict['details'] = aux['observations']
            l_dict.append(aux_dict)
        all_data = {'usr_name': name, 'data': l_dict} 
        return all_data
    except Exception:
        return None
    

def get_doctor_obs(db, cc):
    try:
        obs = db.child("doctors").child(cc).child("observations").get()
        doc = db.child("doctors").child(cc).get().val()
        obs = obs.val().keys()
        l_dict = []
        for key in obs:
            aux_dict = {}
            aux = db.child("medical_observations").child(key).get().val()
            pacient = db.child("pacients").child(aux['usr_cc']).get().val()
            aux_dict['pacient'] = pacient['usr_name']
            aux_dict['hospital'] = db.child("hospitals").child(
                doc['hosp_cc']).get().val()['hosp_name']
            aux_dict['especiality'] = aux['especiality']
            aux_dict['details'] = aux['observations']
            l_dict.append(aux_dict)
            return {'doc_name': doc['doc_name'], 'data': l_dict}
    except Exception:
        return None

def get_hospital_obs(db, cc):
    try:
        obs = db.child("hospitals").child(cc).child("doctors_cc").get()
        hosp = db.child("hospitals").child(cc).get().val()
        obs = obs.val().keys()
        l_dict = []
        for key in obs:
            l_dict.append(get_doctor_obs(db, key))
        return {'hosp_name': hosp['hosp_name'], 'data': l_dict}
    except Exception:
        return None

def get_obs_data(db, user_type, cc):
    if user_type == "pacient":
        return get_pacient_obs(db, cc)
    if user_type == "doctor":
        return get_doctor_obs(db, cc)
    if user_type == "hospital":
        return get_hospital_obs(db, cc)
    return None

def get_pdf_pacient(db, cc):
    data = get_pacient_obs(db, cc)
    print("**************")
    print(cc)
    print(data)
    if data is None:
        return None
    route = pdf(data)
    return route
