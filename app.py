from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
from datetime import datetime, date
import hashlib
 
app = Flask(__name__)
app.secret_key = 'dwr_sistemas_riego_2026_secret'
 
DATA_FILE = 'data.json'
 
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_data()
 
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
 
def get_default_data():
    return {
        "users": [
            {
                "id": 1,
                "username": "admin",
                "password": hash_password("admin123"),
                "role": "admin",
                "name": "Administrador DWR",
                "email": "admin@dwr.com",
                "created_at": "2026-01-01"
            },
            {
                "id": 2,
                "username": "gerente",
                "password": hash_password("gerente123"),
                "role": "gerente",
                "name": "Gerente DWR",
                "email": "gerente@dwr.com",
                "created_at": "2026-01-01"
            }
        ],
        "productos": [
            {"id": 1, "nombre": "Sistema de goteo", "precio": 1500000, "stock": 15, "categoria": "Riego por goteo", "descripcion": "Sistema de riego por goteo profesional para cultivos de alta densidad", "activo": True},
            {"id": 2, "nombre": "Programador de riego", "precio": 800000, "stock": 22, "categoria": "Automatización", "descripcion": "Controlador automático para programar ciclos de riego con hasta 8 zonas", "activo": True},
            {"id": 3, "nombre": "Kit de aspersores", "precio": 2000000, "stock": 8, "categoria": "Aspersión", "descripcion": "Kit completo de aspersores de alta presión para cultivos extensivos", "activo": True},
            {"id": 4, "nombre": "Filtro de malla 200 mesh", "precio": 320000, "stock": 30, "categoria": "Filtración", "descripcion": "Filtro de malla para eliminar partículas en sistemas de riego presurizado", "activo": True},
            {"id": 5, "nombre": "Válvula solenoidea 1\"", "precio": 180000, "stock": 45, "categoria": "Accesorios", "descripcion": "Válvula solenoidea para control automático de flujo de agua", "activo": True},
        ],
        "clientes": [
            {"id": 1, "nombre": "Juan Pérez", "empresa": "Finca El Paraíso", "telefono": "3001234567", "email": "juan@finca.com", "ciudad": "Montería", "activo": True, "created_at": "2026-01-15"},
            {"id": 2, "nombre": "Ana Gómez", "empresa": "Cultivos Los Andes", "telefono": "3109876543", "email": "ana@losandes.com", "ciudad": "Cereté", "activo": True, "created_at": "2026-02-10"},
            {"id": 3, "nombre": "Carlos Díaz", "empresa": "Agroindustria Córdoba", "telefono": "3207654321", "email": "carlos@agrocor.com", "ciudad": "Sahagún", "activo": True, "created_at": "2026-03-05"},
        ],
        "pedidos": [
            {"id": 1, "cliente_id": 1, "cliente_nombre": "Juan Pérez", "producto_id": 1, "producto_nombre": "Sistema de goteo", "cantidad": 2, "total": 3000000, "estado": "Pendiente", "fecha": "2026-03-12", "notas": "Instalación en zona norte"},
            {"id": 2, "cliente_id": 2, "cliente_nombre": "Ana Gómez", "producto_id": 2, "producto_nombre": "Programador de riego", "cantidad": 1, "total": 800000, "estado": "En Proceso", "fecha": "2026-03-11", "notas": ""},
            {"id": 3, "cliente_id": 3, "cliente_nombre": "Carlos Díaz", "producto_id": 3, "producto_nombre": "Kit de aspersores", "cantidad": 1, "total": 2000000, "estado": "Entregado", "fecha": "2026-03-10", "notas": "Cliente satisfecho"},
            {"id": 4, "cliente_id": 1, "cliente_nombre": "Juan Pérez", "producto_id": 4, "producto_nombre": "Filtro de malla 200 mesh", "cantidad": 3, "total": 960000, "estado": "Pendiente", "fecha": "2026-04-01", "notas": ""},
        ],
        "alertas_stock": 5,
        "next_pedido_id": 5,
        "next_producto_id": 6,
        "next_cliente_id": 4,
        "next_user_id": 3
    }
 
