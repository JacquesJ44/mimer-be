from flask import Flask
from flask import jsonify, request, make_response, session, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_session import Session
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import sqlite3

from db import DbUtil

# UPLOAD_FOLDER = '/Users/jacquesdutoit/Documents/vsc/mimer-be'
UPLOAD_FOLDER = './docs'
# C:\Users\Jacques\OneDrive - Aesir Systems (Pty) Ltd\Documents\vsc\mimer-be\docs
ALLOWED_EXTENSIONS = set(['pdf', 'png'])

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_SAMESITE"] = 'None'
# app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = DbUtil()
Session(app)

con = sqlite3.connect('mimir.db', check_same_thread=False)
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        surname TEXT,
        email TEXT,
        password TEXT
    )
 """)
cur.execute("""   
    CREATE TABLE IF NOT EXISTS sites (
        site TEXT PRIMARY KEY,
        latitude TEXT,
        longitude TEXT,
        building TEXT,
        street TEXT,
        number TEXT,
        suburb TEXT,
        city TEXT,
        postcode TEXT,
        province TEXT
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS circuits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT,
        circuitType TEXT,
        speed TEXT,
        circuitNumber TEXT,
        enni TEXT,
        vlan TEXT,
        startDate TEXT,
        contractTerm TEXT,
        endDate TEXT,
        siteA TEXT,
        siteB TEXT,
        comments TEXT,
        status TEXT,
        doc TEXT
    )
