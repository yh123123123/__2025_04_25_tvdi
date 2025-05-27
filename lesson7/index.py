from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/classes")
def classes():
    name = "Robert"
    weekdays=["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    return render_template('classes.html', name=name,weekdays=weekdays)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/traffic")
def traffic():
    return render_template("traffic.html")

@app.route("/user")
def user():
    return "<h1>Hello, World!</h1><p>02頁</p>"

@app.route("/product")
def userproduct():
    return "<h1>Hello, World!</h1><p>03頁</p>"