# Initialize data
if not os.path.exists(DATA_FILE):
    save_data(get_default_data())
 
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        data = load_data()
        user = next((u for u in data['users'] if u['username'] == username and u['password'] == hash_password(password)), None)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')
 
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
 
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    
    pedidos = data['pedidos']
    productos = data['productos']
    clientes = data['clientes']
    
    total_ventas = sum(p['total'] for p in pedidos if p['estado'] == 'Entregado')
    pedidos_activos = len([p for p in pedidos if p['estado'] in ['Pendiente', 'En Proceso']])
    productos_disponibles = sum(p['stock'] for p in productos if p['activo'])
    clientes_activos = len([c for c in clientes if c['activo']])
    
    # Ventas por día (últimos 7 días)
    ventas_semana = {}
    dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    for i, d in enumerate(dias):
        ventas_semana[d] = sum(p['total'] for p in pedidos if p['estado'] == 'Entregado' and i % 7 == hash(p['fecha']) % 7)
    
    # Simular datos de ventas semanales más realistas
    ventas_chart = [850000, 1200000, 980000, 1450000, 1100000, 760000, 1300000]
    
    pedidos_recientes = sorted(pedidos, key=lambda x: x['fecha'], reverse=True)[:5]
    stock_bajo = [p for p in productos if p['stock'] <= data.get('alertas_stock', 5) and p['activo']]
    
    return render_template('dashboard.html',
        total_ventas=total_ventas,
        pedidos_activos=pedidos_activos,
        productos_disponibles=productos_disponibles,
        clientes_activos=clientes_activos,
        pedidos_recientes=pedidos_recientes,
        stock_bajo=stock_bajo,
        ventas_chart=ventas_chart,
        dias=dias,
        user=session
    )
 
# ---- PEDIDOS ----
@app.route('/pedidos')
def pedidos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    estado_filter = request.args.get('estado', '')
    pedidos_list = data['pedidos']
    if estado_filter:
        pedidos_list = [p for p in pedidos_list if p['estado'] == estado_filter]
    pedidos_list = sorted(pedidos_list, key=lambda x: x['fecha'], reverse=True)
    return render_template('pedidos.html', pedidos=pedidos_list, estado_filter=estado_filter, user=session, clientes=data['clientes'], productos=data['productos'])
 
@app.route('/pedidos/nuevo', methods=['POST'])
def nuevo_pedido():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    data = load_data()
    cliente_id = int(request.form.get('cliente_id'))
    producto_id = int(request.form.get('producto_id'))
    cantidad = int(request.form.get('cantidad', 1))
    notas = request.form.get('notas', '')
    
    cliente = next((c for c in data['clientes'] if c['id'] == cliente_id), None)
    producto = next((p for p in data['productos'] if p['id'] == producto_id), None)
    
    if not cliente or not producto:
        flash('Cliente o producto no encontrado', 'error')
        return redirect(url_for('pedidos'))
    
    nuevo = {
        "id": data['next_pedido_id'],
        "cliente_id": cliente_id,
        "cliente_nombre": cliente['nombre'],
        "producto_id": producto_id,
        "producto_nombre": producto['nombre'],
        "cantidad": cantidad,
        "total": producto['precio'] * cantidad,
        "estado": "Pendiente",
        "fecha": date.today().isoformat(),
        "notas": notas
    }
    data['pedidos'].append(nuevo)
    data['next_pedido_id'] += 1
    save_data(data)
    flash('Pedido creado exitosamente', 'success')
    return redirect(url_for('pedidos'))
 