""")
con.close()

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

    # ROUTES
    
@app.route('/', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def login():
    obj = request.get_json()
    row = db.get_user_by_email(obj['email'])
    
    if request.method == 'GET':
        print(app.config['SECRET_KEY'])
    # if request.method == 'GET':
    #     if session:
    #         print(session)
    #     else:
    #         return jsonify({"msg": "You are not authorized"}), 401
        
    if request.method == 'POST':
        if row:
            # print(row)
            if obj['password'] == row[4]:
                session['email'] = row[3]
                session['fullname'] = row[1] + ' ' + row[2]
                # print(session)
                
                res = make_response({'id': row[0], 'email': row[3]})
                res.status_code = 200
                res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
                return res
            else:
                return jsonify({"msg": "Username or password is incorrect"}), 401
        else:
            return jsonify({"msg" : "User not found"}), 401
        
@app.route('/logout', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def logout():
    if session:
        if 'email' in session:
            del session['fullname']
            del session['email']
            # print(session)
        res = make_response({"msg": "You have been logged out"})
        res.status_code = 200
        res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
        return res
    elif not session:
        return jsonify({"msg": "You weren't logged in"})


@app.route('/register', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def register():
    obj = request.get_json()
    # print(obj)
    row = db.get_user_by_email(obj['email'])
    
    if request.method == 'POST':
        if not row:
            name = obj['name']
            surname = obj['surname']
            email = obj['email']
            password = obj['password']
            confirmpassword = obj['confirmpassword']
            if confirmpassword != password:
                return jsonify({"error": "Passwords do not match"})
            else:
                db.save_user(name, surname, email, password)
                return jsonify({"msg" : "Welcome to the knowledge of the gods"})
        else:
            return jsonify({"msg": "User already exists"})
        
@app.route('/navbar', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def navbar():
    if request.method == 'GET':
        if session:
            row = db.get_user_by_email(session['email'])
            # print(row) 
            res = make_response({'id': row[0], 'email': row[3]})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res
        elif not session:
            res = make_response({"error": 'You are not authorized'})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res
   
@app.route('/circuits', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def circuits():
    if request.method == 'GET':
        if session:
            row = db.get_user_by_email(session['email'])
            # print(row) 
            res = make_response({'id': row[0], 'email': row[3]})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res
        elif not session:
            res = make_response({"error": 'You are not authorized'})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res

    if request.method == 'POST':
        obj = request.get_json()
        # print('This is the object')
        # print(obj)
        y = []
        for key, value in obj.items():
            if value == "":
                pass
            else:
                value = "'%" + value + "%'"
                # print(key)
                # print(value)
                y = db.search_similar_circuit(key, value)
        if y:
            # print(y)
            return y
            
        return jsonify({"error": "No entries found"}), 404

@app.route('/sites', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def sites():
    if request.method == 'GET':
        if session:
            row = db.get_user_by_email(session['email'])
            # print(row) 
            res = make_response({'id': row[0], 'email': row[3]})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res
        elif not session:
            res = make_response({"error": 'You are not authorized'})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            # print(res.response)
            return res

    if request.method == 'POST':
        obj = request.get_json()
        # print('This is the object')
        # print(obj)
        y = []
        for key, value in obj.items():
            if value == "":
                pass
            else:
                value = "'%" + value + "%'"
                # print(key)
                # print(value)
                y = db.search_similar_site(key, value)
        if y:
            # print(y)
            return y
            
        return jsonify({"error": "No entries found"}), 404
        

@app.route('/addcircuit', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def addcircuit():
    if request.method == 'POST':
        obj = request.get_json()
        status = 'Active'
        if obj['doc']:
            doc = obj['doc']
            filename = doc.split('\\')
            filename = filename[2]
            # print('Original filename: ' + filename)
            # input()
            # filename = filename.replace(' ', '_')
            obj['doc'] = secure_filename(filename)
            # print('Replaced with: ' + filename)
            # input()
        else:
            filename = 'None'
        # print(obj)
        try:
            db.save_circuit(
                obj['vendor'],
                obj['circuitType'], 
                obj['speed'], 
                obj['circuitNumber'], 
                obj['enni'], 
                obj['vlan'], 
                obj['startDate'], 
                obj['contractTerm'], 
                obj['endDate'], 
                obj['siteA'],
                obj['siteB'],
                obj['comments'],
                status,
                filename
            )
            res = make_response({"msg": "Circuit successfully added"})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res
        except:   
            res = make_response({"error": "Unable to save circuit"})
            res.status_code = 403
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res

@app.route('/upload', methods=['POST'])
@cross_origin(methods=['POST'], supports_credentials=True, origins='http://localhost:3000')
def upload():
    # target = os.path.join(UPLOAD_FOLDER, 'docs')
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    file = request.files['formFile']
    filename = secure_filename(file.filename)
    destination = '/'.join([UPLOAD_FOLDER, filename])
    # print(filename)
    if filename not in os.listdir(UPLOAD_FOLDER):
        file.save(destination)
    else:
        res = make_response({"error": "File already exists"})
        res.status_code = 403
        return res
    res = make_response({"msg": "Document uploaded successfully!"})
    res.status_code = 200
    # res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
    return res

@app.route('/addsite', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def addsite():
    if request.method == 'POST':
        obj = request.get_json()
        # print(obj)
        exists = db.search_site(obj['site'])
        if not exists:
            db.save_site(
                obj['site'],
                obj['latitude'], 
                obj['longitude'], 
                obj['building'], 
                obj['street'], 
                obj['number'], 
                obj['suburb'], 
                obj['city'], 
                obj['post'], 
                obj['province']
            )
            res = make_response({"msg": "Site successfully added"})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res
        else:
            res = make_response({"error": "Site already exists"})
            res.status_code = 406
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res
        
@app.route('/viewcircuit/<int:id>', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def view_circuit(id):
    row = db.search_circuit_to_view(id)
    # print('row found')
    # print(row)
    return row[0]

@app.route('/viewsite/<site>', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def view_site(site):
    if request.method == 'GET':
        row = db.search_site_to_view(site)
        # print(row)
        return row[0]

    if request.method == 'POST':
        row = db.search_site_to_view(site)
        # print('row found')
        # print(row)
        db.delete_site(site)
        return jsonify({"msg": "Deleted!"})

@app.route('/updatecircuit/<int:id>', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def update_circuit(id):
    row = db.search_circuit_to_view(id)
    if request.method == 'GET':
        # print('This is the row')
        # print(row)
        return row[0]

    if request.method == 'POST':
        obj = request.get_json()
        # print('OBJ: ')
        # print(obj)
        if 'doc' in obj:    
            doc = obj['doc']
            # print(doc)
            # input()
            filename = doc.split('\\')
            filename = filename[2]
            # filename = filename.replace(' ', '_')
            obj['doc'] = secure_filename(filename)
            # print(obj['doc'])
        else:
            pass
        for key, value in obj.items():
            if key == 'id':
                pass
            else:
                db.update_circuit(key, value, obj['id'])
        return jsonify({"msg": 'Updated'})
    
@app.route('/download/<int:id>', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def download(id):
    row = db.search_circuit_to_view(id)
    # print(row)
    file = row[0]['doc']
    # print('FILE: ')
    # print(file)
    # print('UPLOAD FOLDER: ')
    # print(UPLOAD_FOLDER)
    target = '/'.join([UPLOAD_FOLDER, file])
    # print(target)
    if file in os.listdir(UPLOAD_FOLDER):
        return send_file(target, as_attachment=True, mimetype='application/pdf')
        
    else:
        return jsonify({"error": "File not Found"})
    
@app.route('/getsite', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def get_site():
    obj = request.get_json()
    if obj != "":
        obj = "'%" + obj + "%'"
        # print(obj)
        y = db.search_sitename(obj)
        # print(y)
    else:
        return jsonify({"msg": "No site found"})
    return y

# @app.route('/test', methods=['GET'])
# @cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
# def test():
#     return jsonify({"msg": "It works"})

if __name__ == '__main__':
    CORS(app, supports_credentials=True, resource={r"/*": {"origins": "*"}})
    app.run()