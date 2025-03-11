from flask import Flask, render_template
from flask_socketio import SocketIO
from beso import Cantilever, CvxFEA, BESO2D

def create_app():
    # Создаем Flask-приложение
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Установите секретный ключ
    socketio = SocketIO(app)

    # Маршрут для главной страницы
    @app.route('/')
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

        # Инициализация задачи
        E = 1
        nu = 0.3
        load = Cantilever(nelx, nely, E, nu)
        fesolver = CvxFEA()
        optimization = BESO2D(load, fesolver)

        # Модифицируем метод topology для отправки данных через WebSocket
        def send_iteration_data(itr, x):
            print(f"Iteration: {itr}, Topology shape: {x.shape}, Min: {x.min()}, Max: {x.max()}")  # Логирование
            socketio.emit('iteration_update', {
                'iteration': itr,
                'topology': x.tolist()
            })

        # Выполнение оптимизации
        optimization.topology(vol_frac, er, rmin, penal, Plotting=False, Saving=False, callback=send_iteration_data)
    return app, socketio


