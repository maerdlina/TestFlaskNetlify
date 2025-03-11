from flask_frozen import Freezer
from project import create_app

# Инициализация приложения и WebSocket
app, socketio = create_app()

# Инициализация Freezer
freezer = Freezer(app)

if __name__ == '__main__':
    # Запуск приложения с поддержкой WebSocket
    socketio.run(app, debug=True)
