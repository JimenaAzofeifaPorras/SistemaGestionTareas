# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexiones desde el frontend

class GestorTareas:
    def __init__(self, archivo_datos='tareas.json'):
        self.archivo_datos = archivo_datos
        self.tareas = self.cargar_tareas()
    
    def cargar_tareas(self):
        """Carga las tareas desde el archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as archivo:
                    return json.load(archivo)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def guardar_tareas(self):
        """Guarda las tareas en el archivo JSON"""
        with open(self.archivo_datos, 'w', encoding='utf-8') as archivo:
            json.dump(self.tareas, archivo, indent=2, ensure_ascii=False)
    
    def agregar_tarea(self, descripcion, prioridad='media'):
        """Agrega una nueva tarea"""
        # Encontrar el próximo ID disponible
        max_id = max([t['id'] for t in self.tareas], default=0)
        tarea = {
            'id': max_id + 1,
            'descripcion': descripcion,
            'completada': False,
            'prioridad': prioridad,
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.tareas.append(tarea)
        self.guardar_tareas()
        return tarea
    
    def obtener_tareas(self, solo_pendientes=False):
        """Obtiene todas las tareas o solo las pendientes"""
        if solo_pendientes:
            return [t for t in self.tareas if not t['completada']]
        return self.tareas
    
    def completar_tarea(self, id_tarea):
        """Marca una tarea como completada"""
        for tarea in self.tareas:
            if tarea['id'] == id_tarea:
                if not tarea['completada']:
                    tarea['completada'] = True
                    tarea['fecha_completacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.guardar_tareas()
                return tarea
        return None
    
    def eliminar_tarea(self, id_tarea):
        """Elimina una tarea"""
        for i, tarea in enumerate(self.tareas):
            if tarea['id'] == id_tarea:
                tarea_eliminada = self.tareas.pop(i)
                self.guardar_tareas()
                return tarea_eliminada
        return None
    
    def buscar_tareas(self, termino):
        """Busca tareas por descripción"""
        return [t for t in self.tareas if termino.lower() in t['descripcion'].lower()]
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de las tareas"""
        total = len(self.tareas)
        completadas = len([t for t in self.tareas if t['completada']])
        pendientes = total - completadas
        
        prioridades = {'alta': 0, 'media': 0, 'baja': 0}
        for tarea in self.tareas:
            if not tarea['completada']:
                prioridades[tarea['prioridad']] += 1
        
        return {
            'total': total,
            'completadas': completadas,
            'pendientes': pendientes,
            'prioridades': prioridades
        }

# Instancia global del gestor
gestor = GestorTareas()

# Rutas de la API
@app.route('/')
def index():
    """Sirve el frontend"""
    return render_template('index.html')

@app.route('/api/tareas', methods=['GET'])
def obtener_tareas():
    """Obtiene todas las tareas"""
    solo_pendientes = request.args.get('pendientes') == 'true'
    tareas = gestor.obtener_tareas(solo_pendientes)
    return jsonify(tareas)

@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    """Crea una nueva tarea"""
    data = request.get_json()
    if not data or 'descripcion' not in data:
        return jsonify({'error': 'Descripción requerida'}), 400
    
    descripcion = data['descripcion'].strip()
    prioridad = data.get('prioridad', 'media')
    
    if not descripcion:
        return jsonify({'error': 'La descripción no puede estar vacía'}), 400
    
    if prioridad not in ['alta', 'media', 'baja']:
        prioridad = 'media'
    
    tarea = gestor.agregar_tarea(descripcion, prioridad)
    return jsonify(tarea), 201

@app.route('/api/tareas/<int:id_tarea>', methods=['PUT'])
def completar_tarea(id_tarea):
    """Completa una tarea"""
    tarea = gestor.completar_tarea(id_tarea)
    if tarea:
        return jsonify(tarea)
    return jsonify({'error': 'Tarea no encontrada'}), 404

@app.route('/api/tareas/<int:id_tarea>', methods=['DELETE'])
def eliminar_tarea(id_tarea):
    """Elimina una tarea"""
    tarea = gestor.eliminar_tarea(id_tarea)
    if tarea:
        return jsonify({'mensaje': 'Tarea eliminada correctamente'})
    return jsonify({'error': 'Tarea no encontrada'}), 404

@app.route('/api/buscar')
def buscar_tareas():
    """Busca tareas"""
    termino = request.args.get('q', '').strip()
    if not termino:
        return jsonify({'error': 'Término de búsqueda requerido'}), 400
    
    resultados = gestor.buscar_tareas(termino)
    return jsonify(resultados)

@app.route('/api/estadisticas')
def obtener_estadisticas():
    """Obtiene estadísticas de las tareas"""
    stats = gestor.obtener_estadisticas()
    return jsonify(stats)

if __name__ == '__main__':
    # Crear directorio templates si no existe
    if not os.path.exists('templates'):
        os.makedirs('templates')

    app.run(debug=True, host='0.0.0.0', port=5000)