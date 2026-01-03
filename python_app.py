from turtle import color
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

def get_projects():
    if 'uid' not in session:
        return []
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, name FROM projects WHERE user_id=%s ORDER BY id ASC",
        (session['uid'],)
    )
    return cur.fetchall()
def render_page(title, content):
    return render_template_string(
        BASE_HTML,
        title=title,
        content=content,
        projects=get_projects()
    )
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def priority_color(p):
    mapping = {'low':'#28a745', 'medium':'#ffc107', 'high':'#dc3545'}
    return mapping.get(str(p).lower(), '#a0a0a0')


def render_task_full(t):
    """
    t = (id, task, priority, is_done, due_date, due_time)
    """
    task_id, task_name, priority, is_done, due_date, due_time = t
    date_label = due_date.strftime('%d %b %Y') if due_date else ''
    time_label = str(due_time)[:5] if due_time else ''
    
    border_color = priority_color(priority)

    return f"""
    <div class="task-item {'completed' if is_done else ''}" style="border-left:5px solid {border_color}">
        <div class="task-left">
            <form action="/toggle/{task_id}" method="post">
                <input type="checkbox" class="checkbox" onchange="this.form.submit()" {'checked' if is_done else ''}>
            </form>
            <span style="{'text-decoration:line-through;color:#999;' if is_done else 'color:#000;'}">
                {task_name}
            </span>
        </div>

        <div class="task-right">
            <small>{date_label} {time_label}</small>
            
            <span class="edit-btn"
                onclick="openEditModal({task_id}, '{task_name.replace("'", "\\'")}', '{priority}', '{due_date or ''}')">
                ✏
            </span>

            <a href="/delete/{task_id}" class="delete-btn text-danger">🗑</a>
        </div>
    </div>
    """






BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>


<script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
<script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<link rel="stylesheet" href="https://code.jquery.com/ui/1.13.2/themes/base/jquery-ui.css">

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">


<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">


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
.overdue-group .date-title {
    color: #e03131;
}

.overdue-task {
    background: #fff5f5;
}

.text-danger {
    color: #e03131;
}
.task-item.completed {
    background: #f8f9fa;
    opacity: 0.85;
}
.project-item button {
    background: none;
    border: none;
    opacity: 0.5;
}

