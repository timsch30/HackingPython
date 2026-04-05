from ticket import app
from flask import render_template


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/tickets')
def tickets_pages():

    items = [{"id": 1, "prio": 2, "user": "Mark", "title":"backend broken"},
             {"id": 2, "prio": 1, "user": "Luke", "title":"GUI not working"},
             {"id": 3, "prio": 2, "user": "Han", "title":"Nothing works"}]

    return render_template('tickets.html', items=items)


