import flask
from flask import Flask, render_template, request,redirect,session
import userconfig
import stock_utils
import gpt_utils

# source ~/anaconda3/bin/activate
app = Flask("myGPT")
app.secret_key = "Alexyyds245633"

@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    return render_template("chatGPT-clone.html")

@app.route("/chatGPT-clone",methods=["POST","GET"])
def chatGPT_clone():
    if "username" not in session:
        return redirect("/login")
    question = request.args.get("question", "")
    question = str(question).strip()
    username = session["username"]
    if question:
        return flask.Response(
            gpt_utils.gpt_stream(username, question),
            mimetype="text/event-stream"
        )
    else:
        return "Please enter a question"


# 登录功能
@app.route("/login",methods=["POST","GET"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if userconfig.check_user(username,password):
            session["username"] = username
            return redirect("/")
        else:
            message = "用户名或者密码错误"
    return render_template("login.html",message=message)

# 登出功能
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# 显示配额信息
@app.route("/show_quotas",methods=["GET"])
def show_quotas():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    return userconfig.get_quotas(username)

# 股票分析界面
@app.route("/stock",methods=["POST","GET"])
def stock():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]

    # 历史一个月的股票数据通过表格展示
    data_type = request.args.get("data_type")
    stock_code = request.args.get("stock_code")
    df_stock_table = None
    if data_type == "stock_table":
        df_stock_table = stock_utils.get_data_before_k_days(code=stock_code,before_days=30)
        return df_stock_table.to_html(index=False,classes="table table-striped")

    # gpt分析股票结果输出
    if data_type == "gpt_stock_output":
        df_stock_data= stock_utils.get_data_before_k_days(code=stock_code, before_days=30)
        question = "分析如下股票的交易数据，给出收盘价，交易量的趋势分析，并且给出投资建议：%s" % df_stock_data.to_string()
        return flask.Response(
            gpt_utils.gpt_stream(username, question),
            mimetype="text/event-stream"
        )

    # 获取现金流数据表
    if data_type == "stock_cash_table":
        df_cash_table = stock_utils.get_cash_flow(code=stock_code)
        return df_cash_table.to_html(index=False,classes="table table-striped")
    # gpt分析现金流结果输出
    if data_type == "gpt_cash_output":
        df_cash_data = stock_utils.get_cash_flow(code=stock_code)
        question = "分析如下股票的现金流数据，进行数据分析，并且给出投资建议：%s" % df_cash_data.to_string()
        return flask.Response(
            gpt_utils.gpt_stream(username, question),
            mimetype="text/event-stream"
        )

    # 上证300股票列表获取
    df_stock_codes = stock_utils.get_hs300_stocks()
    stock_codes = []
    for idx, row in df_stock_codes.iterrows():
        stock_codes.append({"code":row["code"],"code_name":row["code_name"]})
    return render_template("stock.html",stock_codes=stock_codes)




app.run(host="0.0.0.0",port=7757,debug=True)