from ticket import app
from flask import render_template

@app.route('/')
def home_page():
    vars = ["Kylo", "Luke", "Han"]
    return render_template('actors.html', vars = vars)

@app.route('/welcome')
def welcome():

    vars = ["kylo","you are on the dark side"]

    return render_template('welcome.html', vars = vars)

