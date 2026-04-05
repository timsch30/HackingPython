from ticket import app, db
from flask import render_template, request, url_for, redirect
from sqlalchemy import text

@app.route('/')
def home_page():
    cookie = request.cookies.get('name')
    print("<>home_page()")
    return render_template('home.html', cookie=cookie)



@app.route('/login', methods=['GET', 'POST'])
def login_pages():
    print("login was called")

    if request.method == 'POST':
        print("->login_pages()")
        username = request.form.get('Username')
        password = request.form.get('Password')
        print("Here the Data!!!")
        print(username)
        print(password)

        if (username is None or
                isinstance(username, str) is False or
                len(username) < 3):
            print("not valid")
            #flash(f"Username is not valid", category='warning')
            return render_template('login.html', cookie=None)

        if (password is None or
                isinstance(password, str) is False or
                len(password) < 3):
            print("something with password")
            #flash(f"Password is not valid", category='warning')
            return render_template('login.html', cookie=None)

        query_stmt = f"select username from bugusers where username = '{username}' and password = '{password}'"
        print(query_stmt)
        result = db.session.execute(text(query_stmt))

        user = result.fetchall()
        #print("debug1")
        if not user:
            #flash(f"Try again", category='warning')
            #print("debug2")
            return render_template('login.html', cookie=None)
        #print("debug3")
        #flash(f"'{user}', you are logged in ", category='success')
        print("debug1")

        resp = redirect('/tickets')
        print("debug2")
        resp.set_cookie('name', username)
        print("<-login(), go to tickets_pages")
        return resp
        #return render_template('tickets.html')

    return render_template('login.html', cookie=None)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        print("->register_page()")

        username = request.form.get('Username')
        email = request.form.get('Email')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')

        print(username)
        print(email)
        print(password1)
        print(password2)

        if(username is None or
                isinstance(username, str) is False or
                len(username) < 3):
            #flash("Username not valid", category='danger')
            print("<-register_page(), username invalid")
            return render_template('register.html', cookie=None)

        if(email is None or
                isinstance(email, str) is False or
                len(email) < 3):
            print("<-register_page(), email not valid")
            #flash("Email not valid", category='danger')
            return render_template('register.html', cookie=None)

        if(password1 is None or
                isinstance(password1, str) is False or
                len(password1) < 3 or
                password1 != password2):
            print("<-register_page(), password1 not valid")
            #flash("Password1 not valid", category='danger')
            return render_template('register.html', cookie=None)

        query_stmt = f"select * from bugusers where username = '{username}'"
        print(query_stmt)
        result = db.session.execute(text(query_stmt))
        item = result.fetchone()
        print(item)

        if item is not None:
            #flash("Username exists, try again")
            print("Username exists")
            return render_template('register.html', cookie=None)

        query_insert = f"insert into bugusers (username, email_address, password) values ('{username}', '{email}', '{password1}')"
        print(query_insert)
        db.session.execute(text(query_insert))
        db.session.commit()
        #flash("You are registered", category='success')
        resp = redirect('/tickets_pages')
        resp.set_cookie('name', username)
        print("<-register_page(), go to tickets_pages")
        return resp

    return render_template('register.html')

@app.route('/tickets')
def tickets_pages():

    cookie = request.cookies.get('name')
    print("->tickets_pages()", cookie)
    if not request.cookies.get('name'):
        print("<-tickets_pages(), no cookie")
        return redirect(url_for('login_pages'))

    query_stmt = f"select * from bugitems"
    result = db.session.execute(text(query_stmt))
    itemsquery = result.fetchall()

    print(itemsquery)
    print("<-tickets_pages()=", cookie)
    return render_template('tickets.html', items=itemsquery, cookie=cookie)


@app.route('/logout')
def logout():
    resp = redirect('/')
    resp.set_cookie('name', '', expires=0)
    return resp


@app.route('/ticket_entry', methods=['GET', 'POST'])
def ticket_entry():

    cookie = request.cookies.get('name')
    print("->ticket_entry()", cookie)
    if not cookie:
        print("no cookie")
        return redirect(url_for('login'))

    if request.method == 'POST':
        priority = request.form.get('Priority')
        username = request.form.get('Username')
        title = request.form.get('Title')
        description = request.form.get('Description')

        query_insert = f"insert into butitems (priority, username, title, description) values ({priority}, '{username}', '{title}', '{description}')"
        print(query_insert)
        db.session.execute(text(query_insert))
        db.session.commit()
        print("hey erfolgreich")
        resp = redirect('/tickets')
        resp.set_cookie('name', cookie)
        return resp

    return render_template('ticket_entry.html', cookie=cookie)

@app.route('/ticket_item/<int:item_id>', methods=['GET'])
def ticket_item(item_id):
    print("->ticket_item()")
    query_stmt = f"select * from bugitems where id={item_id}"

    result = db.session.execute(text(query_stmt))
    item = result.fetchone()
    print(query_stmt)
    if not item:
        print("item not existing")
        # error handling ....

    cookie = request.cookies.get('name')

    return render_template('ticket_item.html', items=item, cookie=cookie)


