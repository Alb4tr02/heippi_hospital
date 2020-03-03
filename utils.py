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

def get_type_user(db, user):
    try:
        cc = user['cc']
    except KeyError:
        return None, None
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