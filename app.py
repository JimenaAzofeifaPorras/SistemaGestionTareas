from flask import Flask, render_template_string
import os

app = Flask(__name__)

# HTML de la aplicación
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas</title>
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
    </style>
</head>
<body>
    <div class="container">
        <!-- Pantalla de Login -->
        <div id="loginScreen">
            <h1>🔐 Iniciar Sesión</h1>
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
                <input type="password" id="registerPassword" placeholder="••••••••">
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

            <div class="task-input-group">
                <input type="text" id="taskInput" placeholder="Nueva tarea..." onkeypress="if(event.key==='Enter') addTask()">
                <button onclick="addTask()">Agregar</button>
            </div>

            <div class="tasks-list" id="tasksList"></div>
        </div>
    </div>

    <script>
        let users = {};
        let currentUser = null;
        let tasks = {};

        function loadData() {
            const savedUsers = localStorage.getItem('users');
            const savedTasks = localStorage.getItem('tasks');
            if (savedUsers) users = JSON.parse(savedUsers);
            if (savedTasks) tasks = JSON.parse(savedTasks);
        }

        function saveData() {
            localStorage.setItem('users', JSON.stringify(users));
            localStorage.setItem('tasks', JSON.stringify(tasks));
        }

        loadData();

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
            document.getElementById('userInfo').textContent = `Hola, ${currentUser.name}`;
            renderTasks();
        }

        function clearErrors() {
            document.getElementById('loginError').textContent = '';
            document.getElementById('registerError').textContent = '';
            document.getElementById('registerSuccess').textContent = '';
        }

        function register() {
            const name = document.getElementById('registerName').value.trim();
            const email = document.getElementById('registerEmail').value.trim().toLowerCase();
            const password = document.getElementById('registerPassword').value;

            if (!name || !email || !password) {
                document.getElementById('registerError').textContent = 'Todos los campos son obligatorios';
                return;
            }

            if (users[email]) {
                document.getElementById('registerError').textContent = 'Este email ya está registrado';
                return;
            }

            users[email] = { name, password };
            tasks[email] = [];
            saveData();

            document.getElementById('registerSuccess').textContent = '¡Cuenta creada! Redirigiendo...';
            document.getElementById('registerError').textContent = '';
            
            setTimeout(() => {
                document.getElementById('registerName').value = '';
                document.getElementById('registerEmail').value = '';
                document.getElementById('registerPassword').value = '';
                showLogin();
            }, 1500);
        }

        function login() {
            const email = document.getElementById('loginEmail').value.trim().toLowerCase();
            const password = document.getElementById('loginPassword').value;

            if (!email || !password) {
                document.getElementById('loginError').textContent = 'Por favor completa todos los campos';
                return;
            }

            if (!users[email] || users[email].password !== password) {
                document.getElementById('loginError').textContent = 'Email o contraseña incorrectos';
                return;
            }

            currentUser = { email, name: users[email].name };
            showTasks();
        }

        function logout() {
            currentUser = null;
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPassword').value = '';
            showLogin();
        }

        function addTask() {
            const taskInput = document.getElementById('taskInput');
            const taskText = taskInput.value.trim();

            if (!taskText) return;

            if (!tasks[currentUser.email]) {
                tasks[currentUser.email] = [];
            }

            tasks[currentUser.email].push({
                id: Date.now(),
                text: taskText,
                completed: false
            });

            saveData();
            taskInput.value = '';
            renderTasks();
        }

        function toggleTask(id) {
            const userTasks = tasks[currentUser.email];
            const task = userTasks.find(t => t.id === id);
            if (task) {
                task.completed = !task.completed;
                saveData();
                renderTasks();
            }
        }

        function deleteTask(id) {
            tasks[currentUser.email] = tasks[currentUser.email].filter(t => t.id !== id);
            saveData();
            renderTasks();
        }

        function renderTasks() {
            const tasksList = document.getElementById('tasksList');
            const userTasks = tasks[currentUser.email] || [];

            if (userTasks.length === 0) {
                tasksList.innerHTML = '<div class="empty-state">No tienes tareas. ¡Agrega una para comenzar!</div>';
                return;
            }

            tasksList.innerHTML = userTasks.map(task => `
                <div class="task-item ${task.completed ? 'completed' : ''}">
                    <div class="task-text">${task.text}</div>
                    <div class="task-actions">
                        <button class="complete-btn" onclick="toggleTask(${task.id})">
                            ${task.completed ? '↩️' : '✓'}
                        </button>
                        <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️</button>
                    </div>
                </div>
            `).join('');
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)