@app.route('/pedidos/actualizar/<int:pid>', methods=['POST'])
def actualizar_pedido(pid):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    data = load_data()
    nuevo_estado = request.form.get('estado')
    for p in data['pedidos']:
        if int(p['id']) == int(pid):
            estado_anterior = p['estado']
            p['estado'] = nuevo_estado

            if nuevo_estado == 'Entregado' and estado_anterior != 'Entregado':
                for prod in data['productos']:
                    if int(prod['id']) == int(p['producto_id']):
                        prod['stock'] = max(0, prod['stock'] - p['cantidad'])
                        break

            if estado_anterior == 'Entregado' and nuevo_estado != 'Entregado':
                for prod in data['productos']:
                    if int(prod['id']) == int(p['producto_id']):
                        prod['stock'] = prod['stock'] + p['cantidad']
                        break
            break

    save_data(data)
    flash('Estado del pedido actualizado', 'success')
    return redirect(url_for('pedidos'))
 
@app.route('/pedidos/eliminar/<int:pid>', methods=['POST'])
def eliminar_pedido(pid):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    data = load_data()
    data['pedidos'] = [p for p in data['pedidos'] if p['id'] != pid]
    save_data(data)
    flash('Pedido eliminado', 'success')
    return redirect(url_for('pedidos'))
 
# ---- CLIENTES ----
@app.route('/clientes')
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('clientes.html', clientes=data['clientes'], user=session)
 
@app.route('/clientes/nuevo', methods=['POST'])
def nuevo_cliente():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('clientes'))
    data = load_data()
    nuevo = {
        "id": data['next_cliente_id'],
        "nombre": request.form.get('nombre'),
        "empresa": request.form.get('empresa', ''),
        "telefono": request.form.get('telefono', ''),
        "email": request.form.get('email', ''),
        "ciudad": request.form.get('ciudad', ''),
        "activo": True,
        "created_at": date.today().isoformat()
    }
    data['clientes'].append(nuevo)
    data['next_cliente_id'] += 1
    save_data(data)
    flash('Cliente registrado exitosamente', 'success')
    return redirect(url_for('clientes'))
 
@app.route('/clientes/editar/<int:cid>', methods=['POST'])
def editar_cliente(cid):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('clientes'))
    data = load_data()
    for c in data['clientes']:
        if c['id'] == cid:
            c['nombre'] = request.form.get('nombre', c['nombre'])
            c['empresa'] = request.form.get('empresa', c['empresa'])
            c['telefono'] = request.form.get('telefono', c['telefono'])
            c['email'] = request.form.get('email', c['email'])
            c['ciudad'] = request.form.get('ciudad', c['ciudad'])
            break
    save_data(data)
    flash('Cliente actualizado', 'success')
    return redirect(url_for('clientes'))
 
@app.route('/clientes/eliminar/<int:cid>', methods=['POST'])
def eliminar_cliente(cid):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('clientes'))
    data = load_data()
    for c in data['clientes']:
        if c['id'] == cid:
            c['activo'] = False
            break
    save_data(data)
    flash('Cliente desactivado', 'success')
    return redirect(url_for('clientes'))
 
# ---- INVENTARIO ----
@app.route('/inventario')
def inventario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('inventario.html', productos=data['productos'], user=session, alertas_stock=data.get('alertas_stock', 5))
 
@app.route('/inventario/nuevo', methods=['POST'])
def nuevo_producto():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('inventario'))
    data = load_data()
    nuevo = {
        "id": data['next_producto_id'],
        "nombre": request.form.get('nombre'),
        "precio": int(request.form.get('precio', 0)),
        "stock": int(request.form.get('stock', 0)),
        "categoria": request.form.get('categoria', ''),
        "descripcion": request.form.get('descripcion', ''),
        "activo": True
    }
    data['productos'].append(nuevo)
    data['next_producto_id'] += 1
    save_data(data)
    flash('Producto agregado al inventario', 'success')
    return redirect(url_for('inventario'))
 
