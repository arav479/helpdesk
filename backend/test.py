from flask import Flask,request,render_template,session
import subprocess
import os
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


print(fetch_tickets())