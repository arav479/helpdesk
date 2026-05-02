from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from datetime import datetime
import subprocess
import os


app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")
app.secret_key = 'some_very_secret_key'

NOTIFICATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notifications.txt')

def load_notifications(engineer_name):
    """Load notifications for a specific engineer from file"""
    notifications = []
    try:
        if os.path.exists(NOTIFICATIONS_FILE):
            with open(NOTIFICATIONS_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('|')
                    # Format: engineer_name|type|title|message|timestamp|read
                    if len(parts) >= 6 and parts[0] == engineer_name:
                        notifications.append({
                            'engineer': parts[0],
                            'type': parts[1],
                            'title': parts[2],
                            'message': parts[3],
                            'timestamp': parts[4],
                            'read': parts[5] == '1'
                        })
    except Exception as e:
        print(f"Error loading notifications: {e}")
    # Return newest first
    notifications.reverse()
    return notifications

def add_notification(engineer_name, notif_type, title, message):
    """Add a notification for an engineer"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        with open(NOTIFICATIONS_FILE, 'a') as f:
            f.write(f"{engineer_name}|{notif_type}|{title}|{message}|{timestamp}|0\n")
    except Exception as e:
        print(f"Error adding notification: {e}")

def get_unread_count(engineer_name):
    """Get the count of unread notifications for an engineer"""
    count = 0
    try:
        if os.path.exists(NOTIFICATIONS_FILE):
            with open(NOTIFICATIONS_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 6 and parts[0] == engineer_name and parts[5] == '0':
                        count += 1
    except:
        pass
    return count

def mark_notifications_read(engineer_name):
    """Mark all notifications as read for an engineer"""
    try:
        if not os.path.exists(NOTIFICATIONS_FILE):
            return
        lines = []
        with open(NOTIFICATIONS_FILE, 'r') as f:
            lines = f.readlines()
        with open(NOTIFICATIONS_FILE, 'w') as f:
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 6 and parts[0] == engineer_name:
                    parts[5] = '1'
                    f.write('|'.join(parts) + '\n')
                else:
                    f.write(line)
    except Exception as e:
        print(f"Error marking notifications read: {e}")

def clear_notifications(engineer_name):
    """Clear all notifications for an engineer"""
    try:
        if not os.path.exists(NOTIFICATIONS_FILE):
            return
        lines = []
        with open(NOTIFICATIONS_FILE, 'r') as f:
            lines = f.readlines()
        with open(NOTIFICATIONS_FILE, 'w') as f:
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 6 and parts[0] == engineer_name:
                    continue  # Skip this engineer's notifications
                f.write(line)
    except Exception as e:
        print(f"Error clearing notifications: {e}")

@app.route('/')
def home():
    return render_template("login.html")

# ======== SEPARATE ENGINEER LOGIN PAGE ========
@app.route('/engineer_login', methods=['GET', 'POST'])
def engineer_login_page():
    if request.method == 'GET':
        return render_template("engineer_login.html")
    
    # POST - handle engineer login
    email = request.form['email']
    password = request.form['password']
    
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.exe")
    result = subprocess.run(
        [exe_path, 'engineer_login', email, password],
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    
    if output.startswith("SUCCESS:engineer:"):
        engineer_name = output.split(":")[2]
        session['role'] = 'engineer'
        session['engineer_name'] = engineer_name
        session['email'] = email
        
        # Create a welcome notification for the engineer
        add_notification(
            engineer_name,
            'info',
            'Login Successful',
            f'Welcome back, {engineer_name}! You are now logged in.'
        )
        
        tickets = fetch_engineer_tickets(engineer_name)
        return render_template("engineer_dashboard.html", tickets=tickets, Email=email, EngineerName=engineer_name)
    else:
        return render_template("engineer_login.html", error="Invalid engineer email or password. Please try again.")

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
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned",
                        "status": parts[10].strip() if len(parts) > 10 else "Open"
                    })
        
    except Exception as e:
        print(f"Error fetching user tickets: {e}")
    
    return tickets

def fetch_tickets(query=None):
    tickets = []
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    
    try:
        # Attempt to get tickets using C executable
        if query:
            result = subprocess.run([exe_path, "search", query], capture_output=True, text=True)
        else:
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
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned",
                        "status": parts[10].strip() if len(parts) > 10 else "Open"
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
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned",
                        "status": parts[10].strip() if len(parts) > 10 else "Open"
                    })
                line = f.readline()
            f.close()
    except Exception as e:
        print(f"Error fetching tickets: {e}")
    
    return tickets

def fetch_engineer_tickets(engineer_name):
    """Fetch tickets assigned to a specific engineer"""
    tickets = []
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    try:
        result = subprocess.run(
            [exe_path, 'viewengineertickets', engineer_name],
            capture_output=True,
            text=True,
        )
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
                        "engineer": parts[9].strip() if len(parts) > 9 else "Unassigned",
                        "status": parts[10].strip() if len(parts) > 10 else "Open"
                    })
    except Exception as e:
        print(f"Error fetching engineer tickets: {e}")
    return tickets

@app.route('/dashboard')
def dashboard():
    role = session.get('role')
    email = session.get('email')
    
    if role == 'admin':
        tickets = fetch_tickets()
        return render_template("admin_dashboard.html", tickets=tickets, Email=email)
    elif role == 'engineer':
        engineer_name = session.get('engineer_name')
        tickets = fetch_engineer_tickets(engineer_name)
        return render_template("engineer_dashboard.html", tickets=tickets, Email=email, EngineerName=engineer_name)
    elif role == 'user':
        tickets = fetch_user_tickets()
        return render_template("user_dashboard.html", tickets=tickets, Email=email)
    else:
        return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('q')
    email = session.get('email')
    tickets = fetch_tickets(query)
    return render_template("admin_dashboard.html", tickets=tickets, Email=email)

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
        # Check if engineer login
        if role == 'engineer':
            result = subprocess.run(
                [exe_path, 'engineer_login', email, password],
                capture_output=True,
                text=True,
            )
            output = result.stdout.strip()
            if output.startswith("SUCCESS:engineer:"):
                engineer_name = output.split(":")[2]
                session['role'] = 'engineer'
                session['engineer_name'] = engineer_name
                session['email'] = email  # Store engineer name as email for display
                tickets = fetch_engineer_tickets(engineer_name)
                return render_template("engineer_dashboard.html", tickets=tickets, Email=email, EngineerName=engineer_name)
            else:
                return render_template("login.html", error="Invalid Engineer Name or Password")
        else:
            # Regular user/admin login
            result = subprocess.run(
                [exe_path, 'login', email, password],
                capture_output=True,
                text=True,
            )
            output = result.stdout.strip()
            if output == "SUCCESS:admin": 
                session['role'] = 'admin'
                return render_template("admin_dashboard.html", tickets=fetch_tickets(),Email=email)
            elif output == "SUCCESS:user":
                session['role'] = 'user'
                return render_template("user_dashboard.html", tickets=fetch_user_tickets(), Email=email)
            else:
                return render_template("login.html", error="Invalid Email or Password")
    
    if role == 'admin':
        session['role'] = 'admin'
        return render_template("admin_dashboard.html", tickets=fetch_tickets(),Email=email)
    elif role == 'engineer':
        session['role'] = 'engineer'
        return redirect(url_for('dashboard'))
    else:
        session['role'] = 'user'
        return render_template("user_dashboard.html", tickets=fetch_user_tickets(), Email=email)

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
    
    # Parse the C output for ASSIGNED: line
    assigned_engineer = "Unassigned"
    ticket_id = ""
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            if line.startswith("ASSIGNED:"):
                parts = line.replace("ASSIGNED:", "").split("|")
                assigned_engineer = parts[0] if len(parts) > 0 else "Unassigned"
                ticket_id = parts[1] if len(parts) > 1 else ""
    
    # Create notification for the assigned engineer
    if assigned_engineer != "Unassigned":
        add_notification(
            assigned_engineer,
            'new_ticket',
            'New Ticket Assigned',
            f'Ticket {ticket_id} - {helptopic}: {issue_summary} at {location}'
        )
    
    return render_template("ticket_confirmation.html", 
                           engineer=assigned_engineer, 
                           ticket_id=ticket_id)

@app.route('/delete', methods=['POST'])
def delete_ticket():
    ticket_id = request.form['ticket_id']
    
    # Find the engineer assigned to this ticket before deleting
    all_tickets = fetch_tickets()
    assigned_eng = None
    for t in all_tickets:
        if t['id'] == ticket_id:
            assigned_eng = t.get('engineer', 'Unassigned')
            break
    
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result=subprocess.run(
        [exe_path, 'close', ticket_id],
        capture_output=True,
        text=True,
        )
    print("Closed ticket and reassigned engineer:",ticket_id)
    
    # Notify the engineer that their ticket was closed by admin
    if assigned_eng and assigned_eng != 'Unassigned':
        add_notification(
            assigned_eng,
            'info',
            'Ticket Closed by Admin',
            f'Ticket {ticket_id} has been closed. You have been reassigned.'
        )
    
    flash(f"Ticket {ticket_id} closed and engineer reassigned.", "success")
    return redirect(url_for('dashboard'))

@app.route('/mark_done', methods=['POST'])
def mark_done():
    """Mark a ticket as completed and free the engineer"""
    ticket_id = request.form['ticket_id']
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result = subprocess.run(
        [exe_path, 'markdone', ticket_id],
        capture_output=True,
        text=True,
    )
    print("Mark done result:", result.stdout.strip())
    
    # Create notification for the engineer who completed the ticket
    engineer_name = session.get('engineer_name', '')
    if engineer_name:
        add_notification(
            engineer_name,
            'completed',
            'Ticket Completed',
            f'You successfully resolved ticket {ticket_id}. Great work!'
        )
    
    flash(f"Ticket {ticket_id} marked as DONE! Engineer is now available.", "success")
    return redirect(url_for('dashboard'))

@app.route('/assign_all_unassigned', methods=['POST'])
def assign_all_unassigned():
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result=subprocess.run(
        [exe_path, 'assignall'],
        capture_output=True,
        text=True,
        )
    print("Assigned all unassigned tickets")
    print(result.stdout)
    tickets=fetch_tickets()
    return render_template("admin_dashboard.html", tickets=tickets, Email=session['email'])

@app.route('/undo', methods=['POST'])
def undo_delete():
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result = subprocess.run(
        [exe_path, 'undo'],
        capture_output=True,
        text=True,
    )
    print("Undo result:", result.stdout.strip())
    flash("Last deletion undone successfully.", "info")
    return redirect(url_for('dashboard'))

@app.route('/viewmytickets', methods=['GET', 'POST'])
def view_my_tickets():
    tickets=fetch_user_tickets()
    return render_template("mytickets.html", tickets=tickets, Email=session.get('email'))

@app.route('/engineer_dashboard')
def engineer_dashboard():
    engineer_name = session.get('engineer_name')
    if not engineer_name:
        return redirect(url_for('home'))
    tickets = fetch_engineer_tickets(engineer_name)
    return render_template("engineer_dashboard.html", tickets=tickets, Email=session.get('email'), EngineerName=engineer_name)

@app.route('/support')
def support_page():
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('role', None)
    session.pop('engineer_name', None)
    return redirect(url_for('home'))

# ======== NOTIFICATION API ENDPOINTS ========

@app.route('/api/notifications')
def api_get_notifications():
    """API: Get notifications for the logged-in engineer"""
    engineer_name = session.get('engineer_name')
    if not engineer_name:
        return jsonify({'notifications': [], 'unread_count': 0})
    notifications = load_notifications(engineer_name)
    unread = get_unread_count(engineer_name)
    return jsonify({'notifications': notifications, 'unread_count': unread})

@app.route('/api/notifications/read', methods=['POST'])
def api_mark_read():
    """API: Mark all notifications as read for the logged-in engineer"""
    engineer_name = session.get('engineer_name')
    if engineer_name:
        mark_notifications_read(engineer_name)
    return jsonify({'status': 'ok'})

@app.route('/api/notifications/clear', methods=['POST'])
def api_clear_notifications():
    """API: Clear all notifications for the logged-in engineer"""
    engineer_name = session.get('engineer_name')
    if engineer_name:
        clear_notifications(engineer_name)
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(debug=True)