@app.route('/inventario/editar/<int:pid>', methods=['POST'])
def editar_producto(pid):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('inventario'))
    data = load_data()
    for p in data['productos']:
        if p['id'] == pid:
            p['nombre'] = request.form.get('nombre', p['nombre'])
            p['precio'] = int(request.form.get('precio', p['precio']))
            p['stock'] = int(request.form.get('stock', p['stock']))
            p['categoria'] = request.form.get('categoria', p['categoria'])
            p['descripcion'] = request.form.get('descripcion', p['descripcion'])
            break
    save_data(data)
    flash('Producto actualizado', 'success')
    return redirect(url_for('inventario'))
 
@app.route('/inventario/eliminar/<int:pid>', methods=['POST'])
def eliminar_producto(pid):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('inventario'))
    data = load_data()
    for p in data['productos']:
        if p['id'] == pid:
            p['activo'] = False
            break
    save_data(data)
    flash('Producto desactivado', 'success')
    return redirect(url_for('inventario'))
 
# ---- USUARIOS ----
@app.route('/usuarios')
def usuarios():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Acceso restringido', 'error')
        return redirect(url_for('dashboard'))
    data = load_data()
    return render_template('usuarios.html', usuarios=data['users'], user=session)
 
@app.route('/usuarios/nuevo', methods=['POST'])
def nuevo_usuario():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('usuarios'))
    data = load_data()
    username = request.form.get('username', '').strip()
    if any(u['username'] == username for u in data['users']):
        flash('El nombre de usuario ya existe', 'error')
        return redirect(url_for('usuarios'))
    nuevo = {
        "id": data['next_user_id'],
        "username": username,
        "password": hash_password(request.form.get('password', 'temp123')),
        "role": request.form.get('role', 'gerente'),
        "name": request.form.get('name', ''),
        "email": request.form.get('email', ''),
        "created_at": date.today().isoformat()
    }
    data['users'].append(nuevo)
    data['next_user_id'] += 1
    save_data(data)
    flash('Usuario creado exitosamente', 'success')
    return redirect(url_for('usuarios'))
 
@app.route('/usuarios/eliminar/<int:uid>', methods=['POST'])
def eliminar_usuario(uid):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('No autorizado', 'error')
        return redirect(url_for('usuarios'))
    if uid == session['user_id']:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('usuarios'))
    data = load_data()
    data['users'] = [u for u in data['users'] if u['id'] != uid]
    save_data(data)
    flash('Usuario eliminado', 'success')
    return redirect(url_for('usuarios'))
 
# ---- API para datos en tiempo real ----
@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = load_data()
    pedidos = data['pedidos']
    productos = data['productos']
    total_ventas = sum(p['total'] for p in pedidos if p['estado'] == 'Entregado')
    pedidos_activos = len([p for p in pedidos if p['estado'] in ['Pendiente', 'En Proceso']])
    productos_disponibles = sum(p['stock'] for p in productos if p['activo'])
    return jsonify({
        'total_ventas': total_ventas,
        'pedidos_activos': pedidos_activos,
        'productos_disponibles': productos_disponibles,
    })
 
