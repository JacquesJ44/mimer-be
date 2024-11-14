from flask import Flask
from flask import jsonify, request, make_response, session, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from flask_session import Session
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import pymysql

from db import DbUtil

UPLOAD_FOLDER = './docs'
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_SAMESITE"] = 'None'
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = DbUtil()
Session(app)

con = pymysql.connect(host='localhost', user='root', database='mimir')
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT(5) PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(20),
        surname VARCHAR(20),
        email VARCHAR(50) UNIQUE,
        password VARCHAR(20)
    )
 """)
cur.execute("""   
    CREATE TABLE IF NOT EXISTS sites (
        id INT(5) PRIMARY KEY AUTO_INCREMENT,
        site VARCHAR(50) UNIQUE,
        latitude VARCHAR(30),
        longitude VARCHAR(30),
        building VARCHAR(30),
        street VARCHAR(30),
        number VARCHAR(5),
        suburb VARCHAR(30),
        city VARCHAR(30),
        postcode VARCHAR(10),
        province VARCHAR(30)
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS circuits (
        id INT(5) PRIMARY KEY AUTO_INCREMENT,
        vendor VARCHAR(15),
        circuitType VARCHAR(15),
        speed VARCHAR(15),
        circuitNumber VARCHAR(50),
        enni VARCHAR(15),
        vlan VARCHAR(15),
        startDate VARCHAR(15),
        contractTerm VARCHAR(15),
        endDate VARCHAR(15),
        mrc VARCHAR(15),
        siteA VARCHAR(50),
        siteB VARCHAR(50),
        comments VARCHAR(1000),
        status VARCHAR(15),
        doc VARCHAR(100)
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
        
    if request.method == 'POST':
        if row:
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
            return res
        elif not session:
            res = make_response({"error": 'You are not authorized'})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res
   
@app.route('/circuits', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def circuits():
    if request.method == 'GET':
        if session:
            return jsonify({'id': db.get_user_by_email(session['email'])[0], 'email': session['email']})
        else:
            return jsonify({"error": 'You are not authorized'}), 401
        
    if request.method == 'POST':
        obj = request.get_json()

    if not any(obj.values()):
        return jsonify({"error": "Please enter at least one search parameter"}), 404
    
    query = 'SELECT * FROM circuits WHERE '
    for key, value in obj.items():
        if value:
            query += f'{key} LIKE %s AND '
    query = query.rstrip(' AND ')
    y = db.search_similar_circuit(query, tuple('%' + value + '%' for value in obj.values() if value))
    if y:
        return jsonify(y), 200
    return jsonify({"error": "No entries found"}), 404

@app.route('/sites', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def sites():
    if request.method == 'GET':
        if session:
            return jsonify({'id': db.get_user_by_email(session['email'])[0], 'email': session['email']})
        else:
            return jsonify({"error": 'You are not authorized'}), 401

    if request.method == 'POST':
        obj = request.get_json()

        if not any(obj.values()):
            return jsonify({"error": "Please enter at least one search parameter"}), 404
        
        query = 'SELECT * FROM sites WHERE '
        for key, value in obj.items():
            if value:
                query += f'{key} LIKE %s AND '
        query = query.rstrip(' AND ')
        y = db.search_similar_site(query, tuple('%' + value + '%' for value in obj.values() if value))
        if y:
            return jsonify(y), 200
        return jsonify({"error": "No entries found"}), 404
        

@app.route('/circuits/addcircuit', methods=['POST'])
@cross_origin(methods=['POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def addcircuit():
    if request.method == 'POST':
        obj = request.get_json()
        x = float(obj['mrc'])
        obj['mrc'] = "{:.2f}".format(x)
        status = 'Active'
        if obj['doc']:
            doc = obj['doc']
            filename = doc.split('\\')
            filename = filename[2]
            obj['doc'] = secure_filename(filename)
        else:
            filename = 'None'
            obj['doc'] = filename
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
                obj['mrc'], 
                obj['siteA'],
                obj['siteB'],
                obj['comments'],
                status,
                obj['doc']
                
            )
            res = make_response({"msg": "Circuit successfully added"})
            res.status_code = 200
            res.headers['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'] = True
            return res
        except Exception as e:   
            print(f"Error: {e}")
            res = make_response({"error": "Unable to save circuit"})
            res.status_code = 500  # Use 500 for server errors, not 403
            return res

@app.route('/upload', methods=['POST'])
@cross_origin(methods=['POST'], supports_credentials=True, origins='http://localhost:3000')
def upload():
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    file = request.files['formFile']
    filename = secure_filename(file.filename)
    destination = '/'.join([UPLOAD_FOLDER, filename])
    if filename not in os.listdir(UPLOAD_FOLDER):
        file.save(destination)
    else:
        res = make_response({"error": "File already exists"})
        res.status_code = 403
        return res
    res = make_response({"msg": "Document uploaded successfully!"})
    res.status_code = 200
    return res

@app.route('/sites/addsite', methods=['GET', 'POST'])
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
        
@app.route('/circuits/viewcircuit/<int:id>', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def view_circuit(id):
    row = db.search_circuit_to_view(id)
    # print('row found')
    # print(row)
    return row[0]

@app.route('/sites/viewsite/<site>', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def view_site(site):
    row = db.search_site_to_view(site)
    if request.method == 'GET':
        return row[0] if row else jsonify({"error": "No site found"}), 404

    if request.method == 'POST':
        if row:
            db.delete_site(site)
            return jsonify({"msg": "Deleted!"})
        return jsonify({"error": "No site found"}), 404

@app.route('/circuits/updatecircuit/<int:id>', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def update_circuit(id):
    row = db.search_circuit_to_view(id)[0]
    if request.method == 'GET':
        # print(row)
        return row

    if request.method == 'POST':
        obj = request.get_json()
        if 'doc' in obj:
            doc = obj['doc']
            filename = doc.split('\\')[2]
            obj['doc'] = secure_filename(filename)
        for key, value in obj.items():
            if key != 'id':
                db.update_circuit(key, value, id)
        return jsonify({"msg": 'Updated'})
    
@app.route('/download/<int:id>', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def download(id):
    row = db.search_circuit_to_view(id)
    # print(row)
    file = row[0]['doc']
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
    if obj:
        query = "SELECT * FROM sites WHERE site LIKE %s"
        values = (f"%{obj}%",)
        return db.search_sitename(query, values)
    return jsonify({"msg": "No site found"})

if __name__ == '__main__':
    CORS(app, supports_credentials=True, resource={r"/*": {"origins": "*"}})
    app.run()