.project-item:hover button {
    opacity: 1;
}
.profile-container img {
            object-fit: cover;
        }
        .profile-container .btn-sm i {
            font-size: 0.85rem;
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
                <option value="low">Low</option>
<option value="medium">Medium</option>
<option value="high">High</option>

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
 <a href="#" data-bs-toggle="modal" data-bs-target="#addTaskModal"
   class="sidebar-item add-task-btn" style="font-weight:bold; color:#dc3545;">
   <i class="fas fa-plus"></i> Add Task
</a>


    <a href="/todo"><i class="fa-solid fa-inbox"></i> Inbox</a>
    <a href="/today"><i class="fa-regular fa-calendar"></i> Today</a>
    <a href="/upcoming"><i class="fa-solid fa-calendar-week"></i> Upcoming</a>
    <a href="/done_tasks"><i class="fa-solid fa-check"></i> Completed</a>
    <a href="/overdue"><i class="fa-solid fa-clock"></i> Overdue</a>
  




    <hr>

    <small class="text-muted">My Projects</small>

{% for p in projects %}
<div class="d-flex align-items-center justify-content-between project-item">
    <a href="/project/{{ p[0] }}" class="flex-grow-1 text-decoration-none">
        <i class="fa-solid fa-hashtag me-2"></i>{{ p[1] }}
    </a>

    <form method="post"
          action="/delete_project/{{ p[0] }}"
          onsubmit="return confirm('Hapus project ini beserta semua task?')">
        <button class="btn btn-sm text-danger p-0 ms-2">🗑</button>
    </form>
</div>
{% endfor %}



    <a href="#" data-bs-toggle="modal" data-bs-target="#addProjectModal"
       class="text-muted">
        <i class="fa-solid fa-plus"></i> Add project
    </a>
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

<div class="modal fade" id="addProjectModal">
  <div class="modal-dialog">
    <form class="modal-content" method="post" action="/add_project">
      <div class="modal-header">
        <h5>Add Project</h5>
        <button class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <input name="name" class="form-control"
               placeholder="Project name" required>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary w-100">Create</button>
      </div>
    </form>
  </div>
</div>
<div class="modal fade" id="addTaskModal" tabindex="-1">
  <div class="modal-dialog">
    <form method="post" action="/add_task" class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Add Task</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body">
        <input name="task" class="form-control mb-2" placeholder="Task name" required>

        <select name="project_id" class="form-control mb-2">
          <option value="">Inbox</option>
          {% for p in projects %}
          <option value="{{ p[0] }}">{{ p[1] }}</option>
          {% endfor %}
        </select>

        <input type="date" name="due_date" class="form-control mb-2">
        <input type="time" name="due_time" class="form-control mb-2">

        <select name="priority" class="form-control mb-2">
    <option value="low">Low</option>
    <option value="medium" selected>Medium</option>
    <option value="high">High</option>
</select>

      </div>

      <div class="modal-footer">
        <button class="btn btn-primary">Add</button>
      </div>
    </form>
  </div>
</div>
<script>
function openAddTask(projectId){
    // set project otomatis
    document.querySelector('#addTaskModal select[name="project_id"]').value = projectId;

    // buka modal bootstrap
    var modal = new bootstrap.Modal(
        document.getElementById('addTaskModal')
    );
    modal.show();
}
</script>

<script>
function enableEditProject(projectId, oldName){
    let span = document.getElementById('project-title');

    span.innerHTML = `
        <input id="editProjectInput"
               class="form-control d-inline w-auto"
               value="${oldName}"
               onblur="saveProjectName(${projectId})"
               onkeydown="if(event.key==='Enter') saveProjectName(${projectId})">
    `;

    document.getElementById('editProjectInput').focus();
}

function saveProjectName(projectId){
    let val = document.getElementById('editProjectInput').value;

    $.post('/rename_project/' + projectId, {name: val}, function(){
        location.reload();
    });
}
</script>
>





<!-- Lalu script custom kamu -->
<script>
$(function() {
    $("#task-list").sortable({
        update: function(event, ui) {
            // kode update urutan task
        }
    });
});
</script>


<script>
function updatePriorityColor(sel){
    if(!sel) return;
    const val = sel.value.toLowerCase();
    if(val === 'low') sel.style.color = 'green';
    else if(val === 'medium') sel.style.color = 'orange';
    else if(val === 'high') sel.style.color = 'red';
}

// Terapkan ke semua select priority
document.querySelectorAll('select[name="priority"]').forEach(sel => {
    updatePriorityColor(sel); // warna default
    sel.addEventListener('change', function(){ updatePriorityColor(this); });
});
</script>


</body>
</html>
"""




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
            session.clear()
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
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'uid' not in session:
        return redirect('/')

    task = request.form['task']
    priority = request.form['priority']
    project_id = request.form.get('project_id') or None
    due_date = request.form.get('due_date') or None
    due_time = request.form.get('due_time') or None

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO tasks (task, priority, user_id, project_id, is_done, due_date, due_time)
        VALUES (%s,%s,%s,%s,0,%s,%s)
    """, (task, priority, session['uid'], project_id, due_date, due_time))

    mysql.connection.commit()

    return redirect(request.referrer or '/todo')