# ---- ANÁLISIS IA ----
@app.route('/ia')
def ia():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    productos = data['productos']
    pedidos   = data['pedidos']
 
    # Predicción de demanda simulada
    predicciones = []
    for p in productos:
        if not p.get('activo', True):
            continue
        vendidos  = sum(o['cantidad'] for o in pedidos if o['producto_id'] == p['id'])
        demanda   = max(3, round(vendidos * 1.3 + 2))
        predicciones.append({
            'nombre':           p['nombre'],
            'categoria':        p['categoria'],
            'stock':            p['stock'],
            'demanda_predicha': demanda,
            'alerta':           p['stock'] < demanda,
        })
 
    total_ventas  = sum(o['total'] for o in pedidos if o['estado'] == 'Entregado')
    pedidos_mes   = len([o for o in pedidos if o['fecha'] >= '2026-04-01'])
    tasa_entrega  = round(len([o for o in pedidos if o['estado'] == 'Entregado']) / len(pedidos) * 100) if pedidos else 0
 
    ventas_historico    = [650000, 980000, 1200000, 870000, 1450000, 1100000, 1600000, 1350000, 1800000, 1500000, 2100000, 1900000]
    meses_historico     = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    ventas_proyectadas  = [2200000, 2450000, 2800000]
    meses_proyectados   = ['May (p)','Jun (p)','Jul (p)']
 
    return render_template('ia.html',
        predicciones=predicciones,
        total_ventas=total_ventas,
        pedidos_mes=pedidos_mes,
        tasa_entrega=tasa_entrega,
        ventas_historico=ventas_historico,
        meses_historico=meses_historico,
        ventas_proyectadas=ventas_proyectadas,
        meses_proyectados=meses_proyectados,
        user=session,
    )
 
 
@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data    = load_data()
    pedidos  = data['pedidos']
    productos = data['productos']
    clientes  = data['clientes']
    mensaje  = request.json.get('mensaje', '').lower().strip()
 
    if any(w in mensaje for w in ['pedido', 'orden', 'compra']):
        pendientes = len([p for p in pedidos if p['estado'] == 'Pendiente'])
        proceso    = len([p for p in pedidos if p['estado'] == 'En Proceso'])
        resp = f"Hay {len(pedidos)} pedidos en total. {pendientes} pendientes y {proceso} en proceso. ¿Quieres más detalle?"
    elif any(w in mensaje for w in ['stock', 'inventario', 'producto']):
        bajos = [p['nombre'] for p in productos if p['stock'] <= 5 and p.get('activo', True)]
        total = sum(p['stock'] for p in productos if p.get('activo', True))
        if bajos:
            resp = f"⚠️ Stock crítico en: {', '.join(bajos)}. Total de unidades disponibles: {total}."
        else:
            resp = f"El inventario está bien. {total} unidades disponibles en {len(productos)} productos activos."
    elif any(w in mensaje for w in ['venta', 'ingreso', 'dinero', 'total']):
        total = sum(p['total'] for p in pedidos if p['estado'] == 'Entregado')
        resp  = f"Las ventas confirmadas (pedidos entregados) suman ${total:,}. Se han cerrado {len([p for p in pedidos if p['estado'] == 'Entregado'])} pedidos."
    elif any(w in mensaje for w in ['cliente']):
        resp = f"Hay {len([c for c in clientes if c.get('activo', True)])} clientes activos registrados."
    elif any(w in mensaje for w in ['predicci', 'demanda', 'ia', 'recomend']):
        alertas = [p['nombre'] for p in productos if p['stock'] <= 5 and p.get('activo', True)]
        if alertas:
            resp = f"🔮 Basado en el historial, predigo alta demanda próximamente. Recomiendo reabastecer: {', '.join(alertas)}."
        else:
            resp = "🔮 El análisis de demanda indica niveles estables. No hay necesidad urgente de reabastecimiento."
    elif any(w in mensaje for w in ['hola', 'ayuda', 'que puedes', 'opciones']):
        resp = "👋 Hola, soy el asistente IA de DWR. Puedo ayudarte con:\n• Pedidos y órdenes\n• Estado del inventario\n• Resumen de ventas\n• Predicciones de demanda\n¿Sobre qué quieres saber?"
    else:
        resp = "Puedo ayudarte con información sobre pedidos, inventario, ventas y predicciones. ¿Qué necesitas consultar?"
 
    return jsonify({'respuesta': resp})

# ---- DRON ----
@app.route('/dron')
def dron():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = load_data()
    zonas = data.get('zonas_dron', [])
    ultimo_escaneo = data.get('ultimo_escaneo_dron', 'Hoy 08:30')
    return render_template('dron.html', zonas=zonas, ultimo_escaneo=ultimo_escaneo, user=session)
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)
 