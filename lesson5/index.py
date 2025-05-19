from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/classes")
def classes():
    return render_template("classes.html")

@app.route("/user")
def user():
    return "<h1>Hello, World!</h1><p>02頁</p>"

@app.route("/product")
def userproduct():
    return "<h1>Hello, World!</h1><p>03頁</p>"

