from flask import Flask, render_template, request, redirect
# import the Connector function
from mysqlconnection import MySQLConnector
app = Flask(__name__)
# connect and store the connection in "mysql"; note that you pass the database name to the function
mysql = MySQLConnector(app, 'mydb')
# an example of running a query
@app.route('/')
def index():
    query = "SELECT name, age, DATE_FORMAT(since, '%b %D %Y') as since FROM friends"
    friends = mysql.query_db(query)
    return render_template('index.html', friends=friends)

@app.route('/add', methods=['POST'])
def add():
    query = "INSERT INTO friends (name, age, since) VALUES (:name, :age, NOW())"
    data = {
             'name': request.form['name'],
             'age':  request.form['age'],
           }
    mysql.query_db(query, data)
    return redirect('/')





app.run(debug=True)