@app.route('/todo')
def todo():
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    
    cur.execute(
        "SELECT id, name FROM projects WHERE user_id=%s ORDER BY id ASC",
        (session['uid'],)
    )
    projects = cur.fetchall()

    
    cur.execute("""
        SELECT id, task, priority, is_done, due_date, due_time
        FROM tasks
        WHERE user_id=%s AND project_id IS NULL
        ORDER BY is_done, due_date IS NULL, due_date, due_time
    """, (session['uid'],))
    inbox_tasks = cur.fetchall()

    
    def render_task(t):
        date_label = t[4].strftime('%d %b %Y') if t[4] else ''
        time_label = str(t[5])[:5] if t[5] else ''

        return f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}; padding:5px 10px; margin-bottom:5px;">

            <div class="task-left" style="display:flex; align-items:center; gap:8px;">
                <form action="/toggle/{t[0]}" method="post">
                    <input type="checkbox" class="checkbox"
                        onchange="this.form.submit()" {'checked' if t[3] else ''}>
                </form>
                <span style="{'text-decoration:line-through;color:#999;' if t[3] else 'color:#000;'}">
                    {t[1]}
                </span>
            </div>
            <div class="task-right" style="margin-left:auto;">
                <small style="color:#000;">{date_label} {time_label}</small>
            </div>
        </div>
        """

   
    inbox_html = "".join(render_task_full(t) for t in inbox_tasks)


    content = f"""
    <h4 class="mb-3 d-flex justify-content-between align-items-center">
        Inbox
        <button class="btn btn-sm btn-primary"
            data-bs-toggle="modal" data-bs-target="#addTaskModal">
            + Add Task
        </button>
    </h4>
    {inbox_html}
    <hr>
    """

    
    for p in projects:
        cur.execute("""
            SELECT id, task, priority, is_done, due_date, due_time
            FROM tasks
            WHERE project_id=%s AND user_id=%s
            ORDER BY is_done, due_date IS NULL, due_date
        """, (p[0], session['uid']))
        project_tasks = cur.fetchall()

        task_html = "".join(render_task(t) for t in project_tasks)

        content += f"""
        <div class="mb-4">
            <h5 class="fw-bold text-dark" ondblclick="renameProject({p[0]}, '{p[1]}')">
                # {p[1]}
            </h5>
            {task_html if task_html else '<p class="ms-3 text-muted">No task</p>'}
        </div>
        """

    return render_template_string(
        BASE_HTML,
        title="Todo",
        content=content,
        projects=get_projects()
    )


@app.route('/add_project', methods=['POST'])
def add_project():
    if 'uid' not in session:
        return redirect('/')

    name = request.form['name']
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO projects (name, user_id) VALUES (%s,%s)",
        (name, session['uid'])
    )
    mysql.connection.commit()
    return redirect('/todo')
@app.route('/project/<int:project_id>')
def project_detail(project_id):
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    # Ambil nama project
    cur.execute(
        "SELECT name FROM projects WHERE id=%s AND user_id=%s",
        (project_id, session['uid'])
    )
    project = cur.fetchone()
    if not project:
        return redirect('/todo')

    # Ambil task project
    cur.execute("""
        SELECT id, task, priority, is_done, due_date, due_time
        FROM tasks
        WHERE user_id=%s AND project_id=%s
        ORDER BY is_done, due_date IS NULL, due_date, due_time
    """, (session['uid'], project_id))
    tasks = cur.fetchall()

    task_html = ""
    for t in tasks:
        date_label = t[4].strftime('%d %b %Y') if t[4] else ''
        time_label = str(t[5])[:5] if t[5] else ''

        task_html += f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}; padding:5px 10px; margin-bottom:5px;">

            <div class="task-left">
                <form action="/toggle/{t[0]}" method="post">
                    <input type="checkbox" class="checkbox"
                        onChange="this.form.submit()" {'checked' if t[3] else ''}>
                </form>

                <span style="{'text-decoration:line-through;color:#999;' if t[3] else ''}">
                    {t[1]}
                </span>
            </div>

            <div class="task-right">
                <small class="text-muted">{date_label} {time_label}</small>

                <span class="edit-btn"
                    onclick="openEditModal({t[0]}, '{t[1].replace("'", "\\'")}', {t[2]}, '{t[4] or ''}')">
                    ✏
                </span>

                <a href="/delete/{t[0]}" class="delete-btn text-danger">🗑</a>
            </div>
        </div>
        """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">{project[0]}</h4>
    <button class="btn btn-sm btn-primary"
            onclick="openAddTask({project_id})">
        + Add Task
    </button>
