import json
from datetime import datetime
from tkinter import Label

import numpy
from dominate.tags import legend
from numpy import histogram, double
from pandas.io.json import json_normalize
from flask import Flask, render_template, url_for, jsonify, request, redirect, flash
from flaskext.mysql import MySQL
from flask_googlecharts import GoogleCharts, BarChart, MaterialLineChart, ColumnChart, GaugeChart, AnnotationChart, \
    BubbleChart, CandlestickChart, Histogram, ScatterChart
import plotly.graph_objs as go
import plotly
import plotly.express as px

global filledresult, charts, versionID, useriddd
import numpy as np

app = Flask(__name__)
charts = GoogleCharts(app)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'a19lightgame'
app.config['MYSQL_DATABASE_PASSWORD'] = '5pb2ycsdke'
app.config['MYSQL_DATABASE_DB'] = 'a19lightgame'
app.config['MYSQL_DATABASE_HOST'] = 'mysql.studev.groept.be'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
# query = f"SELECT text FROM question;"
# cursor.execute(query)
# inter1 = cursor.fetchall()
# inter2 = json.dumps(inter1)
# inter3 = json.loads(inter2)
# result = sum(inter3, [])
# print(result)
colours = ['Red', 'Blue', 'Black', 'Orange']


# numberscale = ['Strongly Disagree', 'Disagree', 'Slightly Disagree', 'Neutral', 'Slightly Agree', 'Agree',
#                'Strongly Agree']


def printquestion(idS):
    query = f"SELECT text FROM question where surveyID={idS} or surveyID is null;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    result = sum(inter3, [])
    return result


def printquestionnumbers(idS):
    query = f"SELECT idquestion FROM question where surveyID={idS} or surveyID is null;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    result = sum(inter3, [])
    return result


def getsurveyID():
    query = "SELECT max(idsurvey) FROM survey;"
    cursor.execute(query)
    (id,) = cursor.fetchone()
    global versionID
    versionID = id
    return id


def getuserID():
    query = "SELECT max(iduser) FROM user;"
    cursor.execute(query)
    (id,) = cursor.fetchone()
    global useriddd
    useriddd = id
    return id


def progressbar():
    userid = getuserID()
    queryy = f"SELECT * FROM question where surveyID={versionID} or surveyID is null ;"
    inter5 = cursor.execute(queryy)
    queryy = f"SELECT * FROM answer inner join question on question.idquestion=answer.questionID where (surveyID={versionID} or surveyID is null) and userID = {userid};"
    inter19 = cursor.execute(queryy)
    progress = int(round(((inter19) / inter5) * 100))
    return progress


def takeanswers():
    userid = getuserID()
    query = f"SELECT answer,questionID FROM answer inner join question on question.idquestion=answer.questionID where userID = {userid} and (surveyID={versionID} or surveyID is null)  ORDER BY questionID ASC"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    answer = [row[0] for row in inter3]
    answer = [int(x) for x in answer]
    answer = [x - 4 for x in answer]
    questionid = [row[1] for row in inter3]
    return answer, questionid


def takeallanswers():
    query = f"SELECT avg(answer),questionID FROM answer inner join question on question.idquestion=answer.questionID where (surveyID={versionID} or surveyID is null) group by questionID ORDER BY questionID ASC"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    avganswer = [row[0] for row in inter3]
    avganswer = [x - 4 for x in avganswer]
    questionid = [row[1] for row in inter3]
    return avganswer, questionid


def takeallanswersbyperson():
    query = f"SELECT avg(answer),age,gender FROM answer inner join a19lightgame.user on a19lightgame.user.iduser=answer.userID group by userID ORDER BY userID ASC"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    avganswer = [row[0] for row in inter3]
    avganswer = [x - 4 for x in avganswer]
    age = [row[1] for row in inter3]
    gender = [row[2] for row in inter3]
    for index, item in enumerate(gender):
        if item == 'M' or item == 'male':
            gender[index] = 1
        else:
            gender[index] = 0

    return avganswer, age, gender


