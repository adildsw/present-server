# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 23:21:37 2020

@author: AdilDSW
"""
# Standard Built-in Libraries
import csv
import math
from datetime import timedelta, datetime
from bcrypt import checkpw

# 3rd-party Libraries
from flask import Flask, request, render_template, session, redirect, url_for
from flask_qrcode import QRcode

# Local Modules
from utils import status_code
from utils import read_config, write_config, delete_config
from database import PresentDatabaseInterface as PDI


# Creating Flask object
app = Flask(__name__, static_folder="web/", template_folder="web/")
app.secret_key = "present_newest_secret_key"
QRcode(app)

pdi = PDI() # Creating database interface object

# Initializing database configuration values if present
config = read_config()
if config:
    pdi.init_values(config['ip'], config['port'], config['user'], 
                    config['pwd'], config['authdb'])


@app.before_request
def session_expiry():
    """Deals with session expiry and redirection to login page."""
    current_time = datetime.now()
    try:
        last_active = session['last_active']
        delta = current_time - last_active
        if delta > timedelta(minutes=20):
            session['last_active'] = current_time
            session['username'] = None
            return redirect("/")
    except:
        pass
    
    try:
        session['last_active'] = current_time
    except:
        pass


@app.before_request
def username_session():
    """Creates an empty username session if it is not initialized."""
    if 'username' not in session:
        session['username'] = None
    
 
"""
|-----------------------------------------------------------------------------
| In-App Routing for System Navigation
|-----------------------------------------------------------------------------
|
| This section contains routing rules for rendering different sections of the
| attendance management system.
|
"""


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    """"Loads index.html as the system root page which displays a loader. This
    page sends a request to assimilate the server state, and then the page is 
    redirected accordingly.
    """
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """Dashboard Page"""
    if session['username'] == "admin":
        return render_template("admindash.html")
    elif session['username'] == None:
        return redirect(url_for("home"))
    else:
        faculty_res = get_faculty_list()
        faculty_name = faculty_res['faculty_name'][faculty_res['faculty_code'].
                                                   index(session['username'])]     
        return render_template("facultydash.html", 
                               faculty_name=faculty_name.split(" ")[0])


@app.route("/login")
def login_page():
    """Login Page"""
    if not session['username']:
        return render_template("loader.html", server_code=2, 
                               org_name=get_org_name())
    else:
        return redirect(url_for("home"))


@app.route("/configuredb")
def configure_db_page():
    """Database Configuration Page"""
    config = read_config()
    if not config:
        return render_template("loader.html", server_code=0, org_name=None)
    else:
        db = pdi.check_db_connection()
        if db['connected']:
            return redirect(url_for("home"))
        else:
            return render_template("loader.html", server_code=3, org_name=None)


@app.route("/registerorg")
def register_org_page():
    """Organization Registration Page"""
    org_name = get_org_name()
    if org_name:
        return redirect(url_for("home"))
    else:
        return render_template("loader.html", server_code=1, org_name=org_name)


@app.route("/index.html")
@app.route("/loader.html")
@app.route("/admindash.html")
@app.route("/admindash/department.html")
@app.route("/admindash/faculty.html")
def error():
    """Blocks all direct HTML file access by returning ERROR 404."""
    return "ERROR 404: The page you're looking for is unavailable."


"""
|-----------------------------------------------------------------------------
| Service Calls
|-----------------------------------------------------------------------------
|
| This section contains routing rules for various service calls made to the
| server for functionalities like logging in, database connection, organization 
| registration, etc.
|
"""


@app.route("/load", methods=['POST'])
def load():
    """Loader function to assimilate server state and redirect to appropriate
    page.
    
    server_code - (int) decides the server state. Codes are as follows:
        0 => Unconfigured Database
        1 => Unconfigured Server/Organization Not Registered
        2 => Login Page
        3 => Database Connection Issue Page [Retry/Reconfigure]
        4 => Already Logged In

    """
    if request.values.get('reconfig') == "true":
        delete_config()
        server_code = 0
    else:
        config = read_config()
        if not config:
            server_code = 0
        else:
            db_con = pdi.check_db_connection()
            if db_con['connected']:
                if is_org_registered():
                    if session['username']:
                        server_code = 4
                    else:
                        server_code = 2
                else:
                    server_code = 1
            else:
                server_code = 3
    # Redirecting to appropriate route
    if server_code == 0 or server_code == 3:
        return redirect(url_for("configure_db_page"))
    elif server_code == 1:
        return redirect(url_for("register_org_page"))
    elif server_code == 2:
        return redirect(url_for("login_page"))
    elif server_code == 4:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("error"))


@app.route('/connect_db', methods=['POST'])
def connect_db():
    """Establishes connection with database."""
    if request.method == 'POST':
        ip = request.values.get('ip')
        port = request.values.get('port')
        user = request.values.get('user')
        pwd = request.values.get('pwd')
        authdb = request.values.get('authdb')
        
        pdi.init_values(ip, port, user, pwd, authdb)
        res = pdi.check_db_connection()
        if res['connected']:
            write_config(ip, port, user, pwd, authdb)
    else:
        res = {"connected": False, "message": "ERROR: Illegal Service Call"}
    
    return res


@app.route("/admin_dash", methods=['POST'])
def admin_dash():
    """Renders content of administrator dashboard."""
    if session['username'] == "admin":
        nav = request.values.get('navigation')
        if nav == "home":
            return render_template("/admindash/home.html")
        elif nav == "dept":
            dept_res = get_dept_list()
            dept_code, dept_name = dept_res['dept_code'], dept_res['dept_name']
            
            return render_template("/admindash/department.html", 
                                   dept_code=dept_code, dept_name=dept_name)
        elif nav == "faculty":
            faculty_res = get_faculty_list()
            faculty_name = faculty_res['faculty_name']
            faculty_code = faculty_res['faculty_code']
            faculty_dept = faculty_res['faculty_dept']
            
            dept_res = get_dept_list()
            dept_name = dept_res['dept_name']
            
            return render_template("/admindash/faculty.html", 
                                   faculty_name=faculty_name,
                                   faculty_code=faculty_code,
                                   faculty_dept=faculty_dept,
                                   dept_name=dept_name)
        elif nav == "class":
            class_res = get_class_list()
            class_code = class_res['class_code']
            dept_name = class_res['dept_name']
            class_start = class_res['class_start']
            class_end = class_res['class_end']
            class_section = class_res['class_section']
            
            student_count = []
            for idx in range(0, len(class_code)):
                code = class_code[idx]
                student_res = get_student_list(code)
                student_count.append(len(student_res['student_name']))
            
            dept_res = get_dept_list()
            dept_name_list = dept_res['dept_name']
            section = ["-", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
            
            return render_template("/admindash/class.html", section=section,
                                   dept_name_list=dept_name_list, 
                                   class_code=class_code, 
                                   dept_name=dept_name,
                                   class_start=class_start, 
                                   class_end=class_end,
                                   class_section=class_section, 
                                   student_count=student_count);
        elif nav == "student":
            student_res = get_student_list()
            student_roll = student_res['student_roll']
            student_name = student_res['student_name']
            student_class_code = student_res['class_code']
            device_uid = student_res['device_uid']
            device_status = ['Registered' if i else 'Not Registered' 
                             for i in device_uid]
            
            class_res = get_class_list()
            class_code = class_res['class_code']
            
            return render_template("/admindash/student.html",
                                   class_code=class_code, 
                                   student_roll=student_roll, 
                                   student_name=student_name, 
                                   student_class_code=student_class_code, 
                                   device_status=device_status)
        elif nav == "course":
            course_res = get_course_list()
            course_code = course_res['course_code']
            course_name = course_res['course_name']
            course_faculty_code = course_res['faculty_code']
            course_class_code = course_res['class_code']
            course_status = course_res['course_status']
            
            faculty_res = get_faculty_list()
            faculty_code = faculty_res['faculty_code']
            
            class_res = get_class_list()
            class_code = class_res['class_code']
            
            return render_template("/admindash/course.html",
                                   faculty_code=faculty_code, 
                                   class_code=class_code, 
                                   course_code=course_code, 
                                   course_name=course_name, 
                                   course_faculty_code=course_faculty_code, 
                                   course_class_code=course_class_code, 
                                   course_status=course_status)
        else:
            return "ERROR: Incorrect Service Call"
    else:
        return redirect(url_for("home"))


@app.route("/faculty_dash", methods=['POST'])
def faculty_dash():
    """Renders content of faculty dashboard."""
    if session['username'] and session['username'] != "admin":
        nav = request.values.get('navigation')
        
        # Checking if the operating faculty has any sessions left active
        op_faculty_code = session['username']
        session_res = get_session_list(op_faculty_code=op_faculty_code, 
                                       session_status="Active")
        if len(session_res['session_code']) > 0:
            course_info = session_res['course_info'][0]
            session_code = session_res['session_code'][0]
            timestamp = session_res['timestamp'][0]
            nav = "restart_session"
        
        if nav == "fac_course":
            faculty_code = session['username']
            
            course_res = get_course_list(faculty_code)
            course_code = course_res['course_code']
            course_name = course_res['course_name']
            faculty_codes = course_res['faculty_code']
            class_codes = course_res['class_code']
            course_status = course_res['course_status']
            course_info = course_res['course_info']
            
            session_count = []
            for c_info in course_info:
                session_res = get_session_list(c_info, faculty_code)
                session_count.append(len(session_res['session_code']))
            
            return render_template("/facultydash/fac_course.html",
                                   course_code=course_code, 
                                   course_name=course_name, 
                                   faculty_code=faculty_codes, 
                                   class_code=class_codes, 
                                   course_status=course_status,
                                   course_info=course_info,
                                   session_count=session_count)
        elif nav == "start_session":
            course_info = request.values.get('course_info')
            
            course_info_res = course_info.split("|")
            course_code = course_info_res[0]
            course_name = course_info_res[1]
            class_code = course_info_res[3].split(", ")
            class_code = " | ".join(class_code)
            op_faculty_code = session['username']
            
            session_res = start_session(course_info, op_faculty_code)
            session_id = session_res['session_id']
            timestamp = session_res['timestamp']
            date = datetime.utcfromtimestamp(timestamp).strftime('%d/%m/%Y')
            session_code = str(session_id)
            
            if session_res['status'] != "S0":
                return "ERROR: Please Contact Admin"
            
            return render_template("/facultydash/start_session.html",
                                   session_code=session_code,
                                   course_info=course_info,
                                   course_code=course_code, 
                                   course_name=course_name,
                                   faculty_code=op_faculty_code,
                                   class_code=class_code, date=date)
        elif nav == "restart_session":
            course_info_res = course_info.split("|")
            course_code = course_info_res[0]
            course_name = course_info_res[1]
            class_code = course_info_res[3].split(", ")
            class_code = " | ".join(class_code)
            op_faculty_code = session['username']
            date = datetime.utcfromtimestamp(timestamp).strftime('%d/%m/%Y')
            
            if session_res['status'] != "S0":
                return "ERROR: Please Contact Admin"
            
            return render_template("/facultydash/start_session.html",
                                   session_code=session_code,
                                   course_info=course_info,
                                   course_code=course_code, 
                                   course_name=course_name,
                                   faculty_code=op_faculty_code,
                                   class_code=class_code, date=date)
        else:
            return "ERROR: Incorrect Service Call"
    else:
        return redirect(url_for("home"))


@app.route("/gen_qr_img", methods=['POST'])
def gen_qr_img():
    """App route for generating QR Code for attendance session."""
    if session['username'] and session['username'] != "admin":
        qrcode_id = request.values.get('qrcode_id')
        return render_template("/facultydash/components/qrcode_img.html", 
                               qrcode_id=qrcode_id)
    else:
        return "ERROR: Insufficient Privilege"


@app.route("/gen_qr_timestamp", methods=['POST'])
def gen_qr_timestamp():
    """App route for generating the QR Code timestamp for attendance session."""
    if session['username'] and session['username'] != "admin":
        qr_timestamp = request.values.get('qr_timestamp')
        new_timestamp = ""
        
        if qr_timestamp == "":
            timestamp = math.floor(datetime.now().timestamp())
            new_timestamp = timestamp + 5 # Adding a 5 second validity
        else:
            old_timestamp = int(qr_timestamp)
            timestamp = math.floor(datetime.now().timestamp())
            if (timestamp - old_timestamp) > -2:
                new_timestamp = timestamp + 5 # Adding a 5 second validity
            else:
                new_timestamp = old_timestamp
                
        return {'status': "S0", 'message': status_code['S0'], 
                'qr_timestamp': new_timestamp}
    else:
        return {'status': "E8", 'message': status_code['S0'], 
                'qr_timestamp': new_timestamp}


@app.route("/terminate_attendance_session", methods=['POST'])
def terminate_attendance_session():
    """App route for terminating attendance session."""
    if session['username'] and session['username'] != "admin":
        session_code = request.values.get('session_code')
        res = end_session(session_code)
        
        return {'status': res['status'], 'message': res['message']}
    else:
        return {'status': "E8", 'message': status_code['E8']}


@app.route("/share_attendance_controls", methods=['POST'])
def share_attendance_controls():
    """Shares attendance session QRCode with student."""
    student_name = ""
    if session['username'] and session['username'] != "admin":
        student_roll = request.values.get('student_roll')
        class_codes = request.values.get('class_codes').split(" | ")
        session_code = request.values.get('session_code')
        
        student_res = get_student_info(student_roll=student_roll)
        if student_res['status'] == "S0":
            student_name = student_res['student_name']
            class_code = student_res['class_code']
            if class_code in class_codes:
                query = {'session_code': session_code}
                mod_query = {'control_share': student_roll}
                res = pdi.update_data("sessions", query, mod_query)
                status = res['status']
                if status == "S0" and not has_attended(student_roll, session_code):
                    res = give_attendance("faculty", session_code, 
                                          {'student_roll': student_roll})
                    status = res['status']
            else:
                status = "E10"
        else:
            status = student_res['status']
    else:
        status = "E8"
        
    return {'status': status, 'message': status_code[status], 
            'student_name': student_name}


@app.route("/get_attending_students_stats", methods=['POST'])
def attending_students_stats():
    """App route for providing live attending students count feed."""
    if session['username'] and session['username'] != "admin":
        session_code = request.values.get('session_code')
        attending_res = get_attending_students(session_code)
        student_roll = attending_res['student_roll']
        return render_template(
            "/facultydash/components/attending_students_stats.html", 
            student_roll=student_roll)
    else:
        return "ERROR: Insufficient Privilege"
    

@app.route("/get_attending_students_list", methods=['POST'])
def attending_students_list():
    """App route for providing live attending students list feed."""
    if session['username'] and session['username'] != "admin":
        session_code = request.values.get('session_code')
        attending_res = get_attending_students(session_code)
        student_roll = attending_res['student_roll']
        student_name = attending_res['student_name']
        return render_template(
            "/facultydash/components/attending_students_table_body.html", 
            student_roll=student_roll, student_name=student_name)
    else:
        return "ERROR: Insufficient Privilege"


@app.route("/give_attendance", methods=['POST'])
def set_attendance():
    """App route for giving attendance to students."""
    if session['username'] and session['username'] != "admin":
        student_roll = request.values.get('student_roll')
        class_codes = request.values.get('class_codes').split(" | ")
        session_code = request.values.get('session_code')
        
        student_res = get_student_info(student_roll=student_roll)
        if student_res['status'] == "S0":
            class_code = student_res['class_code']
            if class_code in class_codes:
                if not has_attended(student_roll, session_code):
                    res = give_attendance("faculty", session_code, 
                                          {'student_roll': student_roll})
                    status = res['status']
                else:
                    status = "S4"
            else:
                status = "E10"
        else:
            status = student_res['status']
    else:
        status = "E8"
        
    return {'status': status, 'message': status_code[status]}
    
@app.route("/org_reg", methods=['POST'])
def org_reg():
    """Registers organization and administrator credentials to the system."""
    if request.method == 'POST':
        org_name = request.values.get('org_name')
        admin_pwd = request.values.get('admin_pwd')
        
        if is_org_registered():
            status = "E7"
        else:
            data = {'org_name': org_name, 
                    'acc_type': "admin", 
                    # 'acc_pwd': hashpw(admin_pwd.encode(), gensalt())}
                    'acc_pwd': admin_pwd}
            res = pdi.insert_data("details", data)
            status = res['status']
    else:
        status = "E3"
        
    return {'status': status, 'message': status_code[status]}


@app.route("/login_auth", methods=['POST'])
def login_auth():
    """Authenticates user login to the system."""
    if request.method == 'POST':
        user = request.values.get('user')
        pwd = request.values.get('pwd').encode()
        
        if user == "admin":
            hashed_pwd = get_admin_pwd()
        else:
            hashed_pwd = get_faculty_pwd(user)
        
        if hashed_pwd:
            if checkpw(pwd, hashed_pwd):
                status = "S0"
                session['username'] = user
            else:
                status = "E4"
                session['username'] = None
        else:
            status="E4"
    else:
        status = "E3"
        
    return {'status': status, 'message': status_code[status]}


@app.route("/logout", methods=['POST'])
def logout():
    """Logs user out of the system."""
    session['username'] = None
    return redirect(url_for("login_page"))


@app.route("/unregister_device", methods=['POST'])
def unregister_device():
    """Unlinks the device from the student."""
    if session['username'] == "admin":
        student_roll = request.values.get("student_roll")
        query = {'student_roll': student_roll}
        mod_query = {'device_uid': ""}
        update_res = pdi.update_data("students", query, mod_query)
        status = update_res['status']
    else:
        status = "E8"
    
    return {'status': status, 'message': status_code[status]}

"""
|-----------------------------------------------------------------------------
| Insert/Modify/Delete Operations
|-----------------------------------------------------------------------------
|
| This section contains routing rules for various insertion, modification and
| deletion related database operations for various system elements like 
| Departments, Faculties, Class Groups, etc.
|
"""


@app.route("/insert_dept", methods=['POST'])
def insert_dept():
    if session['username'] == "admin":
        dept_name = request.values.get('dept_name')
        dept_code = request.values.get('dept_code')
        data = {'dept_name': dept_name, 'dept_code': dept_code}
        
        res = pdi.insert_data("departments", data)
        status = res['status']
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message}


@app.route('/insert_dept_csv', methods=['POST'])
def insert_dept_csv():
    fail_data_string = ""
    if session['username'] == "admin":
        dept_csv_data = request.values.get('dept_csv')
        dept_csv = list(csv.reader(dept_csv_data.splitlines()))
        head, rows = dept_csv[0], dept_csv[1:]
        data = []
        for row in rows:
            row_data = {}
            for idx in range(len(head)):
                row_data[head[idx]] = row[idx]
            data.append(row_data)
        
        res = pdi.insert_many_data("departments", data)
        status = res['status']
        
        fail_data_string = ""
        for item in res['fail_data']:
            fail_data_string = "{}{}\n".format(fail_data_string, str(item))
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message, 
            'fail_data': fail_data_string}


@app.route("/insert_faculty", methods=['POST'])
def insert_faculty():
    if session['username'] == "admin":
        faculty_name = request.values.get('faculty_name')
        faculty_code = request.values.get('faculty_code')
        faculty_dept = request.values.get('faculty_dept')
        faculty_pwd = request.values.get('faculty_pwd')
        faculty_pwd_cnf = request.values.get('faculty_pwd_cnf')
        
        if faculty_pwd != faculty_pwd_cnf:
            status = "E5"
        else:
            data = {'faculty_name': faculty_name,
                    'faculty_code': faculty_code,
                    'dept_name': faculty_dept,
                    'faculty_pwd': faculty_pwd}
            res = pdi.insert_data("faculties", data)
            status = res['status']
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message}


@app.route('/insert_faculty_csv', methods=['POST'])
def insert_faculty_csv():
    fail_data_string = ""
    if session['username'] == "admin":
        faculty_csv_data = request.values.get('faculty_csv')
        faculty_csv = list(csv.reader(faculty_csv_data.splitlines()))
        head, rows = faculty_csv[0], faculty_csv[1:]
        data = []
        for row in rows:
            row_data = {}
            for idx in range(len(head)):
                row_data[head[idx]] = row[idx]
            data.append(row_data)
        
        res = pdi.insert_many_data("faculties", data)
        status = res['status']
    
        fail_data_string = ""
        for item in res['fail_data']:
            fail_data_string = "{}{}\n".format(fail_data_string, str(item))
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message, 
            'fail_data': fail_data_string}


@app.route("/insert_class", methods=['POST'])
def insert_class():
    if session['username'] == "admin":
        dept_name = request.values.get('dept_name')
        class_start = request.values.get('class_start')
        class_end = request.values.get('class_end')
        class_section = request.values.get('class_section')
        
        dept_res = get_dept_list()
        dept_name_res = dept_res['dept_name']
        dept_code_res = dept_res['dept_code']
        dept_code = dept_code_res[dept_name_res.index(dept_name)]
        
        class_code = "{}_{}_{}_{}".format(dept_code, class_start, class_end, 
                                          class_section)
        
        data = {'class_code': class_code, 'dept_name': dept_name, 
                'class_start': class_start, 'class_end': class_end,
                'class_section': class_section}
        res = pdi.insert_data("classes", data)
        status = res['status']
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message}


@app.route('/insert_class_csv', methods=['POST'])
def insert_class_csv():
    fail_data_string = ""
    if session['username'] == "admin":
        class_csv_data = request.values.get('class_csv')
        class_csv = list(csv.reader(class_csv_data.splitlines()))
        head, rows = class_csv[0], class_csv[1:]
        
        dept_res = get_dept_list()
        dept_name_res = dept_res['dept_name']
        dept_code_res = dept_res['dept_code']
        
        data = []
        for row in rows:
            row_data = {}
            for idx in range(len(head)):
                row_data[head[idx]] = row[idx]
            
            dept_name = row_data['dept_name']
            dept_code = dept_code_res[dept_name_res.index(dept_name)]
            class_code = "{}_{}_{}_{}".format(dept_code, 
                                              row_data['class_start'], 
                                              row_data['class_end'], 
                                              row_data['class_section'])
            row_data['class_code'] = class_code
            data.append(row_data)
        
        res = pdi.insert_many_data("classes", data)
        status = res['status']
        
        fail_data_string = ""
        for item in res['fail_data']:
            fail_data_string = "{}{}\n".format(fail_data_string, str(item))
    else:
        status = "E8"
    
    message = status_code[status]
    return {'status': status, 'message': message, 
            'fail_data': fail_data_string}


@app.route("/insert_student", methods=['POST'])
def insert_student():
    if session['username'] == "admin":
        student_roll = request.values.get('student_roll')
        student_name = request.values.get('student_name')
        class_code = request.values.get('class_code')
        data = {'student_roll': student_roll, 'student_name': student_name,
                'class_code': class_code, 'device_uid': ""}
        
        res = pdi.insert_data("students", data)
        status = res['status']
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message}


@app.route('/insert_student_csv', methods=['POST'])
def insert_student_csv():
    fail_data_string = ""
    if session['username'] == "admin":
        student_csv_data = request.values.get('student_csv')
        student_csv = list(csv.reader(student_csv_data.splitlines()))
        head, rows = student_csv[0], student_csv[1:]
        data = []
        for row in rows:
            row_data = {}
            for idx in range(len(head)):
                row_data[head[idx]] = row[idx]
            row_data['device_uid'] = ""
            data.append(row_data)
        
        res = pdi.insert_many_data("students", data)
        status = res['status']
        
        fail_data_string = ""
        for item in res['fail_data']:
            fail_data_string = "{}{}\n".format(fail_data_string, str(item))
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message, 
            'fail_data': fail_data_string}


@app.route("/insert_course", methods=['POST'])
def insert_course():
    if session['username'] == "admin":
        course_code = request.values.get('course_code')
        course_name = request.values.get('course_name')
        faculty_codes = request.values.get('faculty_codes').split(',')
        class_codes = request.values.get('class_codes').split(',')
        course_info = "{}|{}|{}|{}".format(course_code, course_name,
                                           ", ".join(faculty_codes),
                                           ", ".join(class_codes))
        data = {'course_code': course_code, 'course_name': course_name,
                'faculty_code': faculty_codes, 'class_code': class_codes,
                'course_status': "Active", 'course_info': course_info}
        
        res = pdi.insert_data("courses", data)
        status = res['status']
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message}


@app.route('/insert_course_csv', methods=['POST'])
def insert_course_csv():
    fail_data_string = ""
    if session['username'] == "admin":
        course_csv_data = request.values.get('course_csv')
        course_csv = list(csv.reader(course_csv_data.splitlines()))
        head, rows = course_csv[0], course_csv[1:]
        data = []
        for row in rows:
            row_data = {}
            for idx in range(len(head)):
                if head[idx] == "faculty_code" or head[idx] == "class_code":
                    row_data[head[idx]] = row[idx].split('|')
                else:
                    row_data[head[idx]] = row[idx]
            row_data['course_status'] = "Active"
            row_data['course_info'] = "{}|{}|{}|{}".format(
                row_data['course_code'],
                row_data['course_name'],
                ", ".join(row_data['faculty_code']),
                ", ".join(row_data['class_code']))
            data.append(row_data)
        
        res = pdi.insert_many_data("courses", data)
        status = res['status']
        
        fail_data_string = ""
        for item in res['fail_data']:
            fail_data_string = "{}{}\n".format(fail_data_string, str(item))
    else:
        status = "E8"
        
    message = status_code[status]
    return {'status': status, 'message': message, 
            'fail_data': fail_data_string}


"""
|-----------------------------------------------------------------------------
| API
|-----------------------------------------------------------------------------
|
| This section contains APIs for assisting external system communication.
|
"""

# TODO: Use make_response for all the API calls


@app.route("/dept_list", methods=['POST', 'GET'])
def dept_list_api():
    """API for fetching department list."""
    return get_dept_list()


@app.route("/server_status", methods=['POST', 'GET'])
def server_status_api():
    """API for checking server status."""
    if is_org_registered():
        return "Active"
    else:
        return "Server not configured"


@app.route("/org_name", methods=['POST', 'GET'])
def org_name_api():
    """API for fetching registered organization name"""
    return get_org_name()


@app.route("/attendance_control", methods=['POST', 'GET'])
def attendance_control_api():
    """API for getting attendance control info for given session."""
    session_code = request.values.get("session_code")
    student_roll = get_attendance_control_info(session_code)
    if student_roll:
        return student_roll
    else:
        return "None"


@app.route("/register_device", methods=['POST'])
def register_device_api():
    """API for registering device against a student's roll number."""
    if request.is_json:
        device_uid = request.json['device_uid']
        student_roll = request.json['student_roll']
    else:
        device_uid = request.values.get("device_uid")
        student_roll = request.values.get("student_roll")
    register_res = register_device(device_uid, student_roll)
    
    return register_res


