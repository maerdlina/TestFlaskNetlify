from flask_frozen import Freezer
from myapp import socketio

freezer = Freezer(socketio)

if __name__ == '__main__':
    freezer.freeze()
