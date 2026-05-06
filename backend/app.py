from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from datetime import datetime
import subprocess
import os


app = Flask(__name__,template_folder='../frontend',static_folder="../frontend")
app.secret_key = 'some_very_secret_key'

NOTIFICATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notifications.txt')
USER_DETAILS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'userdetails.txt')

VALID_ROLES = {'user', 'admin'}

@app.context_processor
def inject_theme():
    return {'theme': session.get('theme', 'light')}

def read_users():
    users = []
    try:
        if not os.path.exists(USER_DETAILS_FILE):
            return users

        with open(USER_DETAILS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                users.append({
                    'email': parts[0],
                    'password': parts[1],
                    'role': parts[2].lower()
                })
    except Exception as e:
        print(f"Error reading users: {e}")
    return users

def find_user(email, password, role):
    email = email.strip().lower()
    role = role.strip().lower()
    for user in read_users():
        if (
            user['email'].lower() == email
            and user['password'] == password
            and user['role'] == role
        ):
            return user
    return None

def user_role_exists(email, role):
    email = email.strip().lower()
    role = role.strip().lower()
    for user in read_users():
        if user['email'].lower() == email and user['role'] == role:
            return True
    return False

def register_user(email, password, role):
    role = role.strip().lower()
    if role not in VALID_ROLES:
        return False, "Please choose a valid role."

    if user_role_exists(email, role):
        return False, f"This email is already registered as {role}."

    try:
        with open(USER_DETAILS_FILE, 'a') as f:
            f.write(f"{email.strip()} {password} {role}\n")
        return True, "Registration successful."
    except Exception as e:
        print(f"Error registering user: {e}")
        return False, "Registration failed. Please try again."

def open_dashboard_for_role(role, email):
    session['email'] = email
    session['role'] = role

    if role == 'admin':
        return render_template("admin_dashboard.html", tickets=fetch_tickets(), Email=email, current_page='dashboard')

    return render_template("user_dashboard.html", tickets=fetch_user_tickets(), Email=email)

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

def build_role_counts(users):
    counts = {'user': 0, 'admin': 0, 'engineer': 0}
    for user in users:
        role = user.get('role', '').lower()
        if role in counts:
            counts[role] += 1
    return counts

def require_role(role_name):
    if session.get('role') != 'admin' and role_name == 'admin':
        return redirect(url_for('home'))
    if session.get('role') != role_name:
        return redirect(url_for('home'))
    return None
@app.route('/dashboard')
def dashboard():
    role = session.get('role')
    email = session.get('email')
    
    if role == 'admin':
        tickets = fetch_tickets()
        return render_template("admin_dashboard.html", tickets=tickets, Email=email, current_page='dashboard')
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
    return render_template("admin_dashboard.html", tickets=tickets, Email=email, current_page='dashboard')

@app.route('/ticket/<ticket_id>')
def ticket_details(ticket_id):
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticket_update.exe")
    result = subprocess.run(
        [exe_path, 'details', ticket_id],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        flash(f"Ticket {ticket_id} not found.", "info")
        return redirect(url_for('dashboard'))

    parts = result.stdout.strip().split("|")
    if len(parts) < 9:
        flash(f"Ticket {ticket_id} details are incomplete.", "info")
        return redirect(url_for('dashboard'))

    ticket = {
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
    }

    role = session.get('role')
    dashboard_route = url_for('engineer_dashboard') if role == 'engineer' else url_for('dashboard')
    return render_template("ticket_details.html", ticket=ticket, Email=session.get('email'), role=role, dashboard_route=dashboard_route)

@app.route('/create', methods=['POST'])
def create():
    email = request.form['email'].strip()
    password = request.form['password']
    role = request.form.get('role', 'user').lower()

    if role not in VALID_ROLES:
        return render_template("login.html", error="Please choose User or Admin.")
    
    if 'signin' in request.form:
        success, message = register_user(email, password, role)
        if not success:
            return render_template("login.html", error=message)

        return open_dashboard_for_role(role, email)
       
    elif 'login' in request.form:
        user = find_user(email, password, role)
        if not user:
            return render_template("login.html", error=f"Invalid {role} email or password.")

        return open_dashboard_for_role(role, email)
    
    return render_template("login.html", error="Please choose SIGN IN or LOGIN.")

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
    return render_template("admin_dashboard.html", tickets=tickets, Email=session['email'], current_page='dashboard')

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
    if session.get('role') != 'user':
        return redirect(url_for('dashboard'))
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
    role = session.get('role')
    if not role:
        return redirect(url_for('home'))
    return render_template('support.html', role=role, email=session.get('email'), engineer_name=session.get('engineer_name'))

@app.route('/knowledge-base')
def knowledge_base():
    role = session.get('role')
    if not role:
        return redirect(url_for('home'))
    return render_template('knowledge_base.html', role=role, email=session.get('email'), engineer_name=session.get('engineer_name'))

@app.route('/admin/active-tickets')
def admin_active_tickets():
    blocked = require_role('admin')
    if blocked:
        return blocked
    tickets = [ticket for ticket in fetch_tickets() if ticket.get('status') != 'Completed']
    return render_template('active_tickets.html', tickets=tickets, Email=session.get('email'), current_page='active')

@app.route('/admin/resolved-tickets')
def admin_resolved_tickets():
    blocked = require_role('admin')
    if blocked:
        return blocked
    tickets = [ticket for ticket in fetch_tickets() if ticket.get('status') == 'Completed']
    return render_template('resolved_tickets.html', tickets=tickets, Email=session.get('email'), current_page='resolved')

@app.route('/admin/users')
def admin_user_management():
    blocked = require_role('admin')
    if blocked:
        return blocked
    users = read_users()
    return render_template('user_management.html', users=users, role_counts=build_role_counts(users), Email=session.get('email'), current_page='users')

@app.route('/admin/settings')
def admin_settings():
    blocked = require_role('admin')
    if blocked:
        return blocked
    tickets = fetch_tickets()
    open_tickets = len([ticket for ticket in tickets if ticket.get('status') != 'Completed'])
    return render_template('admin_settings.html', Email=session.get('email'), current_page='settings', user_count=len(read_users()), open_tickets=open_tickets, completed_tickets=len(tickets) - open_tickets, notification_file=os.path.basename(NOTIFICATIONS_FILE))

@app.route('/settings')
def user_settings():
    if session.get('role') != 'user':
        return redirect(url_for('dashboard'))
    tickets = fetch_user_tickets()
    open_tickets = len([ticket for ticket in tickets if ticket.get('status') != 'Completed'])
    return render_template('user_settings.html', Email=session.get('email'), ticket_count=len(tickets), open_tickets=open_tickets, completed_tickets=len(tickets) - open_tickets)

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    session['theme'] = 'dark' if session.get('theme', 'light') == 'light' else 'light'
    return redirect(request.referrer or url_for('dashboard'))

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