def takeanswerswithquestionid(selectedid):
    query = f"SELECT answer,questionID FROM answer inner join question on question.idquestion=answer.questionID where (surveyID={versionID} or surveyID is null) and questionID={selectedid} ORDER BY questionID ASC"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    answer = [row[0] for row in inter3]
    answer = [int(x) - 4 for x in answer]
    questionid = [row[1] for row in inter3]

    return answer, questionid


def takequestions():
    query = f"SELECT text FROM question where (surveyID={versionID} or surveyID is null) ORDER BY categoryID ASC"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    return inter3


def takeperson():
    query = f"SELECT * FROM a19lightgame.user"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    inter4 = [str(x) for x in inter3]
    return inter4


def plotly1():
    yScale, xScale, gender = takeallanswersbyperson()
    pplinfo = takeperson()
    sizee = [float(x) for x in yScale]
    absyscale = [30 * abs(x) for x in sizee]
    gender = [int(x) for x in gender]
    trace = go.Scatter(
        mode='markers',
        x=yScale,
        y=xScale,
        hovertext=pplinfo,
        hoverinfo="text",
        marker_color=gender,
        marker=dict(size=absyscale, colorscale='Viridis'),
        showlegend=False)
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    data2 = []
    for x in range(31):
        yScale, xScale = takeanswerswithquestionid(x)
        tracetemp = go.Violin(y=yScale, box_visible=True, line_color='black', points="all",
                              meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                              x0='Total Bill', name='QUESTION' + str(x))
        data2.append(tracetemp)
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON, graphJSON2


def takeavganswerspsy():
    ans = ["" for x in range(5)]
    for i in range(1, 6):
        query = f"SELECT avg(answer) FROM answer inner join question on question.idquestion=answer.questionID where categoryID={i};"
        cursor.execute(query)
        inter1 = cursor.fetchall()
        inter2 = json.dumps(inter1)
        inter3 = json.loads(inter2)
        inter4 = sum(inter3, [])[0]
        print(inter4)
        ans[i - 1] = inter4 - 4
        # ans[i]=numberscale[inter4-1]
    answer = ans
    query = "SELECT Category FROM category;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    cat = json.loads(inter2)
    cat1 = ["" for x in range(5)]
    for p in range(0, 5):
        cat1[p] = cat[p]
    print(cat1)
    return answer, cat1


def takeavganswersfunc():
    ans = ["" for x in range(5)]
    for i in range(1, 6):
        query = f"SELECT avg(answer) FROM answer inner join question on question.idquestion=answer.questionID where categoryID={i + 5};"
        cursor.execute(query)
        inter1 = cursor.fetchall()
        inter2 = json.dumps(inter1)
        inter3 = json.loads(inter2)
        inter4 = sum(inter3, [])[0]
        print(inter4)
        ans[i - 1] = inter4 - 4
        # ans[i]=numberscale[inter4-1]
    answer = ans
    query = "SELECT Category FROM category;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    cat = json.loads(inter2)
    cat2 = ["" for x in range(5)]
    for p in range(5, 10):
        cat2[p - 5] = cat[p]
    print(cat2)
    return answer, cat2