@app.route("/device_info", methods=['POST', 'GET'])
def device_info():
    """API for getting user info against registered device."""
    if request.is_json:
        device_uid = request.json['device_uid']
    else:
        device_uid = request.values.get("device_uid")
    student_res = get_student_info(device_uid=device_uid)
    
    return student_res
    

"""
|-----------------------------------------------------------------------------
| Utility Functions
|-----------------------------------------------------------------------------
|
| This section contains utility and helper functions.
|
"""


def start_session(course_info, op_faculty_code):
    """Starts a session pertaining to the given course_info and op_faculty_code
    and returns the resultant session_id and timestamp."""
    timestamp = datetime.now().timestamp()
    session_code = "{}|{}".format(course_info, timestamp)
    data = {'session_code': session_code, 'course_info': course_info,
            'timestamp': timestamp, 'op_faculty_code': op_faculty_code,
            'session_status': "Active", 'control_share': ""}
    res = pdi.insert_data("sessions", data)
    session_id = ""
    if res['status'] == "S0":
        session_id = pdi.get_id("sessions", 'session_code', session_code)
        
    if session_id:
        query = {'session_code': session_code}
        mod_query = {'session_code': str(session_id)}
        id_res = pdi.update_data("sessions", query, mod_query)
        status = id_res['status']
    else:
        status = res['status'] if res['status'] != "S0" else "E9"
        
    return {'status': status, 'message': status_code[status], 
            'session_id': session_id, 'timestamp': timestamp}


