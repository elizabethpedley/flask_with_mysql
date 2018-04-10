from flask import Flask, render_template, request, redirect, flash, session
import re
from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = 'ThisIsSecret'

mysql = MySQLConnector(app, 'mydb')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    email = request.form['email']
    if EMAIL_REGEX.match(email): 
        success = 'The email address you entered {} is a VALID email address! Thank you'.format(email)
        flash(success)
        query = "INSERT INTO emails (email, created_at) VALUES (:email, NOW())"
        data = {
             'email': email,
           }
        mysql.query_db(query, data)
    else:
        flash("Email not valid!")
    return redirect('/success')

@app.route('/success')
def success():
    query = "SELECT email, DATE_FORMAT(created_at, '%c/%d/%y %h:%i %p') as date FROM emails"
    emails = mysql.query_db(query)
    return render_template('success.html', emails=emails)

app.run(debug=True)