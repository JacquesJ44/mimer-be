from flask import Flask
from flask import jsonify, request, make_response, session
from flask_cors import CORS, cross_origin
import json
import sqlite3

from db import DbUtil

app = Flask(__name__)
app.config['SECRET_KEY'] = '1245oiajfdsgkjfadsfascjhkchjkgeffhklfhtrtbwefaehnmjjmwsdgnieabvrv4inuviun5niaiae'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_SAMESITE"] = 'None'
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = False

db = DbUtil()

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
            print(row)
            if obj['password'] == row[4]:
                session['email'] = row[3]
                session['fullname'] = row[1] + ' ' + row[2]
                print(session)
                
                res = make_response({'id': row[0], 'email': row[3], 'route': '/POST'})
                res.status_code = 200
                res.headers['Content-Type', 'Authorization', 'Acces-Control-Allow-Origin'] = True
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
            print(session)
        res = make_response({"msg": "You have been logged out"})
        res.status_code = 200
        res.headers['Content-Type', 'Authorization', 'Acces-Control-Allow-Origin'] = True
        return res
    elif not session:
        return jsonify({"msg": "You weren't logged in"})


@app.route('/register', methods=['POST'])
@cross_origin(methods=['POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def register():
    obj = request.get_json()
    print(obj)
    row = db.get_user_by_email(obj['email'])
    if not row:
        name = obj['name']
        surname = obj['surname']
        email = obj['email']
        password = obj['password']
        db.save_user(name, surname, email, password)
        return jsonify({"msg" : "Succesfully added to db"})
    else:
        return jsonify({"msg": "User already exists"})
   
@app.route('/circuits', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def circuits():
    if request.method == 'GET':
        if session:
            row = db.get_user_by_email(session['email'])
            print(row) 
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
        pass

@app.route('/sites', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def sites():
    if request.method == 'GET':
        if session:
            row = db.get_user_by_email(session['email'])
            print(row) 
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
        print('This is the object')
        print(obj)
        for key, value in obj.items():
            if value == "":
                pass
            else:
                value = "'%" + value + "%'"
                print(key)
                print(value)
                y = db.search_similar_site(key, value)
        print(y)
        return y

@app.route('/addsite', methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def addsite():
    if request.method == 'POST':
        obj = request.get_json()
        print(obj)
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
        
@app.route('/viewsite/<site>', methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def view_site(site):
    row = db.search_site_to_view(site)
    print(row)
    return row

if __name__ == '__main__':
    CORS(app, supports_credentials=True, resource={r"/*": {"origins": "*"}})
    app.run(debug=True)