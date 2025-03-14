from flask import Flask, render_template
import numpy as np
from flask_socketio import SocketIO
from beso import Cantilever, CvxFEA, BESO2D

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html')

@socketio.on('start_optimization')
def handle_optimization(data):
    # Получаем данные из формы
    nelx = int(data['nelx'])
    nely = int(data['nely'])
    vol_frac = float(data['vol_frac'])
    penal = float(data['penal'])
    rmin = float(data['rmin'])
    er = float(data['er'])
    load_value = float(data.get('load_value', -1))  # Получаем значение нагрузки из формы

    # Инициализация задачи
    E = 1
    nu = 0.3
    load = Cantilever(nelx, nely, E, nu)
    fesolver = CvxFEA()
    optimization = BESO2D(load, fesolver)

    # Модифицируем метод topology для отправки данных через WebSocket
    def send_iteration_data(itr, x):
        socketio.emit('iteration_update', {
            'iteration': itr,
            'topology': x.tolist(),
            'loadValue': load_value  # Отправляем значение нагрузки
        })

    # Выполнение оптимизации
    optimization.topology(vol_frac, er, rmin, penal, Plotting=False, Saving=False, callback=send_iteration_data)

if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app, debug=True)
