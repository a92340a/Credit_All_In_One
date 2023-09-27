import os
from dotenv import load_dotenv
from server_producer import app, socketio

load_dotenv()

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('COMMON_HOST'), port=os.getenv('PRODUCER_PORT'), debug=True, allow_unsafe_werkzeug=True)

