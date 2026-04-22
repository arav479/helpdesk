from flask import Flask,request,render_template
import subprocess
import os

app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")

@app.route('/')
def home():
    return render_template("login.html")


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
                if len(parts) >= 8:
                    tickets.append({
                        "id": parts[0],
                        "topic": parts[1],
                        "summary": parts[2],
                        "explanation": parts[3],
                        "location": parts[4],
                        "dept": parts[5],
                        "mobile": parts[6],
                        "time": parts[7],
                        "status": "Pending"
                    })
        else:
            # Fallback to direct file reading
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_credentials.txt")
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) >= 7:
                            tickets.append({
                                "id": f"TK-{len(tickets)+1:03d}",
                                "topic": parts[0],
                                "summary": parts[1],
                                "explanation": parts[2],
                                "location": parts[3],
                                "dept": parts[4],
                                "mobile": parts[5],
                                "time": parts[6],
                                "status": "Pending"
                            })
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
            return render_template("admin_dashboard.html", tickets=fetch_tickets())
        elif output == "SUCCESS:user":
            return render_template("user_dashboard.html", tickets=fetch_tickets())
        else:
            return "<h1>Login Failed: Invalid Email or Password</h1><a href='/'>Try again</a>"
    
    if role == 'admin':
        return render_template("admin_dashboard.html", tickets=fetch_tickets())
    else:
        return render_template("user_dashboard.html", tickets=fetch_tickets())

@app.route('/ticket_credentials', methods=['POST']) 
def ticket_credentials():
    helptopic = request.form.get('helptopic')
    issue_summary = request.form['issue_summary']
    problem_explaination = request.form['problem_explaination']
    location = request.form['location']
    Department_Hostel = request.form['Department/Hostel']
    mobilenumber = request.form['mobilenumber']
    preferred_time = request.form['preferred_time']

    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")

    result=subprocess.run(
        [exe_path,helptopic,issue_summary,problem_explaination,location,Department_Hostel,mobilenumber,preferred_time],
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
    return render_template("admin_dashboard.html",tickets=tickets)
if __name__ == "__main__":
    app.run(debug=True)