def end_session(session_code):
    """Deactivates attendance entry allowance of the specified session_code."""
    query = {'session_code': session_code}
    mod_query = {'session_status': "Inactive", 'control_share': ""}
    res = pdi.update_data("sessions", query, mod_query)
    
    return {'status': res['status'], 'message': res['message']}


def give_attendance(mode, session_code, params):
    """Gives attendance to student for the given session_code based on two 
    modes - 1. Attendance given by professor, in which case the params required
    is student_roll and class_codes of the session; 2. Attendance through QR 
    Code scanning, in which case the params required is device_uid.
    """
    student_roll = ""
    class_code = ""
    
    if mode == "faculty":
        student_roll = params['student_roll']
        student_res = get_student_info(student_roll=student_roll)
        class_code = student_res['class_code']
    elif mode == "qrscan":
        device_uid = params['device_uid']
        student_res = get_student_info(device_uid=device_uid)
        student_roll = student_res['student_roll']
        class_code = student_res['class_code']
    
    if student_roll and class_code:
        session_res = get_session_info(session_code)
        course_info = session_res['course_info']
        class_codes = course_info.split("|")[3]
        if class_code in class_codes:
            if not has_attended(student_roll, session_code):
                status = "S0"
            else:
                status = "S4"
        else:
            status = "E10"
    else:
        status = "E0"
    
    if status == "S0":
        log_code = "{}_{}".format(session_code, student_roll)
        timestamp = datetime.now().timestamp()
        data = {'log_code': log_code, 'mode': mode, 
                'session_code': session_code, 'student_roll': student_roll, 
                'timestamp': timestamp}
        res = pdi.insert_data("attendance_logs", data)
        status = res['status']
    
    return {'status': status, 'message': status_code[status]}
        
