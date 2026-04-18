from flask import Flask,request,render_template
import subprocess
import os


app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")

@app.route('/')
def home():
    return render_template("login.html")

<<<<<<< HEAD
=======


>>>>>>> 01abd88acfb3e69120a35dc32580a7190aa35a7c
@app.route('/create', methods=['POST'])
def create():
    email = request.form['email'] #to access the email in entire program
    password = request.form['password']  #to store password
    role=request.form.get('role')  #to find whether the person is admin or user

    
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.exe")# Use absolute path to avoid "File Not Found" errors on Windows

    result = subprocess.run(
<<<<<<< HEAD
        [exe_path,'register', email, password,role],
=======
        [exe_path, email, password,role],
>>>>>>> 01abd88acfb3e69120a35dc32580a7190aa35a7c
        capture_output=True,
        text=True
    )
    if role=='admin':
        return render_template("admin_dashboard.html")
    if role=='user':
        return render_template("user_dashboard.html")
<<<<<<< HEAD


@app.route('/ticket_credentials',methods=['POST']) 

def ticket_credentials():
    helptopic=request.form.get('helptopic')
    issue_summary=request.form['issue_summary']
    problem_explaination=request.form['problem_explaination']
    location=request.form['location']
    Department_Hostel=request.form['Department/Hostel']
    mobilenumber=request.form['mobilenumber']
    preferred_time=request.form['preferred_time']
=======
@app.route('/ticket_credentials',methods=['POST']) 
def ticket_credentials():
    helptopic=request.form.get('helptopic')
    issue_summary=request.form('issue_summary')
    problem_explaination=request.form('problem_explaination')
    location=request.form('location')
    Department_Hostel=request.form('Department/Hostel')
    mobilenumber=request.form('mobilenumber')
    preferred_time=request.form('preferred_time')
>>>>>>> 01abd88acfb3e69120a35dc32580a7190aa35a7c

    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")

    result=subprocess.run(
        [exe_path,helptopic,issue_summary,problem_explaination,location,Department_Hostel,mobilenumber,preferred_time],
        capture_output=True,
        text=True)
    if result:
        return "<h1>Ticket created Successfully</h1>"
<<<<<<< HEAD
=======






>>>>>>> 01abd88acfb3e69120a35dc32580a7190aa35a7c
if __name__ == "__main__":
    app.run(debug=True)