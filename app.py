import re
from flask import Flask, render_template, request,redirect,url_for,session
import pyodbc


server = 'tcp:adbsaahilserver.database.windows.net'
database = 'sqldatabase1'
username = 'serveradmin'
password = 'Spa12345'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)


app = Flask(__name__)
app.secret_key = 'any random string'

@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
            if request.form.get("lbutton"):
                uname = request.form["uname"]
                pwd = request.form["psw"]
                cursor = cnxn.cursor()
                cursor.execute("select role, username from users where username = '"+str(uname)+"' and pass = '"+str(pwd)+"';")
                search = cursor.fetchone()
                if str(search) != 'None':
                    print(search[0])
                    session['username'] = search[0]
                    session['name']= search[1]
                    if str(search[0]) =='admin':
                        return redirect('/main')

                    if str(search[0]) =='teacher':
                        return redirect('/main')

                    if str(search[0]) =='student':
                        return redirect('/student')
                else:
                    return render_template('login.html')

            else:
                
                return render_template('login.html')
    else: 
        return render_template('login.html')

@app.route('/main', methods=["POST", "GET"])
def main():
    if request.method == "POST":
            if request.form.get("lbutton"):
                user = session['name']
                question = request.form["questxt"]
                cursor = cnxn.cursor()
                cursor.execute("select username from users where role = 'student';")
                students = cursor.fetchall()
                for x in students:
                    cursor = cnxn.cursor()
                    cursor.execute("insert into qna (teacher,questions,student) values ('"+user+"','"+question+"','"+x[0]+"')")
                    cnxn.commit()
                    
                    
                return redirect('/main')

            else:
                
                return render_template('main.html')

    if request.method == "GET": 

        if 'username' in session:
            role = session['username']
            if role == 'admin' or role =='teacher':
                user = session['name']

                cursor = cnxn.cursor()
                cursor.execute("select * from qna")
                table = cursor.fetchall()

                return render_template('main.html' ,user=user,rows=table,item1='Teacher',item2='Questions',item3='Answers',item4='Student',item5='Grades',item6='edit')

            else:
                return render_template('student.html')
        
        else:
                
           return render_template('login.html')


@app.route('/logout', methods=["POST", "GET"])
def logout():

    session.pop('username', None)
    session.pop('name',None)
    return render_template('login.html')
        

@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == "POST":
            if request.form.get("lbutton"):
                uname = request.form["uname"]
                pwd = request.form["psw"]

            else:
                
                return render_template('student.html')
    else: 
        if 'username' in session:
            role = session['username']
            if role == 'student':
                user = session['name']

                cursor = cnxn.cursor()
                cursor.execute("select * from qna where answers is null and student = '"+user+"';")
                search = cursor.fetchall()

                return render_template('student.html', rows=search ,item1='Questions',item2='Click',user=user)
            else:
                return render_template('login.html')

        else:
            return render_template('login.html')


@app.route('/answers/<string:id_data>', methods = ['GET','POST'])

def answser(id_data):

    if request.method == "POST":
        if request.form.get("ansbutton"):
            user = session['name']
            ans = request.form["anstxt"]

            cursor = cnxn.cursor()
            cursor.execute("UPDATE qna SET answers = '"+ans+"' WHERE id = '"+id_data+"';")
            cnxn.commit()
            return redirect('/student')
        else:
            return render_template('answers.html')

    else:
        if 'username' in session:
            user = session['username']

            cursor = cnxn.cursor()
            cursor.execute("select questions from qna where id = '"+id_data+"'")
            one = cursor.fetchone()
            return render_template('answers.html',ques=one[0],user=user,id=id_data)
        else:
            return render_template('login.html')


@app.route('/update/<string:id_data>', methods = ['GET','POST'])

def grade(id_data):
    if request.method == "POST":
        if request.form.get("gradebutton"):
            user = session['name']
            dop = request.form["dropup"]

            cursor = cnxn.cursor()
            cursor.execute("UPDATE qna SET grades = '"+dop+"' WHERE id = '"+id_data+"';")
            cnxn.commit()
            return redirect('/main')
        else:
            return redirect('/main')

    else:
        if 'username' in session:
            user = session['username']

            cursor = cnxn.cursor()
            cursor.execute("select questions,answers,student from qna where id = '"+id_data+"'")
            one = cursor.fetchone()
            return render_template('grade.html',ques=one[0],answser=one[1],user=user,id=id_data,stud=one[2])
        else:
            return render_template('login.html')

if __name__ == '__main__':
    app.run(debug =True, host='0.0.0.0')