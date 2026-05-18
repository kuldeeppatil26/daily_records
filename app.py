from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_from_directory

import json

import os

import webbrowser

from threading import Timer

from datetime import datetime



app = Flask(__name__)

# In a production environment, this should be an environment variable

app.secret_key = 'python_coder_secure_key_12345'



# CONFIGURATION

REGISTRY_FILE = 'users_registry.json'

APP_PORT = 8080



# --- DATABASE UTILITIES ---



def initialize_registry():

    """Ensures the user registry exists and is valid JSON."""

    if not os.path.exists(REGISTRY_FILE) or os.stat(REGISTRY_FILE).st_size == 0:

        with open(REGISTRY_FILE, 'w') as f:

            json.dump({}, f)



def get_user_data_path(username):

    """Generates a unique filename for each user."""

    return f'{username}_work_data.json'



def load_registry():

    initialize_registry()

    with open(REGISTRY_FILE, 'r') as f:

        try:

            return json.load(f)

        except json.JSONDecodeError:

            return {}



def save_registry(data):

    with open(REGISTRY_FILE, 'w') as f:

        json.dump(data, f, indent=2)



def load_user_data(username):

    path = get_user_data_path(username)

    if not os.path.exists(path):

        initial = { 'lab': [], 'rnd': [], 'office': [], 'learning': [] }

        save_user_data(username, initial)

        return initial

    with open(path, 'r') as f:

        try:

            return json.load(f)

        except json.JSONDecodeError:

            return { 'lab': [], 'rnd': [], 'office': [], 'learning': [] }



def save_user_data(username, data):

    path = get_user_data_path(username)

    with open(path, 'w') as f:

        json.dump(data, f, indent=2)



# --- ROUTES ---



@app.route('/background_img')

def get_image():

    return send_from_directory(os.getcwd(), 'Gemini_Generated_Image_bxw6t5bxw6t5bxw6.png')



@app.route('/')

def index():

    return render_template_string(HTML_TEMPLATE)



@app.route('/api/register', methods=['POST'])

def register():

    req = request.json

    username = req.get('username', '').strip().lower()

    password = req.get('password')

    answer = req.get('security_answer', '').strip().lower()

   

    if not username or not password:

        return jsonify({'status': 'error', 'message': 'Username and Password required'}), 400

   

    registry = load_registry()

    if username in registry:

        return jsonify({'status': 'error', 'message': 'User ID already exists'}), 400

   

    registry[username] = {

        'password': password,

        'security_answer': answer

    }

    save_registry(registry)

    session['user'] = username

    return jsonify({'status': 'success'})



@app.route('/api/login', methods=['POST'])

def login():

    req = request.json

    username = req.get('username', '').strip().lower()

    password = req.get('password', '')

   

    registry = load_registry()

    user_record = registry.get(username)

   

    if user_record:

        stored_password = user_record['password'] if isinstance(user_record, dict) else user_record

        if stored_password == password:

            session['user'] = username

            return jsonify({'status': 'success'})

           

    return jsonify({'status': 'error', 'message': 'Invalid ID or Password'}), 401



@app.route('/api/reset-password', methods=['POST'])

def reset_password():

    req = request.json

    username = req.get('username', '').strip().lower()

    answer = req.get('security_answer', '').strip().lower()

    new_password = req.get('new_password', '')

   

    registry = load_registry()

    user_record = registry.get(username)

   

    if user_record and isinstance(user_record, dict) and user_record.get('security_answer') == answer:

        user_record['password'] = new_password

        save_registry(registry)

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Security answer incorrect or user not found'}), 401



@app.route('/api/change-password', methods=['POST'])

def change_password():

    if 'user' not in session:

        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

   

    req = request.json

    current_pass = req.get('current_password', '')

    new_pass = req.get('new_password', '')

   

    registry = load_registry()

    user_record = registry.get(session['user'])

   

    stored_password = user_record['password'] if isinstance(user_record, dict) else user_record

   

    if stored_password == current_pass:

        if isinstance(user_record, dict):

            user_record['password'] = new_pass

        else:

            registry[session['user']] = {'password': new_pass, 'security_answer': ''}

        save_registry(registry)

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Current password incorrect'}), 401



@app.route('/api/logout')

def logout():

    session.pop('user', None)

    return redirect(url_for('index'))



@app.route('/api/data', methods=['GET'])

def get_data():

    if 'user' not in session:

        return jsonify({'error': 'unauthorized'}), 401

    return jsonify(load_user_data(session['user']))



@app.route('/api/save', methods=['POST'])

