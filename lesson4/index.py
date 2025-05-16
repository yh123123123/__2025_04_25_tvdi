from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello, World!</h1><p>01頁</p>"

@app.route("/user")
def user():
    return "<h1>Hello, World!</h1><p>02頁</p>"

@app.route("/product")
def userproduct():
    return "<h1>Hello, World!</h1><p>03頁</p>"

