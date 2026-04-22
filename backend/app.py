from flask import Flask,request,render_template
import subprocess
import os

app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/create', methods=['POST'])
def create():
    email = request.form['email']#from the form to python and these are send as input in terminal of c program
    password = request.form['password']
    role = request.form.get('role')
    
    # Get project root (one level up from backend/)

    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.exe")
    
    # Check if 'signin' or 'login' button was clicked
    if 'signin' in request.form:
        result = subprocess.run(
            [exe_path, 'register', email, password, role],
            capture_output=True,
            text=True,
            
        )
       
    elif 'login' in request.form:
        result = subprocess.run(
            [exe_path, 'login', email, password],
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        if output == "SUCCESS:admin": 
            return render_template("admin_dashboard.html")
        elif output == "SUCCESS:user":
            return render_template("user_dashboard.html")
        else:
            return "<h1>Login Failed: Invalid Email or Password</h1><a href='/'>Try again</a>"
    


    if role == 'admin':
        return render_template("admin_dashboard.html")
    else:
        return render_template("user_dashboard.html")


@app.route('/ticket_credentials',methods=['POST']) 

def ticket_credentials():
    helptopic=request.form.get('helptopic')
    issue_summary=request.form['issue_summary']
    problem_explaination=request.form['problem_explaination']
    location=request.form['location']
    Department_Hostel=request.form['Department/Hostel']
    mobilenumber=request.form['mobilenumber']
    preferred_time=request.form['preferred_time']

    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")

    result=subprocess.run(
        [exe_path,helptopic,issue_summary,problem_explaination,location,Department_Hostel,mobilenumber,preferred_time],
        capture_output=True,
        text=True)
    if result:
        return render_template("ticket_confirmation.html")
if __name__ == "__main__":
    app.run(debug=True)