from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def home_page():
    return "hello_page"

@app.route('/home')
def hello_world():
    return ("<h1>Hello World</h1><p>this is my text</p>")

@app.route('/welcome')
def welcome():
    vars = {}
    vars["user"] = "kylo"
    vars["message"] = "you are on the dark side"

    return render_template('welcome.html', vars = vars)

@app.route('/quest')
def quest():

    name = request.args.get("name", "kylo")

    return render_template('quest.html', var=name)

if __name__ == "__main__":
    app.run(debug=True)
    #    app.run(debug=True, host="0.0.0.0", port=5000)
