from flask import Flask, render_template_string, request, jsonify, session
import os
import hashlib
import secrets
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto-cambiar-en-produccion')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Requiere HTTPS en producción
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos

# Simulación de base de datos segura
users_db = {}
tasks_db = {}

def hash_password(password):
    """Hashea la contraseña usando SHA-256 con salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def verify_password(stored_password, provided_password):
    """Verifica si la contraseña proporcionada coincide con la almacenada"""
    salt = stored_password[:32]
    stored_key = stored_password[32:]
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return key == stored_key

def login_required(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(text):
    """Sanitiza el input para prevenir XSS"""
    if not text:
        return ""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas Seguro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 500px;
            padding: 40px;
        }

        h1 {
            color: #667eea;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        input[type="text"],
        input[type="password"],
        input[type="email"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(0);
        }

        .secondary-btn {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            margin-top: 10px;
        }

        .task-input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .task-input-group input {
            flex: 1;
        }

        .task-input-group button {
            width: auto;
            padding: 12px 24px;
        }

        .tasks-list {
            margin-top: 20px;
        }

        .task-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s;
        }

        .task-item:hover {
            transform: translateX(5px);
        }

        .task-item.completed {
            opacity: 0.6;
            text-decoration: line-through;
        }

        .task-text {
            flex: 1;
            color: #333;
        }

        .task-actions {
            display: flex;
            gap: 10px;
        }

        .task-actions button {
            width: auto;
            padding: 8px 16px;
            font-size: 14px;
        }

        .delete-btn {
            background: #e74c3c;
        }

        .complete-btn {
            background: #27ae60;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .user-info {
            color: #667eea;
            font-weight: 600;
        }

        .logout-btn {
            width: auto;
            padding: 8px 20px;
            font-size: 14px;
            background: #e74c3c;
        }

        .hidden {
            display: none;
        }

        .error {
            color: #e74c3c;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
        }

        .success {
            color: #27ae60;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
        }

        .empty-state {
            text-align: center;
            color: #999;
            padding: 40px 20px;
            font-style: italic;
        }

        .security-notice {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Pantalla de Login -->
        <div id="loginScreen">
            <h1>🔐 Iniciar Sesión</h1>
            <div class="security-notice">
                ✅ Sesiones seguras con timeout automático
            </div>
            <div class="form-group">
                <label for="loginEmail">Email</label>
                <input type="email" id="loginEmail" placeholder="tu@email.com">
            </div>
            <div class="form-group">
                <label for="loginPassword">Contraseña</label>
                <input type="password" id="loginPassword" placeholder="••••••••">
            </div>
            <button onclick="login()">Iniciar Sesión</button>
            <button class="secondary-btn" onclick="showRegister()">Crear Cuenta</button>
            <div id="loginError" class="error"></div>
        </div>

        <!-- Pantalla de Registro -->
        <div id="registerScreen" class="hidden">
            <h1>📝 Crear Cuenta</h1>
            <div class="security-notice">
                🔒 Contraseñas almacenadas de forma segura
            </div>
            <div class="form-group">
                <label for="registerName">Nombre</label>
                <input type="text" id="registerName" placeholder="Tu nombre">
            </div>
            <div class="form-group">
                <label for="registerEmail">Email</label>
                <input type="email" id="registerEmail" placeholder="tu@email.com">
            </div>
            <div class="form-group">
                <label for="registerPassword">Contraseña</label>
                <input type="password" id="registerPassword" placeholder="Mínimo 8 caracteres">
            </div>
            <button onclick="register()">Registrarse</button>
            <button class="secondary-btn" onclick="showLogin()">Ya tengo cuenta</button>
            <div id="registerError" class="error"></div>
            <div id="registerSuccess" class="success"></div>
        </div>

        <!-- Pantalla de Tareas -->
        <div id="tasksScreen" class="hidden">
            <div class="header">
                <div>
                    <h1>✅ Mis Tareas</h1>
                    <div class="user-info" id="userInfo"></div>
                </div>
                <button class="logout-btn" onclick="logout()">Salir</button>
            </div>

            <div class="security-notice">
                ⚡ Conexión segura - Datos protegidos
            </div>

            <div class="task-input-group">
                <input type="text" id="taskInput" placeholder="Nueva tarea..." onkeypress="if(event.key==='Enter') addTask()">
                <button onclick="addTask()">Agregar</button>
            </div>

            <div class="tasks-list" id="tasksList"></div>
        </div>
    </div>

    <script>
        let currentUser = null;

        function showLogin() {
            document.getElementById('loginScreen').classList.remove('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('tasksScreen').classList.add('hidden');
            clearErrors();
        }

        function showRegister() {
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.remove('hidden');
            document.getElementById('tasksScreen').classList.add('hidden');
            clearErrors();
        }

        function showTasks() {
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('tasksScreen').classList.remove('hidden');
            renderTasks();
        }

        function clearErrors() {
            document.getElementById('loginError').textContent = '';
            document.getElementById('registerError').textContent = '';
            document.getElementById('registerSuccess').textContent = '';
        }

        async function register() {
            const name = document.getElementById('registerName').value.trim();
            const email = document.getElementById('registerEmail').value.trim().toLowerCase();
            const password = document.getElementById('registerPassword').value;

            if (!name || !email || !password) {
                document.getElementById('registerError').textContent = 'Todos los campos son obligatorios';
                return;
            }

            if (password.length < 8) {
                document.getElementById('registerError').textContent = 'La contraseña debe tener al menos 8 caracteres';
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    document.getElementById('registerSuccess').textContent = '¡Cuenta creada! Redirigiendo...';
                    document.getElementById('registerError').textContent = '';
                    
                    setTimeout(() => {
                        document.getElementById('registerName').value = '';
                        document.getElementById('registerEmail').value = '';
                        document.getElementById('registerPassword').value = '';
                        showLogin();
                    }, 1500);
                } else {
                    document.getElementById('registerError').textContent = data.error || 'Error en el registro';
                }
            } catch (error) {
                document.getElementById('registerError').textContent = 'Error de conexión';
            }
        }

        async function login() {
            const email = document.getElementById('loginEmail').value.trim().toLowerCase();
            const password = document.getElementById('loginPassword').value;

            if (!email || !password) {
                document.getElementById('loginError').textContent = 'Por favor completa todos los campos';
                return;
            }

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    currentUser = data.user;
                    document.getElementById('userInfo').textContent = `Hola, ${currentUser.name}`;
                    showTasks();
                } else {
                    document.getElementById('loginError').textContent = data.error || 'Error en el login';
                }
            } catch (error) {
                document.getElementById('loginError').textContent = 'Error de conexión';
            }
        }

        async function logout() {
            try {
                await fetch('/api/logout', { method: 'POST' });
            } catch (error) {
                console.log('Error durante logout:', error);
            } finally {
                currentUser = null;
                document.getElementById('loginEmail').value = '';
                document.getElementById('loginPassword').value = '';
                showLogin();
            }
        }

        async function addTask() {
            const taskInput = document.getElementById('taskInput');
            const taskText = taskInput.value.trim();

            if (!taskText) return;

            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: taskText })
                });

                if (response.ok) {
                    taskInput.value = '';
                    renderTasks();
                }
            } catch (error) {
                console.log('Error agregando tarea:', error);
            }
        }

        async function toggleTask(id) {
            try {
                const response = await fetch(`/api/tasks/${id}/toggle`, {
                    method: 'POST'
                });

                if (response.ok) {
                    renderTasks();
                }
            } catch (error) {
                console.log('Error actualizando tarea:', error);
            }
        }

        async function deleteTask(id) {
            try {
                const response = await fetch(`/api/tasks/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    renderTasks();
                }
            } catch (error) {
                console.log('Error eliminando tarea:', error);
            }
        }

        async function renderTasks() {
            const tasksList = document.getElementById('tasksList');

            try {
                const response = await fetch('/api/tasks');
                const tasks = await response.json();

                if (!response.ok) {
                    throw new Error('Error cargando tareas');
                }

                if (tasks.length === 0) {
                    tasksList.innerHTML = '<div class="empty-state">No tienes tareas. ¡Agrega una para comenzar!</div>';
                    return;
                }

                // Usamos createElement para prevenir XSS
                tasksList.innerHTML = '';
                tasks.forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
                    
                    const taskText = document.createElement('div');
                    taskText.className = 'task-text';
                    taskText.textContent = task.text; // textContent previene XSS
                    
                    const taskActions = document.createElement('div');
                    taskActions.className = 'task-actions';
                    
                    const completeBtn = document.createElement('button');
                    completeBtn.className = 'complete-btn';
                    completeBtn.textContent = task.completed ? '↩️' : '✓';
                    completeBtn.onclick = () => toggleTask(task.id);
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.textContent = '🗑️';
                    deleteBtn.onclick = () => deleteTask(task.id);
                    
                    taskActions.appendChild(completeBtn);
                    taskActions.appendChild(deleteBtn);
                    taskElement.appendChild(taskText);
                    taskElement.appendChild(taskActions);
                    tasksList.appendChild(taskElement);
                });

            } catch (error) {
                tasksList.innerHTML = '<div class="error">Error cargando tareas</div>';
            }
        }

        // Verificar sesión al cargar la página
        async function checkSession() {
            try {
                const response = await fetch('/api/session');
                if (response.ok) {
                    const data = await response.json();
                    if (data.authenticated) {
                        currentUser = data.user;
                        document.getElementById('userInfo').textContent = `Hola, ${currentUser.name}`;
                        showTasks();
                    }
                }
            } catch (error) {
                console.log('Error verificando sesión:', error);
            }
        }

        // Inicializar
        document.addEventListener('DOMContentLoaded', checkSession);
    </script>
</body>
</html>'''

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = sanitize_input(data.get('name', ''))
        email = sanitize_input(data.get('email', '')).lower()
        password = data.get('password', '')

        if not name or not email or not password:
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400

        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

        if email in users_db:
            return jsonify({'error': 'Este email ya está registrado'}), 400

        # Hash de la contraseña
        hashed_password = hash_password(password)
        users_db[email] = {
            'name': name,
            'password': hashed_password.hex(),
            'created_at': time.time()
        }
        
        tasks_db[email] = []

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', '')).lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400

        user = users_db.get(email)
        if not user:
            return jsonify({'error': 'Credenciales inválidas'}), 401

        # Verificar contraseña
        stored_password = bytes.fromhex(user['password'])
        if not verify_password(stored_password, password):
            return jsonify({'error': 'Credenciales inválidas'}), 401

        # Crear sesión
        session.permanent = True
        session['user_email'] = email
        session['user_name'] = user['name']
        session['login_time'] = time.time()

        return jsonify({
            'message': 'Login exitoso',
            'user': {'name': user['name'], 'email': email}
        }), 200

    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout exitoso'}), 200

@app.route('/api/session')
def check_session():
    if 'user_email' in session:
        # Verificar timeout de sesión
        if time.time() - session.get('login_time', 0) > app.config['PERMANENT_SESSION_LIFETIME']:
            session.clear()
            return jsonify({'authenticated': False}), 401
            
        return jsonify({
            'authenticated': True,
            'user': {
                'name': session['user_name'],
                'email': session['user_email']
            }
        }), 200
    return jsonify({'authenticated': False}), 401

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    try:
        user_email = session['user_email']
        tasks = tasks_db.get(user_email, [])
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({'error': 'Error obteniendo tareas'}), 500

@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    try:
        data = request.get_json()
        task_text = sanitize_input(data.get('text', '')).strip()

        if not task_text:
            return jsonify({'error': 'El texto de la tarea no puede estar vacío'}), 400

        user_email = session['user_email']
        task_id = int(time.time() * 1000)  # ID único basado en timestamp

        new_task = {
            'id': task_id,
            'text': task_text,
            'completed': False,
            'created_at': time.time()
        }

        if user_email not in tasks_db:
            tasks_db[user_email] = []

        tasks_db[user_email].append(new_task)

        return jsonify(new_task), 201

    except Exception as e:
        return jsonify({'error': 'Error creando tarea'}), 500

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    try:
        user_email = session['user_email']
        tasks = tasks_db.get(user_email, [])

        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = not task['completed']
                return jsonify(task), 200

        return jsonify({'error': 'Tarea no encontrada'}), 404

    except Exception as e:
        return jsonify({'error': 'Error actualizando tarea'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    try:
        user_email = session['user_email']
        tasks = tasks_db.get(user_email, [])

        tasks_db[user_email] = [task for task in tasks if task['id'] != task_id]

        return jsonify({'message': 'Tarea eliminada'}), 200

    except Exception as e:
        return jsonify({'error': 'Error eliminando tarea'}), 500

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    # En producción, usar: export SECRET_KEY='tu-clave-super-secreta-aqui'
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)