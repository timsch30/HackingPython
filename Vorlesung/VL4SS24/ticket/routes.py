from ticket import app, db
from flask import render_template, request
from sqlalchemy import text

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login_pages():
    print("login was called")

    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')
        print("Here the Data!!!")
        print(username)
        print(password)

    return render_template('login.html')

@app.route('/tickets')
def tickets_pages():

#    items = [{"id": 1, "prio": 2, "user": "Mark", "title":"backend broken"},
#             {"id": 2, "prio": 1, "user": "Luke", "title":"GUI not working"},
#             {"id": 3, "prio": 2, "user": "Han", "title":"Nothing works"}]

    query_stmt = f"select * from bugitems"
    result = db.session.execute(text(query_stmt))
    itemsquery = result.fetchall()

    print(itemsquery)

    return render_template('tickets.html', items=itemsquery)


