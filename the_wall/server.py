from flask import Flask, render_template, request, redirect, flash, session
import re
from mysqlconnection import MySQLConnector
import os, binascii 
import md5


app = Flask(__name__)
app.secret_key = 'ThisIsSecret'

mysql = MySQLConnector(app, 'Wall')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('user_id') is None:
        return redirect('/login')
    else:
        query = 'select * from users where id = :id'
        query_data = {
            'id': session['user_id']
        }
        user = mysql.query_db(query, query_data)
        user = user[0]

        query_messages = 'SELECT messages.message as message, CONCAT_WS(" ", users.first_name, users.last_name) as name, DATE_FORMAT(messages.created_at,"%M %D %Y ") as time, users.id as user_id, messages.id as message_id from messages join users on users.id = messages.user_id order by time DESC'
        messages = mysql.query_db(query_messages)
        query_comments = 'select comments.comment, CONCAT_WS(" ", users.first_name, users.last_name) as name, comments.created_at as time, comments.message_id from comments join users on comments.user_id = users.id order by time'
        comments = mysql.query_db(query_comments)
    return render_template('index.html', user=user, messages=messages, comments=comments)

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('user_id'):
        return redirect('/')
    if request.method == 'POST':

        if request.form['action'] == 'register':
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
                return redirect('/')

            else:
                return redirect('/login')

        elif request.form['action'] == 'login':
            email = request.form['email']
            password = request.form['password']
            query = 'SELECT * FROM users where email=:email'
            query_data = {
                'email': email
            }
            result = mysql.query_db(query, query_data)
            if len(result) < 1:
                flash('That email does not exist')
                return redirect('/login')
            if md5.new(password + result[0]['salt']).hexdigest() == result[0]['password']:
                session['user_id'] = result[0]['id']
                return redirect('/')
            else:
                flash('Incorrect password.')
                return redirect('/login')
            
    else:
        return render_template('login.html')

@app.route('/add/<user_id>', methods=['POST'])
def create(user_id):
    if len(request.form['message']) > 255:
        flash('Your message cannot be longer than 255 characters')
        return redirect('/')
    query = 'INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(),:user_id)'
    query_data = {
        'message': request.form['message'],
        'user_id': user_id
    }
    mysql.query_db(query, query_data)
    return redirect('/')

@app.route('/add/<user_id>/<message_id>', methods=['POST'])
def create_comment(user_id,message_id):
    if len(request.form['message']) > 255:
        flash('Your comment cannot be longer than 255 characters.')
        return redirect('/')
    if len(request.form['message']) < 1:
        flash('Your comment cannot be blank.')
        return redirect('/')
    query = 'INSERT INTO comments (comment, created_at, updated_at, user_id, message_id) VALUES (:message, NOW(), NOW(),:user_id,:message_id)'
    query_data = {
        'message': request.form['message'],
        'user_id': user_id,
        'message_id': message_id
    }
    mysql.query_db(query, query_data)
    return redirect('/')

@app.route('/logoff')
def logoff():
    session.pop('user_id')
    return redirect('/login')
    
    



app.run(debug=True)