def get_dept_list():
    """Returns department list from the database."""
    data = []
    dept_code = []
    dept_name = []
    
    res = pdi.fetch_data('departments')
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            dept_code.append(item['dept_code'])
            dept_name.append(item['dept_name'])
        
    return {'status': res['status'], 'message': res['message'], 
            'dept_code': dept_code, 'dept_name': dept_name}


def get_faculty_list():
    """Returns faculty list from the database."""
    data = []
    faculty_name = []
    faculty_code = []
    faculty_dept = []
    
    res = pdi.fetch_data('faculties')
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            faculty_name.append(item['faculty_name'])
            faculty_code.append(item['faculty_code'])
            faculty_dept.append(item['dept_name'])
    
    return {'status': res['status'], 'message': res['message'],
            'faculty_name': faculty_name, 'faculty_code': faculty_code,
            'faculty_dept': faculty_dept}


def get_class_list():
    """Returns class group list from the database."""
    data = []
    class_code = []
    dept_name = []
    class_start = []
    class_end = []
    class_section = []
    
    res = pdi.fetch_data('classes')
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            class_code.append(item['class_code'])
            dept_name.append(item['dept_name'])
            class_start.append(item['class_start'])
            class_end.append(item['class_end'])
            class_section.append(item['class_section'])
    
    return {'status': res['status'], 'message': res['message'],
            'class_code': class_code, 'dept_name': dept_name,
            'class_start': class_start, 'class_end': class_end, 
            'class_section': class_section}


