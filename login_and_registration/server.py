from flask import Flask, render_template, request, redirect, flash, session
import re
from mysqlconnection import MySQLConnector
import os, binascii 
import md5


app = Flask(__name__)
app.secret_key = 'ThisIsSecret'

mysql = MySQLConnector(app, 'mydb')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route('/')
def index():
    if session.get("user_id") is not None:
        return redirect('/success')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    query = 'SELECT * FROM users where email=:email'
    query_data = {
        'email': email
    }
    result = mysql.query_db(query, query_data)
    if len(result) < 1:
        flash('That email does not exist')
        return redirect('/')
    if md5.new(password + result[0]['salt']).hexdigest() == result[0]['password']:
        session['user_id'] = result[0]['id']
        return redirect('/success')
    else:
        flash('Incorrect password.')
        return redirect('/')

@app.route('/register', methods=["POST"])
def register():
    email = request.form['email'] 
    f_name = request.form['f_name']
    l_name = request.form['l_name']
    password1 = request.form['password']
    password2 = request.form['c_password']
    allgood = True
    if len(email)<1 or len(f_name)<1 or len(l_name)<1 or len(password1)<1 or len(password2)<1:
        flash("All fields are required and must not be blank")
        allgood = False
    if not f_name.isalpha() or not l_name.isalpha():
        flash("Names can only contain letters")
        allgood = False
    if len(f_name)<2 or len(l_name)<2:
        flash("Names must be longer than 2 characters")
        allgood = False
    if len(password1)<8 or len(password2)<8:
        flash("Passwords must be atleast 8 characters.")
        allgood = False
    if not EMAIL_REGEX.match(email):
        flash("Not a valid email address.")
        allgood = False
    if password1 != password2:
        flash("Your passwords do not match.")
        allgood = False

    if allgood == True:
        salt = binascii.b2a_hex(os.urandom(15))
        hashed_pw = hashed_pw = md5.new(password1 + salt).hexdigest()
        insert_query = 'INSERT INTO users (first_name,last_name,email,password,created_at,salt) VALUES (:first, :last, :email, :password, NOW(),:salt)'
        query_data = {
            'first': f_name,
            'last': l_name,
            'email': email,
            'password': hashed_pw,
            'salt': salt
        }
        mysql.query_db(insert_query, query_data)
        query = 'SELECT LAST_INSERT_ID()'
        last_id = mysql.query_db(query)
        print last_id
        session['user_id'] = last_id[0]['LAST_INSERT_ID()']
        return redirect('/success')
    else:
        return redirect('/')

@app.route('/success')
def success():
    if session.get("user_id") is not None:
        query = 'select * from users where id = :id'
        query_data = {
            'id': session['user_id']
        }
        user = mysql.query_db(query, query_data)
        return render_template('success.html', user=user)
    else:
        return redirect('/')

        
        

app.run(debug=True)