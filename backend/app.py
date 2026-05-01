from flask import Flask, request, render_template, session, redirect, url_for
import subprocess
import os


app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")
app.secret_key = 'some_very_secret_key'

@app.route('/')
def home():
    return render_template("login.html")

def fetch_user_tickets():
    tickets = []
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    try:
        email = session.get('email')
        if not email:
            return []
        result=subprocess.run(
            [exe_path, 'viewmytickets', email],
            capture_output=True,
            text=True,
            )
        tickets = []
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                parts = line.split("|")
                if len(parts) >= 9:
                    tickets.append({
                        "username": parts[0],
                        "id": parts[1],
                        "topic": parts[2],
                        "summary": parts[3],
                        "explanation": parts[4],
                        "location": parts[5],
                        "dept": parts[6],
                        "mobile": parts[7],
                        "time": parts[8],
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned"
                    })
        
    except Exception as e:
        print(f"Error fetching user tickets: {e}")
    
    return tickets

def fetch_tickets():
    tickets = []
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    
    try:
        # Attempt to get tickets using C executable
        result = subprocess.run([exe_path, "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                parts = line.split("|")
                if len(parts) >= 9:
                    tickets.append({
                        "username": parts[0],
                        "id": parts[1],
                        "topic": parts[2],
                        "summary": parts[3],
                        "explanation": parts[4],
                        "location": parts[5],
                        "dept": parts[6],
                        "mobile": parts[7],
                        "time": parts[8],
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned"
                    })
        else:
            f=open("ticket_credentials.txt",'r')
            line = f.readline()
            while line:
                parts = line.split("|")
                if len(parts) >= 9:
                    tickets.append({
                        "username": parts[0],
                        "id": parts[1],
                        "topic": parts[2],
                        "summary": parts[3],
                        "explanation": parts[4],
                        "location": parts[5],
                        "dept": parts[6],
                        "mobile": parts[7],
                        "time": parts[8],
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned"
                    })
                line = f.readline()
            f.close()
    except Exception as e:
        print(f"Error fetching tickets: {e}")
    
    return tickets

@app.route('/dashboard')
def dashboard():
    tickets = fetch_tickets()
    return render_template("user_dashboard.html", tickets=tickets)

@app.route('/create', methods=['POST'])
def create():
    email = request.form['email']#from the form to python and these are send as input in terminal of c program
    session['email'] = email
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
        output = result.stdout.strip()
        if "SUCCESS" in output:
            return render_template("login.html", success="Registration successful! Please login.")
        else:
            return render_template("login.html", error="Registration failed. Email might already exist.")
       
    elif 'login' in request.form:
        result = subprocess.run(
            [exe_path, 'login', email, password],
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        if output == "SUCCESS:admin": 
            return render_template("admin_dashboard.html", tickets=fetch_tickets(),Email=email)
        elif output == "SUCCESS:user":
            return render_template("user_dashboard.html",Email=email)
        else:
            return render_template("login.html", error="Invalid Email or Password")
    
    if role == 'admin':
        return render_template("admin_dashboard.html", tickets=fetch_tickets(),Email=email)
    else:
        return render_template("user_dashboard.html", tickets=fetch_tickets(),Email=email)

@app.route('/ticket_credentials', methods=['POST']) 
def ticket_credentials():
    helptopic = request.form.get('helptopic')
    issue_summary = request.form['issue_summary']
    problem_explaination = request.form['problem_explaination']
    location = request.form['location']
    Department_Hostel = request.form['Department/Hostel']
    mobilenumber = request.form['mobilenumber']
    preferred_time = request.form['preferred_time']
    email = session.get('email')
    if not email:
        return "Login failure", 401

    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")

    result=subprocess.run(
        [exe_path,helptopic,issue_summary,problem_explaination,location,Department_Hostel,mobilenumber,preferred_time,email],
        capture_output=True,
        text=True)
    if result:
        return render_template("ticket_confirmation.html")

@app.route('/delete', methods=['POST'])
def delete_ticket():
    ticket_id = request.form['ticket_id']
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result=subprocess.run(
        [exe_path, 'delete', ticket_id],
        capture_output=True,
        text=True,
        )
    print("Deleted:",ticket_id)
    tickets=fetch_tickets()
    return render_template("admin_dashboard.html", tickets=tickets, Email=session['email'])

@app.route('/viewmytickets', methods=['GET', 'POST'])
def view_my_tickets():
    tickets=fetch_user_tickets()
    return render_template("mytickets.html", tickets=tickets, Email=session.get('email'))
@app.route('/support')
def support_page():
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))
if __name__ == "__main__":
    app.run(debug=True)