def get_student_list(class_code=""):
    """Returns list of students enrolled in the given class_code if class_code
    present, otherwise returns list of all the students enrolled.
    """
    data = []
    student_roll = []
    student_name = []
    class_codes = []
    device_uid = []
    
    query = {'class_code' : class_code} if class_code else {}
    res = pdi.fetch_data("students", query)
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            student_roll.append(item['student_roll'])
            student_name.append(item['student_name'])
            class_codes.append(item['class_code'])
            device_uid.append(item['device_uid'])
    
    return {'status': res['status'], 'message': res['message'],
            'student_roll': student_roll, 'student_name': student_name,
            'class_code': class_codes, 'device_uid': device_uid}


def get_student_info(student_roll="", device_uid=""):
    """Returns student details using student_roll as input."""
    student_name = ""
    class_code = ""
    
    res = {}
    res['status'] = "E0"
    res['message'] = status_code["E0"]
    
    query = {}
    if student_roll:
        query['student_roll'] = student_roll
    if device_uid:
        query['device_uid'] = device_uid
    
    if query:
        res = pdi.fetch_data("students", query)
        if res['status'] == "S0":
            student_res = res['data'][0]
            student_name = student_res['student_name']
            class_code = student_res['class_code']
            device_uid = student_res['device_uid']
    
    return {'status': res['status'], 'message': res['message'],
        'student_roll': student_roll, 'student_name': student_name,
        'class_code': class_code, 'device_uid': device_uid}


