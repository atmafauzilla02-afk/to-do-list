from flask import Flask, render_template, render_template_string, request, redirect, session, jsonify

from flask_mysqldb import MySQL
from datetime import date
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'todolist_flask'
mysql = MySQL(app)

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
<script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
<script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
body{background:#f4f5f7;font-family:'Segoe UI',sans-serif;}

.btn-primary{background:#e44232;border:none;}
.btn-primary:hover{background:#c63527;}
.sidebar{background:#fff;min-height:80vh;border-radius:12px;padding:1rem;}
.sidebar a{display:block;padding:0.5rem;border-radius:6px;text-decoration:none;color:#555;margin-bottom:0.3rem;transition: all 0.2s;}
.sidebar a:hover{background:#f0f0f0;color:#e44232;}
.task-item{border-radius:8px;padding:0.5rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between;transition: all 0.2s;cursor:move;}
.task-item:hover{background:#f9f9f9;}
.task-left{display:flex;align-items:center;}
.task-left span{margin-left:0.5rem;}
.delete-btn{display:none;cursor:pointer;}
.task-item:hover .delete-btn{display:inline-block;}
.checkbox{width:18px;height:18px;}
.edit-btn {
    display: none;       /* tersembunyi default */
    cursor: pointer;
    margin-right: 0.5rem;
    color: #0d6efd;
}

.task-item:hover .edit-btn {
    display: inline-block;   /* muncul saat hover */
}
.sidebar .dropdown-toggle::after {
    margin-left: auto;
}
.sidebar img {
    object-fit: cover;
}
.task-item {
    background: #fff;
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
}

.task-item:hover {
    background: #f7f7f7;
}

.checkbox {
    margin-right: 10px;
}
.app-layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: 260px;
    background: #fff;
    padding: 16px;
    border-right: 1px solid #e5e5e5;
}

.sidebar a {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 10px;
    border-radius: 6px;
    color: #444;
    text-decoration: none;
    font-size: 14px;
}

.sidebar a:hover {
    background: #f3f3f3;
    color: #d43c2c;
}

/* Main content */
.main-content {
    flex: 1;
    padding: 24px 32px;
    background: #f8f9fa;
}

/* Date group */
.date-group {
    margin-bottom: 24px;
}

.date-title {
    font-weight: 600;
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

/* Task row */
.task-row {
    background: #fff;
    border-radius: 10px;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}

.task-row:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

.task-row .left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.task-name {
    font-size: 15px;
    font-weight: 500;
}

.task-row .right {
    font-size: 13px;
    color: #888;
    display: flex;
    align-items: center;
    gap: 6px;
}
.date-title {
    font-weight: 600;
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

</style>
</head>
<body>
<div class="container-fluid py-4">
<div class="modal fade" id="editModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Edit Task</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form id="editForm">
            <input type="hidden" id="editTaskId" name="task_id">
            <input class="form-control mb-2" id="editTaskName" name="task" placeholder="Task" required>
            <select name="priority" id="editPriority" class="form-select mb-2">
                <option value="1">Low</option>
                <option value="2">Medium</option>
                <option value="3">High</option>
            </select>
            <input type="date" class="form-control mb-2" name="due_date" id="editDueDate">
            <button class="btn btn-primary w-100">Update</button>
        </form>
      </div>
    </div>
  </div>
</div>


<div class="app-layout">
    {% if session.get('uid') %}
    <aside class="sidebar">
        <div class="dropdown mb-4">
            <a class="d-flex align-items-center text-decoration-none dropdown-toggle" href="#" role="button"
               data-bs-toggle="dropdown">
                <img src="{{ session.get('avatar', '/static/default-avatar.png') }}"
                     class="rounded-circle me-2" width="36" height="36">
                <strong>{{ session['username'] }}</strong>
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="/profile">Profile</a></li>
                <li><a class="dropdown-item text-danger" href="/logout">Logout</a></li>
            </ul>
        </div>

        <nav>
            <a href="/todo"><i class="fa-solid fa-inbox"></i> Inbox</a>
            <a href="/today"><i class="fa-regular fa-calendar-days"></i> Today</a>
            <a href="/upcoming"><i class="fa-solid fa-calendar-week"></i> Upcoming</a>
            <a href="/done_tasks"><i class="fa-solid fa-circle-check"></i> Done</a>
        </nav>
    </aside>
    {% endif %}

    <main class="main-content">
        {{ content|safe }}
    </main>
</div>


</div>
</div>
<script>
$(function(){
    $("#task-list").sortable({
        update: function(event, ui){
            let order = $(this).sortable('toArray', {attribute:'data-id'});
            $.post("/reorder", {order: order.join(',')});
        }
    });
});
</script>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
function openEditModal(taskId, taskName, priority, dueDate){
    $('#editTaskId').val(taskId);
    $('#editTaskName').val(taskName);
    $('#editPriority').val(priority);
    $('#editDueDate').val(dueDate);
    var modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();
}

$('#editForm').submit(function(e){
    e.preventDefault();
    var taskId = $('#editTaskId').val();
    var data = $(this).serialize();
    $.post('/edit_ajax/' + taskId, data, function(){
        location.reload(); // reload task list
    });
});
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
"""

def priority_color(p):
    return {1:'#a0a0a0', 2:'#f0ad4e', 3:'#e44232'}.get(p,'#a0a0a0')

@app.route('/')
def landing():
    if 'uid' in session:
        return redirect('/todo')
    return redirect('/home')

@app.route('/home')
def home():
    if 'uid' in session:
        return redirect('/todo')
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (u, p)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session['uid'] = user[0]
            session['username'] = user[1]
            session['avatar'] = user[3] if user[3] else '/static/default-avatar.png'
            return redirect('/todo')
        else:
            error = "Username atau password salah"

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    success = None

    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (u,))
        if cur.fetchone():
            error = "Username sudah digunakan"
        else:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s,%s)",
                (u, p)
            )
            mysql.connection.commit()
            success = "Registrasi berhasil"
        cur.close()

    return render_template(
        'register.html',
        error=error,
        success=success
    )


@app.route('/todo', methods=['GET','POST'])
def todo():
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()  # 🔥 INI YANG KURANG

    if request.method == 'POST':
        task = request.form['task']
        priority = request.form['priority']
        due = request.form.get('due_date')
        time = request.form.get('due_time')

        cur.execute(
            "INSERT INTO tasks (task, priority, user_id, due_date, due_time) VALUES (%s,%s,%s,%s,%s)",
            (task, priority, session['uid'], due, time)
        )
        mysql.connection.commit()
        return redirect('/todo')

    cur.execute(
        "SELECT id, task, priority, is_done, due_date FROM tasks WHERE user_id=%s ORDER BY position ASC",
        (session['uid'],)
    )
    tasks = cur.fetchall()

    content = f"""
    <h4 class="mb-3">Inbox</h4>
    <form method="post" class="d-flex mb-4">
        <input class="form-control me-2" name="task" placeholder="Add task" required>
        <select name="priority" class="form-select me-2" style="width:130px">
            <option value="1">Low</option>
            <option value="2">Medium</option>
            <option value="3">High</option>
        </select>
        <input type="date" class="form-control me-2" name="due_date">
        <input type="time" class="form-control me-2" name="due_time">
        <button class="btn btn-primary">Add</button>
    </form>
    <div id="task-list">
        {''.join([
        f"""
        <div class="task-item" data-id="{t[0]}" style="border-left:5px solid {priority_color(t[2])}">
            <div class="task-left">
                <form action="/toggle/{t[0]}" method="post">
                    <input type="checkbox" class="checkbox" onChange="this.form.submit()" {'checked' if t[3] else ''}>
                </form>
                <span style="{'text-decoration:line-through;color:#999;' if t[3] else 'color:#222;'}">{t[1]}</span>
            </div>
            <div>
                <span class="edit-btn"
                    onclick="openEditModal({t[0]}, '{t[1].replace("'", "\\'")}', {t[2]}, '{t[4] or ''}')">✏</span>
                <a href="/delete/{t[0]}" class="delete-btn text-danger">🗑</a>
            </div>
        </div>
        """ for t in tasks
        ])}
    </div>
    """
    return render_template_string(BASE_HTML, title='To-Do', content=content)


@app.route('/reorder', methods=['POST'])
def reorder():
    if 'uid' not in session: return '',403
    order = request.form['order'].split(',')
    cur = mysql.connection.cursor()
    for idx, task_id in enumerate(order):
        cur.execute("UPDATE tasks SET position=%s WHERE id=%s AND user_id=%s", (idx, task_id, session['uid']))
    mysql.connection.commit()
    return '',204

@app.route('/delete/<int:task_id>')
def delete(task_id):
    if 'uid' not in session: return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, session['uid']))
    mysql.connection.commit()
    return redirect('/todo')

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    if 'uid' not in session: return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET is_done = NOT is_done WHERE id=%s AND user_id=%s", (task_id, session['uid']))
    mysql.connection.commit()
    return redirect('/todo')

@app.route('/today')
def today():
    if 'uid' not in session: return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, task, priority, is_done, due_date FROM tasks WHERE user_id=%s AND due_date = CURDATE() ORDER BY position ASC", (session['uid'],))
    tasks = cur.fetchall()
    content = f"<h4 class='mb-3'>Today</h4>"
    content += ''.join([f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}">
            <div class="task-left">
                <form action="/toggle/{t[0]}" method="post">
                    <input type="checkbox" class="checkbox" onChange="this.form.submit()" {'checked' if t[3] else ''}>
                </form>
                <span style="{'text-decoration:line-through;color:#999;' if t[3] else 'color:#222;'}">{t[1]}</span>
            </div>
            <a href="/delete/{t[0]}" class="delete-btn text-danger">🗑</a>
        </div>
    """ for t in tasks])
    return render_template_string(BASE_HTML, title="Today", content=content)

@app.route('/done_tasks')
def done_tasks():
    if 'uid' not in session: return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, task, priority, is_done, due_date FROM tasks WHERE user_id=%s AND is_done=1 ORDER BY position ASC", (session['uid'],))
    tasks = cur.fetchall()
    content = f"<h4 class='mb-3'>Done</h4>"
    content += ''.join([f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}">
            <span style="text-decoration:line-through;color:#999;">{t[1]}</span>
        </div>
    """ for t in tasks])
    return render_template_string(BASE_HTML, title="Done", content=content)

@app.route('/edit/<int:task_id>', methods=['GET','POST'])
def edit(task_id):
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        task_name = request.form['task']
        priority = request.form['priority']
        due_date = request.form.get('due_date')
        due_time = request.form.get('due_time')

        cur.execute(
            "UPDATE tasks SET task=%s, priority=%s, due_date=%s, due_time=%s WHERE id=%s AND user_id=%s",
            (task_name, priority, due_date, due_time, task_id, session['uid'])
        )
        mysql.connection.commit()
        return redirect('/todo')

    cur.execute(
        "SELECT task, priority, due_date, due_time FROM tasks WHERE id=%s AND user_id=%s",
        (task_id, session['uid'])
    )
    task = cur.fetchone()
    if not task:
        return redirect('/todo')

    content = f"""
    <h4 class="mb-3">Edit Task</h4>
    <form method="post">
        <input class="form-control mb-2" name="task" value="{task[0]}" required>

        <select name="priority" class="form-select mb-2">
            <option value="1" {"selected" if task[1]==1 else ""}>Low</option>
            <option value="2" {"selected" if task[1]==2 else ""}>Medium</option>
            <option value="3" {"selected" if task[1]==3 else ""}>High</option>
        </select>

        <input type="date" class="form-control mb-2" name="due_date" value="{task[2] or ''}">
        <input type="time" class="form-control mb-2" name="due_time" value="{task[3] or ''}">

        <button class="btn btn-primary w-100">Update</button>
    </form>
    <div class="mt-3"><a href='/todo'>Back</a></div>
    """
    return render_template_string(BASE_HTML, title="Edit Task", content=content)

@app.route('/edit_ajax/<int:task_id>', methods=['POST'])
def edit_ajax(task_id):
    if 'uid' not in session:
        return '', 403

    task_name = request.form['task']
    priority = request.form['priority']
    due_date = request.form.get('due_date')

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE tasks SET task=%s, priority=%s, due_date=%s WHERE id=%s AND user_id=%s",
        (task_name, priority, due_date, task_id, session['uid'])
    )
    mysql.connection.commit()
    return '', 204



import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'uid' not in session:
        return redirect('/')
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user{session['uid']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar_path = f"/{UPLOAD_FOLDER}/{filename}"
                cur.execute("UPDATE users SET avatar=%s WHERE id=%s", (avatar_path, session['uid']))
                mysql.connection.commit()
                session['avatar'] = avatar_path
    # Ambil data user
    cur.execute("SELECT username, avatar FROM users WHERE id=%s", (session['uid'],))
    user = cur.fetchone()
    content = f"""
    <h4 class="mb-3">Profile</h4>
    <div class="mb-3">
        <img src="{user[1]}" alt="avatar" width="100" height="100" class="rounded-circle mb-2">
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="avatar" class="form-control mb-2">
            <button class="btn btn-primary">Upload Avatar</button>
        </form>
    </div>
    <div><a href='/todo'>Back</a></div>
    """
    return render_template_string(BASE_HTML, title="Profile", content=content)


@app.route('/upcoming')
def upcoming():
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, task, priority, is_done, due_date, due_time
        FROM tasks
        WHERE user_id=%s AND due_date IS NOT NULL AND is_done=0
        ORDER BY due_date ASC, position ASC
    """, (session['uid'],))
    tasks = cur.fetchall()

    from collections import defaultdict
    from datetime import date, timedelta

    tasks_by_date = defaultdict(list)
    for t in tasks:
        if t[4] is not None:
            tasks_by_date[t[4]].append(t)

    today = date.today()
    content = "<h4 class='mb-3'>Upcoming</h4>"

    for d in sorted(tasks_by_date.keys()):
        d_obj = d

        if d_obj == today:
            label = "Today"
        elif d_obj == today + timedelta(days=1):
            label = "Tomorrow"
        else:
            label = d_obj.strftime("%A")

        # ===== DATE HEADER =====
        content += f"""
        <div class="date-group">
            <div class="date-title">
                <i class="fa-regular fa-calendar"></i>
                {d_obj.strftime('%d %b')} · {label}
            </div>
        """

        # ===== TASK LOOP =====
        for t in tasks_by_date[d]:
            time_label = ""

            if t[5]:  # due_time = timedelta
                total = int(t[5].total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                time_label = f"{h:02d}:{m:02d}"

            content += f"""
            <div class="task-row" style="border-left:5px solid {priority_color(t[2])}">
                <div class="left">
                    <form action="/toggle/{t[0]}" method="post">
                        <input type="checkbox" class="checkbox" onchange="this.form.submit()">
                    </form>
                    <span class="task-name">{t[1]}</span>
                </div>

                <div class="right">
                    {f'<i class="fa-regular fa-clock"></i> {time_label}' if time_label else ''}
                </div>
            </div>
            """

        content += "</div>"

    return render_template_string(BASE_HTML, title="Upcoming", content=content)



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
