from flask import Flask, render_template
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# 載入 .env 檔案
load_dotenv()
conn_string=os.getenv("RENDER_DATABASE")


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
    try:
        conn=psycopg2.connect(conn_string)
        #raise Exception("出現錯誤")
        with conn.cursor() as cur:
            sql="""SELECT * FROM public.最新訊息
                   ORDER BY 上版日期 DESC"""
            cur.execute(sql)
            # 取得所有資料
            rows=cur.fetchall()
        print("連線成功")
    except OperationalError as e:
        print("連線失敗")
        print(e)
        return render_template("error.html",error_message="資料庫錯誤"),500
    except:
        return render_template("error.html",error_message="不知名錯誤"),500
    conn.close()
    return render_template("new.html",rows=rows)

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