def get_course_list(op_faculty_code=""):
    """Returns list of all the courses registered to the specified 
    op_faculty_code (or all) from the database.
    """
    course_code = []
    course_name = []
    faculty_code = []
    class_code = []
    course_status = []
    course_info = []
        
    res = pdi.fetch_data("courses")
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            course_code.append(item['course_code'])
            course_name.append(item['course_name'])
            faculty_code.append(", ".join(item['faculty_code']))
            class_code.append(", ".join(item['class_code']))
            course_status.append(item['course_status'])
            course_info.append(item['course_info'])
    
    if op_faculty_code:
        pop_idx = []
        for idx, fc in enumerate(faculty_code):
            if op_faculty_code not in fc:
                pop_idx.append(idx)
        pop_idx.reverse()
        for idx in pop_idx:
            course_code.pop(idx)
            course_name.pop(idx)
            faculty_code.pop(idx)
            class_code.pop(idx)
            course_status.pop(idx)
            course_info.pop(idx)
    
    return {'status': res['status'], 'message': res['message'],
            'course_code': course_code, 'course_name': course_name,
            'faculty_code': faculty_code, 'class_code': class_code,
            'course_status': course_status, 'course_info': course_info}


def get_session_list(course_info="", op_faculty_code="", session_status=""):
    """Returns list of sessions taken for the given course_code and 
    op_faculty_code.
    """
    session_code = []
    timestamp = []
    session_status_res = []
    course_info_res = []
    
    query = {}
    if course_info:
        query['course_info'] = course_info
    if op_faculty_code:
        query['op_faculty_code'] = op_faculty_code
    if session_status:
        query['session_status'] = session_status
        
    res = pdi.fetch_data("sessions", query)
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            session_code.append(item['session_code'])
            timestamp.append(item['timestamp'])
            session_status_res.append(item['session_status'])
            course_info_res.append(item['course_info'])
    
    return {'status': res['status'], 'message': res['message'],
            'session_code': session_code, 'timestamp': timestamp, 
            'session_status': session_status_res, 
            'course_info': course_info_res}