def drawBarchart1():
    myfunc_chart = BarChart("myfunc_chart", options={"title": "Category Functional", "width": 1300, "height": 600})
    myfunc_chart.add_column("string", "category")
    myfunc_chart.add_column("number", "score")
    answer, cat = takeavganswersfunc()
    # i = 0
    # for n in answer:
    #     myfunc_chart.add_rows([[cat[i], n]])
    #     i = i + 1
    # charts.register(myfunc_chart)
    cat = [x[0] for x in cat]
    reverseanswer = [-x for x in answer]
    trace3 = go.Bar(
        x=answer,
        y=cat,
        name='Category Function',
        orientation='h',
        marker=dict(
            color=reverseanswer)
    )
    data3 = [trace3]
    graphJSON3 = json.dumps(data3, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON3


def drawBarchart2():
    mypsy_chart = BarChart("mypsy_chart", options={"title": "Category Psychological", "width": 1300, "height": 600})
    mypsy_chart.add_column("string", "category")
    mypsy_chart.add_column("number", "score")
    answer, cat = takeavganswerspsy()
    cat = [x[0] for x in cat]
    reverseanswer = [-x for x in answer]
    trace4 = go.Bar(
        x=answer,
        y=cat,
        name='Category Psychological',
        orientation='h',
        marker=dict(
            color=reverseanswer)
    )
    data4 = [trace4]
    graphJSON4 = json.dumps(data4, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON4
    # i = 0
    # for n in answer:
    #     mypsy_chart.add_rows([[cat[i], n]])
    #     i = i + 1
    # charts.register(mypsy_chart)


def drawBarchartadditional():
    query = f"SELECT avg(answer)-4 FROM answer inner join question on question.idquestion=answer.questionID where idquestion>=46 group by questionID order by questionID ASC;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    inter4 = sum(inter3, [])
    print(inter4)
    answer = [float(x) for x in inter4]
    query = "SELECT text FROM question where idquestion>=46;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    inter4 = sum(inter3, [])
    cat = [str(x) for x in inter4]
    print(cat)
    reverseanswer = [-x for x in answer]
    trace4 = go.Bar(
        x=answer,
        y=cat,
        name='Category Psychological',
        orientation='h',
        marker=dict(
            color=reverseanswer)
    )
    data4 = [trace4]
    graphjson = json.dumps(data4, cls=plotly.utils.PlotlyJSONEncoder)
    data2 = []
    data3 = []
    for x in range(0, len(answer) + 1):
        query = f"SELECT answer-4 FROM answer inner join question on question.idquestion=answer.questionID where text='{cat[x]}';"
        cursor.execute(query)
        inter1 = cursor.fetchall()
        inter2 = json.dumps(inter1)
        inter3 = json.loads(inter2)
        inter4 = sum(inter3, [])
        inter5 = [float(x) for x in inter4]
        absinter5 = [abs(float(x)) * 30 for x in inter4]
        tracetemp = go.Violin(y=inter5, box_visible=True, line_color='black', points="all",
                              meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                              x0='Total Bill', name=cat[x])
        data2.append(tracetemp)
        query2 = f"SELECT a19lightgame.user.* FROM answer inner join question on question.idquestion=answer.questionID inner join a19lightgame.user on user.iduser = answer.userID where text='{cat[x]}';"
        cursor.execute(query2)
        interr1 = cursor.fetchall()
        interr2 = json.dumps(interr1)
        interr3 = json.loads(interr2)
        personinfo5 = [str(x) for x in interr3]
        listforx  = numpy.arange(1, len(inter5), 1).tolist()
        if len(inter5) != 0:
            scattertrace = go.Scatter(
                mode='markers',
                x=listforx,
                y=inter5,
                hovertext=personinfo5,
                hoverinfo="text",
                marker=dict(size=absinter5, colorscale='Viridis'),
                showlegend=True,
                name = cat[x])
            data3.append(scattertrace)
    graphjson2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)
    graphjson3 = json.dumps(data3, cls=plotly.utils.PlotlyJSONEncoder)
    return graphjson, graphjson2, graphjson3


def drawBubblechart():
    bubble_chart = BubbleChart("bubble_chart",
                               options={"title": "Questions Scatter Bubbles", "width": 1500, "height": 700,
                                        "colorAxis": "{ 'colors':['yellow']}", "legend": "none"})
    bubble_chart.add_column("string", "title")
    bubble_chart.add_column("number", "categoryID")
    bubble_chart.add_column("number", "score")
    bubble_chart.add_column("string", "question")
    # bubble_chart.add_column("number", "size")
    answer, questionid = takeallanswers()
    i = 0
    intn = 1
    print(questionid)
    for n in questionid:
        title = n
        n = int(n)
        # ans = int(answer[i])
        ans = answer[i]
        bubble_chart.add_rows([[title, intn, ans, takequestions()[i]]])
        i = i + 1
        if n % 3 == 0:
            intn = intn + 1
    charts.register(bubble_chart)


def previousanswers():
    queryy = f"select answer, questionID from answer inner join question on question.idquestion=answer.questionID where userID = {useriddd} and (surveyID={versionID} or surveyID is null)"
    cursor.execute(queryy)
    inter6 = cursor.fetchall()
    inter7 = json.dumps(inter6)
    inter8 = json.loads(inter7)
    filled = [row[0] for row in inter8]
    questionid = [row[1] for row in inter8]
    print(filled)
    # filled = sum(inter9, [])
    # print(filled)
    return filled, questionid


@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST' and request.form['action'] == 'Create':
        question = request.form['question']
        # category = request.form['category']
        sqlnewquestion = f"INSERT INTO question(text,categoryID) VALUES ('{question}','11');"
        cursor.execute(sqlnewquestion)
        conn.commit()

    sqlqu = "SELECT idquestion,text FROM question where idquestion>30 and surveyID is null  order by idquestion desc;"
    cursor.execute(sqlqu)
    addquestions = cursor.fetchall()
    if request.method == 'POST' and request.form['action'] == 'Submit':
        survey = request.form['survey']
        sqlnewsurvey = f"INSERT INTO survey(name) VALUES ('{survey}');"
        cursor.execute(sqlnewsurvey)
        conn.commit()
        sqls = "SELECT max(idsurvey) FROM survey "
        cursor.execute(sqls)
        (result,) = cursor.fetchone()

        for q in addquestions:
            sqlid = f"UPDATE question SET surveyID='{result}' WHERE idquestion={q[0]} "
            cursor.execute(sqlid)
            conn.commit()

        return redirect(url_for('home'))

    return render_template("newQuestion.html", addquestions=addquestions)


@app.route('/answer/<int:idQ>', methods=['GET', 'POST'])
def edit(idQ):
    sqlqu = f"SELECT text FROM question where idquestion={idQ};"
    cursor.execute(sqlqu)
    (question,) = cursor.fetchone()

    if request.method == 'POST':
        updateQ = request.form['edit']
        sqlupdateQ = f"UPDATE question SET text='{updateQ}' WHERE idquestion={idQ} "
        cursor.execute(sqlupdateQ)
        conn.commit()
        return redirect(url_for('create'))
    return render_template('edit.html', question=question, idQ=idQ)


@app.route('/delete/<int:idQ>', methods=['GET', 'POST'])
def delete(idQ):
    sqlde = f"DELETE FROM question where idquestion={idQ};"
    cursor.execute(sqlde)
    conn.commit()
    sqlqu = "SELECT idquestion,text FROM question where idquestion>30 and surveyID is null  order by idquestion  desc;"
    cursor.execute(sqlqu)
    addquestions = cursor.fetchall()
    return render_template("newQuestion.html", addquestions=addquestions)


@app.route("/survey")
def survey():
    sqls = "SELECT * FROM  survey;"
    cursor.execute(sqls)
    cards = cursor.fetchall()
    return render_template("surveylist.html", cards=cards)


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route('/survey/delete/<int:idS>', methods=['GET', 'POST'])
def deleteSurvey(idS):
    sqlde = f"DELETE FROM survey where idsurvey={idS};"
    cursor.execute(sqlde)
    conn.commit()
    sqls = "SELECT * FROM  survey;"
    cursor.execute(sqls)
    cards = cursor.fetchall()
    return render_template("surveylist.html", cards=cards)


@app.route('/survey/question/<int:idS>', methods=['GET', 'POST'])
def surveyQuestions(idS):
    global versionID
    versionID = idS
    sqlde = f"SELECT text FROM question where surveyID is null or surveyID={idS} ;"
    cursor.execute(sqlde)
    questions = cursor.fetchall()
    return render_template("menulist.html", questions=questions)


@app.route("/list")
def list():
    return render_template("index.html")


@app.route("/welcome/<int:idS>", methods=['GET', 'POST'])
def home(idS):
    global versionID
    versionID = idS
    sqlnewquestion = f"INSERT INTO user(namee) VALUES ('name');"
    cursor.execute(sqlnewquestion)
    conn.commit()
    useriddd = getuserID()
    query = f"SELECT text FROM question where surveyID is null or surveyID={idS} ;"
    cursor.execute(query)
    inter1 = cursor.fetchall()
    inter2 = json.dumps(inter1)
    inter3 = json.loads(inter2)
    result = sum(inter3, [])
    # result1 = printquestion(idS)
    filledresult, qidd = previousanswers()
    progress = progressbar()
    return render_template("homapage.html", result=result, progress=progress, filledresult=filledresult, qidd=qidd)


@app.route('/newQuestion', methods=['GET'])
def newQuestion():
    return render_template('newQuestion.html')


@app.route("/test")
def hometest():
    graphJSON3 = drawBarchart1()
    graphJSON4 = drawBarchart2()
    drawBubblechart()
    graphJSON, graphJSON2 = plotly1()
    return render_template("visualization1.html", colours=colours, graphJSON=graphJSON, graphJSON2=graphJSON2,
                           graphJSON3=graphJSON3, graphJSON4=graphJSON4)


@app.route("/selected", methods=['POST'])
def selected():
    drawBarchart1()
    drawBarchart2()
    myvariable = request.form.getlist("colours")
    print(myvariable)
    return render_template("visualization1.html", colours=colours)


@app.route("/John/<qid>/<idd>/")
def John(qid, idd):
    result1 = printquestion(versionID)
    qidint = int(qid)
    iddint = int(idd)
    vi = getsurveyID()
    quesid = printquestionnumbers(vi)
    realquesid = int(quesid[qidint - 1])
    queryy = f"SELECT * FROM answer where userID = {useriddd} and questionID = {realquesid};"
    inter4 = cursor.execute(queryy)
    if inter4 == 0:
        queryy = f"INSERT INTO a19lightgame.answer (userID,questionID,answer) VALUES ({useriddd},{realquesid},{iddint});"
        cursor.execute(queryy)
    else:
        queryy = f"UPDATE answer SET answer={iddint} WHERE userID = {useriddd} AND questionID = {realquesid}"
        cursor.execute(queryy)
    conn.commit()
    qidint += 1
    qid = str(qidint)
    progress = progressbar()
    filledresult, qidd = previousanswers()
    if progress == 100:
        return redirect(url_for('userinfo'))
    else:
        return render_template("homapage.html", result=result1, scroll=qid, progress=progress,
                               filledresult=filledresult,
                               qidd=qidd)


@app.route("/userinfo")
def userinfo():
    return render_template("userInfo.html")


@app.route("/userinfosubmit", methods=['GET', 'POST'])
def userinfosubmit():
    name = request.form['name']
    email = request.form['email']
    age = int(request.form['age'])
    gender = request.form.get('gender')
    profession = request.form.get('profession')
    queryy = f"UPDATE user SET namee='{name}',email='{email}',age={age},gender='{gender}',profession='{profession}' where iduser = {useriddd};"
    cursor.execute(queryy)
    conn.commit()
    return redirect(url_for('welcome'))


@app.route("/")
def welcome():
    global versionID
    versionID = getsurveyID()
    global useriddd
    useriddd = getuserID()
    return render_template("welcome.html", id=versionID)


@app.route('/additionalvisual')
def additionalvisual():
    graphjson4, graphjson2, graphjson3 = drawBarchartadditional()
    return render_template('additionalvisual.html', graphJSON4=graphjson4, graphJSON2=graphjson2, graphJSON=graphjson3)


if __name__ == "__main__":
    app.run(debug=True)