</div>



   

    <div id="task-list">
        {task_html if task_html else '<p class="text-muted">No tasks</p>'}
    </div>
    """

    return render_template_string(
    BASE_HTML,
    title=project[0],
    content=content,
    projects=get_projects()
)


@app.route('/rename_project/<int:project_id>', methods=['POST'])
def rename_project(project_id):
    if 'uid' not in session:
        return '', 403

    name = request.form['name']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE projects
        SET name=%s
        WHERE id=%s AND user_id=%s
    """, (name, project_id, session['uid']))
    mysql.connection.commit()

    return '', 204

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    # 1. hapus semua task di project ini
    cur.execute(
        "DELETE FROM tasks WHERE project_id=%s AND user_id=%s",
        (project_id, session['uid'])
    )

    # 2. hapus project
    cur.execute(
        "DELETE FROM projects WHERE id=%s AND user_id=%s",
        (project_id, session['uid'])
    )

    mysql.connection.commit()

    return redirect('/todo')



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
def delete_task(task_id):
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM tasks WHERE id=%s AND user_id=%s",
        (task_id, session['uid'])
    )
    mysql.connection.commit()

    return redirect(request.referrer or '/todo')


@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tasks
        SET is_done = NOT is_done
        WHERE id=%s AND user_id=%s
    """, (task_id, session['uid']))
    mysql.connection.commit()
    return redirect(request.referrer or '/todo')




@app.route('/today')
def today():
    if 'uid' not in session: return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, task, priority, is_done, due_date FROM tasks WHERE user_id=%s AND due_date = CURDATE() ORDER BY position ASC", (session['uid'],))
    tasks = cur.fetchall()
    content = f"<h4 class='mb-3'>Today</h4>"
    content += ''.join([f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}; padding:5px 10px; margin-bottom:5px;">

            <div class="task-left">
                <form action="/toggle/{t[0]}" method="post">
                    <input type="checkbox" class="checkbox" onchange="this.form.submit()" {'checked' if t[3] else ''}>
                </form>
                <span style="{'text-decoration:line-through;color:#999;' if t[3] else 'color:#222;'}">{t[1]}</span>
            </div>
            <a href="/delete/{t[0]}" class="delete-btn text-danger">🗑</a>
        </div>
    """ for t in tasks])
    return render_template_string(
        BASE_HTML,
        title="Today",
        content=content,
        projects=get_projects()
    )