def get_session_info(session_code):
    """Returns session info for the given session_code."""
    course_info = ""
    op_faculty_code = ""
    timestamp = ""
    session_status = ""
    
    query = {'session_code': session_code}
    res = pdi.fetch_data("sessions", query)
    if res['status'] == "S0":
        data = res['data'][0]
        course_info = data['course_info']
        op_faculty_code = data['op_faculty_code']
        timestamp = data['timestamp']
        session_status = data['session_status']
        
    return {'status': res['status'], 'message': res['message'],
            'session_code': session_code, 'timestamp': timestamp, 
            'session_status': session_status, 
            'course_info': course_info, 'op_faculty_code': op_faculty_code}


def has_attended(student_roll, session_code):
    """Returns True if student has attended session, else returns False."""
    query = {'student_roll': student_roll, 'session_code': session_code}
    res = pdi.fetch_data("attendance_logs", query)
    if res['status'] == "S0":
        if len(res['data']) == 1:
            return True
    return False


def get_attendance_control_info(session_code):
    """Returns the student_roll of the student with whom the attendance control
    is shared, else returns None."""
    if not session_code:
        return None
    query = {'session_code': session_code}
    res = pdi.fetch_data("sessions", query)
    if res['status'] == "S0":
        student_roll = res['data'][0]['control_share']
        student_res = get_student_info(student_roll=student_roll)
        if student_res['status'] == "S0":
            student_name = student_res['student_name']
            return "{} | {}".format(student_name, student_roll)
    return None