def update_data():

    if 'user' not in session:

        return jsonify({'error': 'unauthorized'}), 401

    save_user_data(session['user'], request.json)

    return jsonify({'status': 'success'})



def open_browser():

    if not os.environ.get('WERKZEUG_RUN_MAIN'):

        webbrowser.open(f'http://127.0.0.1:{APP_PORT}/')



# --- UI TEMPLATE ---

HTML_TEMPLATE = '''

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>Daily Work Organizer</title>

    <style>

        body { font-family: 'Segoe UI', sans-serif; margin: 0; text-align: center; position: relative; transition: background 0.3s; min-height: 100vh; }

        body::before {

            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;

            background-image: url("/background_img");

            background-size: cover; background-position: center; background-repeat: no-repeat;

            opacity: 0.20; z-index: -1;

        }

        body.lab-bg { background:#ffd9df; }

        body.rnd-bg { background:#dff8e8; }

        body.office-bg { background:#fff4cc; }

        body.learning-bg { background:#dce9ff; }

       

        .hidden { display:none !important; }

       

        #authOverlay { position: fixed; top:0; left:0; width:100%; height:100%; background:white; z-index: 1000; display:flex; justify-content:center; align-items:center; }

        .auth-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 350px; }

        .auth-input { width: 92%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; }

        .auth-btn { width: 98%; padding: 12px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px; }

       

        .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: rgba(255,255,255,0.7); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }

        .title { font-size: 32px; font-weight: bold; }

       

        .folders { display: flex; justify-content: center; gap: 40px; margin-top: 60px; }

        .folder {

            width: 180px; height: 130px; border-radius: 0 12px 12px 12px;

            position: relative; padding-top: 40px; font-weight: bold;

            cursor: pointer; color: black; box-shadow: 0 4px 15px rgba(0,0,0,0.1);

            transition: transform 0.2s;

        }

        .folder::before {

            content: ""; position: absolute; top: -15px; left: 0; width: 80px; height: 15px;

            background: inherit; border-radius: 10px 10px 0 0;

        }

        .folder:hover { transform: scale(1.05); }

        .lab { background:#e06c78; } .rnd { background:#66c17a; } .office { background:#e6c36a; } .learning { background:#4a83d8; }

       

        .entry { background: rgba(255,255,255,0.95); padding: 15px; margin: 15px auto; width: 75%; border-radius: 10px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

        .days-old { font-size: 0.85em; color: #d32f2f; font-weight: normal; margin-left: 10px; font-style: italic; }

       

        button { cursor: pointer; padding: 8px 15px; border-radius: 5px; border: 1px solid #ccc; background: white; }

        input, textarea { padding: 10px; border-radius: 5px; border: 1px solid #ccc; }

    </style>

</head>

<body>



    <div id="authOverlay" class="{% if session.user %}hidden{% endif %}">

        <div class="auth-card" id="loginCard">

            <h2>Login</h2>

            <input type="text" id="loginUser" class="auth-input" placeholder="User ID">

            <input type="password" id="loginPass" class="auth-input" placeholder="Password">

            <button onclick="handleAuth('login')" class="auth-btn">Enter Organizer</button>

            <p style="font-size: 0.8em; margin-top:15px;">

                <span style="color:blue; cursor:pointer" onclick="switchAuth('reg')">Register</span> |

                <span style="color:blue; cursor:pointer" onclick="switchAuth('forgot')">Forgot Password?</span>

            </p>

        </div>



        <div class="auth-card hidden" id="registerCard">

            <h2>Create Account</h2>

            <input type="text" id="regUser" class="auth-input" placeholder="User ID">

            <input type="password" id="regPass" class="auth-input" placeholder="Password">

            <p style="font-size:0.75em; color:gray; text-align:left; margin-left:10px;">Security: What is your favorite color?</p>

            <input type="text" id="regAnswer" class="auth-input" placeholder="Your Answer">

            <button onclick="handleAuth('register')" class="auth-btn">Register</button>

            <p style="font-size: 0.8em; margin-top:15px; color:blue; cursor:pointer" onclick="switchAuth('login')">Back to Login</p>

        </div>



        <div class="auth-card hidden" id="forgotCard">

            <h2>Reset Password</h2>

            <input type="text" id="forgotUser" class="auth-input" placeholder="User ID">

            <p style="font-size:0.75em; color:gray; text-align:left; margin-left:10px;">Security Check: Favorite Color?</p>

            <input type="text" id="forgotAnswer" class="auth-input" placeholder="Your Security Answer">

            <input type="password" id="forgotNewPass" class="auth-input" placeholder="New Password">

            <button onclick="handleAuth('reset')" class="auth-btn">Update Password</button>

            <p style="font-size: 0.8em; margin-top:15px; color:blue; cursor:pointer" onclick="switchAuth('login')">Back to Login</p>

        </div>

    </div>



    <div id="mainApp" class="{% if not session.user %}hidden{% endif %}">

        <div class="header-bar">

            <span>User: <strong>{{ session.user }}</strong> | <span style="color:blue; cursor:pointer; font-size:0.85em;" onclick="showChangePass()">Change Password</span></span>

            <div class="title">📁 Daily Organizer</div>

            <button onclick="location.href='/api/logout'">Logout</button>

        </div>



        <div id="changePassModal" class="hidden" style="background:rgba(0,0,0,0.1); padding:10px; margin:10px; border-radius:10px;">

            <input type="password" id="currPass" placeholder="Current Password">

            <input type="password" id="newPass" placeholder="New Password">

            <button onclick="handleAuth('change')">Update</button>

            <button onclick="showChangePass()">Cancel</button>

        </div>



        <div id="home">

            <div style="margin-top: 40px;">

                <input type="text" id="searchInput" placeholder="Search entries..." style="width: 300px;">

                <button onclick="searchWork()">🔍 Search</button>

                <button onclick="clearSearch()">🧹 Clear</button>

            </div>

            <div id="searchResults"></div>

            <div class="folders">

                <div class="folder lab" onclick="openFolder('lab')">Lab Work</div>

                <div class="folder rnd" onclick="openFolder('rnd')">R&D</div>

                <div class="folder office" onclick="openFolder('office')">Office</div>

                <div class="folder learning" onclick="openFolder('learning')">Learning</div>

            </div>

        </div>



        <div id="folderView" class="hidden">

            <div style="width:75%; margin:20px auto; display:flex; justify-content:space-between; align-items: center;">

                <button onclick="goHome()">⬅ Back</button>

                <h2 id="folderTitle" style="margin:0;"></h2>

                <div style="width: 60px;"></div>

            </div>

            <textarea id="folderWorkInput" placeholder="Enter work details..." style="width:75%; height:100px;"></textarea><br>

            <input type="date" id="workDate" style="margin-top:10px;"><br>

            <button onclick="addWork()" style="background:#333; color:white; font-weight: bold; margin-top:10px;">➕ Add Entry</button>

            <div id="entries" style="margin-top: 20px;"></div>

        </div>

    </div>



    <script>

        let data = { lab:[], rnd:[], office:[], learning:[] };

        let currentCategory = "";



        function switchAuth(mode) {

            document.getElementById('loginCard').classList.add('hidden');

            document.getElementById('registerCard').classList.add('hidden');

            document.getElementById('forgotCard').classList.add('hidden');

            if(mode === 'login') document.getElementById('loginCard').classList.remove('hidden');

            if(mode === 'reg') document.getElementById('registerCard').classList.remove('hidden');

            if(mode === 'forgot') document.getElementById('forgotCard').classList.remove('hidden');

        }



        function showChangePass() {

            document.getElementById('changePassModal').classList.toggle('hidden');

        }



        async function handleAuth(action) {

            let payload = {};

            let url = "";



            if(action === 'login') {

                url = "/api/login";

                payload = { username: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value };

            } else if(action === 'register') {

                url = "/api/register";

                payload = {

                    username: document.getElementById('regUser').value,

                    password: document.getElementById('regPass').value,

                    security_answer: document.getElementById('regAnswer').value

                };

            } else if(action === 'reset') {

                url = "/api/reset-password";

                payload = {

                    username: document.getElementById('forgotUser').value,

                    security_answer: document.getElementById('forgotAnswer').value,

                    new_password: document.getElementById('forgotNewPass').value

                };

            } else if(action === 'change') {

                url = "/api/change-password";

                payload = {

                    current_password: document.getElementById('currPass').value,

                    new_password: document.getElementById('newPass').value

                };

            }



            try {

                const res = await fetch(url, {

                    method: 'POST',

                    headers: {'Content-Type': 'application/json'},

                    body: JSON.stringify(payload)

                });



                const result = await res.json();

                if(res.ok) {

                    alert("Success!");

                    if(action !== 'change') location.reload();

                    else showChangePass();

                } else {

                    alert(result.message || "Operation failed");

                }

            } catch (err) {

                alert("Server connection failed");

            }

        }



        async function fetchData() {

            const r = await fetch('/api/data');

            if(r.ok) { data = await r.json(); render(); }

        }



        async function sync() {

            await fetch('/api/save', {

                method: 'POST',

                headers: {'Content-Type': 'application/json'},

                body: JSON.stringify(data)

            });

        }



        function calculateDaysOld(dateStr) {

            if (!dateStr) return "";

            const parts = dateStr.split('-');

            const entryDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));

            const today = new Date();

            today.setHours(0, 0, 0, 0);

            const diffDays = Math.floor((today - entryDate) / (1000 * 60 * 60 * 24));

            return diffDays === 0 ? "0 days old" : (diffDays < 0 ? "Future" : diffDays + " days old");

        }



        async function addWork() {

            let t = document.getElementById("folderWorkInput").value.trim();

            let d = document.getElementById("workDate").value;

            if(!t) return alert("Enter details");

            let dateObj = d ? new Date(d) : new Date();

            const display = dateObj.getDate() + "-" + dateObj.toLocaleDateString('en-GB', {month:'long'});

            const raw = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;

            const newEntry = { id: Date.now(), rawDate: raw, displayDate: display, tasks: t.split("\\n") };

            data[currentCategory].unshift(newEntry);

            await sync();

            document.getElementById("folderWorkInput").value = "";

            render();

        }



        function render() {

            if(!currentCategory) return;

            let html = "";

            const sorted = [...data[currentCategory]].sort((a, b) => b.rawDate.localeCompare(a.rawDate));

            sorted.forEach(e => {

                html += `

                    <div class="entry">

                        <div style="display:flex; justify-content:space-between; align-items: center;">

                            <div style="display: flex; align-items: baseline;">

                                <h4 style="margin:0;">📅 ${e.displayDate}</h4>

                                <span class="days-old">${calculateDaysOld(e.rawDate)}</span>

                            </div>

                            <div>

                                <button onclick="editEntry('${currentCategory}',${e.id})">✏️</button>

                                <button onclick="deleteEntry('${currentCategory}',${e.id})">🗑️</button>

                            </div>

                        </div>

                        <div id="content-${e.id}">

                            <ul>${e.tasks.map(x=>`<li>${x}</li>`).join("")}</ul>

                        </div>

                    </div>`;

            });

            document.getElementById("entries").innerHTML = html || "<p>No entries found.</p>";

        }



        function editEntry(category, id) {

            let entry = data[category].find(e => e.id === id);

            document.getElementById(`content-${id}`).innerHTML = `

                <textarea id="edit-input-${id}" style="width:98%; height:80px; margin-top:10px;">${entry.tasks.join("\\n")}</textarea><br>

                <button onclick="saveEdit('${category}',${id})" style="background:#4caf50; color:white; border:none; padding:5px 10px; margin-top:5px;">Save</button>

                <button onclick="render()" style="margin-top:5px;">Cancel</button>

            `;

        }



        async function saveEdit(category, id) {

            let val = document.getElementById(`edit-input-${id}`).value.trim();

            data[category].find(e => e.id === id).tasks = val.split("\\n");

            await sync(); render();

        }



        async function deleteEntry(category, id) {

            if(confirm("Delete?")) {

                data[category] = data[category].filter(e => e.id !== id);

                await sync(); render();

            }

        }



        function openFolder(cat) {

            currentCategory = cat;

            document.body.className = cat+"-bg";

            document.getElementById("home").classList.add("hidden");

            document.getElementById("folderView").classList.remove("hidden");

            document.getElementById("folderTitle").innerText = cat.toUpperCase();

            render();

        }



        function goHome() {

            document.body.className = "";

            document.getElementById("folderView").classList.add("hidden");

            document.getElementById("home").classList.remove("hidden");

            currentCategory = "";

        }



        function searchWork(){

            let kw = document.getElementById("searchInput").value.toLowerCase();

            if(!kw) return;

            let res = "<h3>Search Results:</h3>";

            let found = false;

            for(let cat in data){

                data[cat].forEach(e => {

                    let matches = e.tasks.filter(t => t.toLowerCase().includes(kw));

                    if(matches.length > 0) {

                        found = true;

                        res += `<div class="entry"><strong>${e.displayDate} (${cat})</strong><ul>${matches.map(m=>`<li>${m}</li>`).join("")}</ul></div>`;

                    }

                });

            }

            document.getElementById("searchResults").innerHTML = found ? res : "<p>No results found.</p>";

        }



        function clearSearch(){

            document.getElementById("searchInput").value = "";

            document.getElementById("searchResults").innerHTML = "";

        }



        {% if session.user %}

        window.onload = fetchData;

        {% endif %}

    </script>

</body>

</html>

'''



if __name__ == '__main__':

    initialize_registry()

    Timer(1.5, open_browser).start()

    app.run(port=APP_PORT, debug=False)