@app.route('/overdue')
def overdue():
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, task, priority, is_done, due_date, due_time
        FROM tasks
        WHERE user_id=%s
        AND due_date < CURDATE()
        AND is_done = 0
        ORDER BY due_date ASC, position ASC
    """, (session['uid'],))
    tasks = cur.fetchall()

    from collections import defaultdict
    from datetime import date, timedelta

    tasks_by_date = defaultdict(list)
    for t in tasks:
        if t[4]:
            tasks_by_date[t[4]].append(t)

    today = date.today()
    content = "<h4 class='mb-3 text-danger'>Overdue</h4>"

    if not tasks_by_date:
        content += """
        <div class="empty-state">
            <i class="fa-regular fa-face-smile"></i>
            <p>Tidak ada task overdue 🎉</p>
        </div>
        """
        return render_template_string(
        BASE_HTML,
        title="Overdue",
        content=content,
        projects=get_projects()
    )

    for d in sorted(tasks_by_date.keys()):
        d_obj = d
        diff = (today - d_obj).days

        if diff == 1:
            label = "Yesterday"
        else:
            label = f"{diff} days overdue"

        content += f"""
        <div class="date-group overdue-group">
            <div class="date-title text-danger">
                <i class="fa-solid fa-triangle-exclamation"></i>
                {d_obj.strftime('%d %b')} · {label}
            </div>
        """

        for t in tasks_by_date[d]:
            time_label = ""

            if t[5]:
                total = int(t[5].total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                time_label = f"{h:02d}:{m:02d}"

            content += f"""
            <div class="task-row overdue-task" style="border-left:5px solid #e03131">
                <div class="left">
                    <form action="/toggle/{t[0]}" method="post">
                        <input type="checkbox" class="checkbox" onchange="this.form.submit()">
                    </form>
                    <span class="task-name">{t[1]}</span>
                </div>

                <div class="right text-danger">
                    {f'<i class="fa-regular fa-clock"></i> {time_label}' if time_label else ''}
                </div>
            </div>
            """

        content += "</div>"

    return render_template_string(
        BASE_HTML,
        title="Overdue",
        content=content,
        projects=get_projects()
    )





@app.route('/done_tasks')
def done_tasks():
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, task, priority, due_date, due_time
        FROM tasks
        WHERE user_id=%s AND is_done=1
        ORDER BY id DESC
    """, (session['uid'],))
    tasks = cur.fetchall()

    task_html = ""
    for t in tasks:
        date_label = t[3].strftime('%d %b %Y') if t[3] else ''
        time_label = str(t[4])[:5] if t[4] else ''

        task_html += f"""
        <div class="task-item" style="border-left:5px solid {priority_color(t[2])}; padding:5px 10px; margin-bottom:5px;">

            <div class="task-left">
                <form action="/restore/{t[0]}" method="post">
                    <input type="checkbox"
                           class="checkbox"
                           onchange="this.form.submit()">
                </form>

                <span style="text-decoration:line-through;color:#999;">
                    {t[1]}
                </span>
            </div>

            <div class="task-right">
                <small class="text-muted">{date_label} {time_label}</small>
                <a href="/delete/{t[0]}" class="delete-btn text-danger">🗑</a>
            </div>
        </div>
        """

    content = f"""
    <h4 class="mb-3">Completed</h4>
    <div id="task-list">
        {task_html if task_html else '<p class="text-muted">No completed tasks</p>'}
    </div>
    """

    return render_template_string(
    BASE_HTML,
    title="Completed",
    content=content,
    projects=get_projects()
)


@app.route('/restore/<int:task_id>', methods=['POST'])
def restore_task(task_id):
    if 'uid' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tasks
        SET is_done = 0
        WHERE id = %s AND user_id = %s
    """, (task_id, session['uid']))

    mysql.connection.commit()
    return redirect('/done_tasks')




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
            <option value="low">Low</option>
<option value="medium">Medium</option>
<option value="high">High</option>

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

    # Handle POST
    if request.method == 'POST':
        # 1️⃣ Update avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user{session['uid']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar_path = f"/{UPLOAD_FOLDER}/{filename}"
                cur.execute("UPDATE users SET avatar=%s WHERE id=%s", (avatar_path, session['uid']))
                mysql.connection.commit()
                session['avatar'] = avatar_path
                session['avatar_version'] = session.get('avatar_version', 0) + 1

        # 2️⃣ Update username
        new_username = request.form.get('username')
        if new_username:
            cur.execute("UPDATE users SET username=%s WHERE id=%s", (new_username, session['uid']))
            mysql.connection.commit()
            session['username'] = new_username

        return redirect('/profile')  # reload page agar update terlihat

    # Ambil data user
    cur.execute("SELECT username, avatar FROM users WHERE id=%s", (session['uid'],))
    user = cur.fetchone()

    content = f"""
    <h4 class="mb-3">Profile</h4>
    <div class="profile-container mb-3 d-flex flex-column align-items-center text-center">
    <img src="{user[1]}?v={session.get('avatar_version',0)}" 
         alt="avatar" width="120" height="120" class="rounded-circle mb-3">

    <form method="post" enctype="multipart/form-data" class="w-50">
        <label>Username</label>
        <input type="text" name="username" class="form-control mb-2" value="{user[0]}" required>
        <label>Avatar</label>
        <input type="file" name="avatar" class="form-control mb-3">
        <button class="btn btn-primary w-100">Update Profile</button>
    </form>
</div>

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

        content += f"""
        <div class="date-group">
            <div class="date-title">
                <i class="fa-regular fa-calendar"></i>
                {d_obj.strftime('%d %b')} · {label}
            </div>
        """

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

    return render_template_string(
        BASE_HTML,
        title="Upcoming",
        content=content,
        projects=get_projects()
    )



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
