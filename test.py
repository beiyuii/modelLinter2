from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from zhipuai import ZhipuAI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

client = ZhipuAI(api_key="a6df69db348269042b6fc9cb64d92ad5.JSCKkZMvUQbx616Z")


@socketio.on('connect')
def handle_connect():
    print('Client connected')



@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    print('received message:', data)
    response = ai(data)
    for chunk in response:
        print(chunk.choices[0].delta.content)
        message = chunk.choices[0].delta.content
        # emit('response', message)
        socketio.send(message)
        # print(66666)  # 确认 emit 是否立即执行


def ai(msg):
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": msg},
        ],
        tools=[
            {
                "type": "retrieval",
                "retrieval": {
                    "knowledge_id": "1789366141454630912",
                    "prompt_template": "{{knowledge}}\n\"\"\"\n{{question}}\n\"\"\"\n你是linter——ai'。",
                }
            }
        ],
        stream=True,
    )
    return response
    # for chunk in response:
    #     print(chunk.choices[0].delta)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8887)