def get_attending_students(session_code):
    """Returns the list of students attending the given session_code."""
    student_name = []
    student_roll = []
    query = {'session_code': session_code}
    res = pdi.fetch_data("attendance_logs", query)
    if res['status'] == "S0":
        data = res['data']
        for item in data:
            student_roll.append(item['student_roll'])
            
    for roll in student_roll:
        res = get_student_info(roll)
        if res['status'] == "S0":
            student_name.append(res['student_name'])
        else:
            student_roll = []
            student_name = []
            break
        
    return {'status': res['status'], 'message': res['message'], 
            'student_roll': student_roll, 'student_name': student_name}

def get_org_name():
    """Returns organization name registered in the server."""
    query = {'acc_type': "admin"}
    res = pdi.fetch_data("details", query)
    if res['status'] == "S0":
        return res['data'][0]['org_name']
    else:
        return "None"
    
    
def get_admin_pwd():
    """Returns administrator's hashed and salted password."""
    query = {'acc_type': "admin"}
    res = pdi.fetch_data("details", query)
    if res['status'] == "S0":
        return res['data'][0]['acc_pwd']
    else:
        return None


def get_faculty_pwd(user):
    """Returns given user's hashed and salted password."""
    query = {'faculty_code': user}
    res = pdi.fetch_data("faculties", query)
    if res['status'] == "S0":
        return res['data'][0]['faculty_pwd']
    else:
        return None


def register_device(device_uid, student_roll):
    """Registers the given device_uid against the given student_roll if the
    student_roll isn't already linked to another device."""
    status = "E9"
    student_name = ""
    class_code = ""
    student_res = get_student_info(device_uid=device_uid)
    if student_res['status'] == "S0":
        status = "S5"
    else:
        res = get_student_info(student_roll=student_roll)
        if res['status'] == "S0":
            if res['device_uid']:
                status = "E11"
            else:
                student_name = res['student_name']
                class_code = res['class_code']
                query = {'student_roll': student_roll}
                mod_query = {'device_uid': device_uid}
                update_res = pdi.update_data("students", query, mod_query)
                status = update_res['status']
        else:
            status = res['status']
    
    return {'status': status, 'message': status_code[status], 
            'student_name': student_name, 'student_roll': student_roll, 
            'class_code': class_code, 'device_uid': device_uid}
            
    
    
def is_org_registered():
    """Returns true if organization is registered, false otherwise."""
    if get_org_name():
        return True
    else:
        return False


# Host Configuration and Server Execution
if __name__ == "__main__":
    app.env = "development"
    app.run(host="192.168.0.100", port="5000", debug=True, use_reloader=False)
    # app.run(host="192.168.192.34", port="5000", debug=True, use_reloader=False)
