from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from zhipuai import ZhipuAI

app = Flask(__name__)
socketio = SocketIO(app)

# 存储每个客户端的会话历史
client_sessions = {}
client = ZhipuAI(api_key="a6df69db348269042b6fc9cb64d92ad5.JSCKkZMvUQbx616Z")

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

@app.before_first_request
def initialize_client_sessions():
    client_sessions.clear()

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    # 初始化该客户端的会话历史
    client_sessions[request.sid] = []

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开连接')
    # 清除该客户端的会话历史
    if request.sid in client_sessions:
        del client_sessions[request.sid]

@socketio.on('message')
def handle_message(data):
    print('收到消息:', data)
    # 将用户消息添加到会话历史
    client_sessions[request.sid].append({"role": "user", "content": data})
    
    try:
        # 调用 AI 处理更新后的会话历史
        response = ai("\n".join([msg['content'] for msg in client_sessions[request.sid]]))  # 优化为传递完整会话历史
        for chunk in response:
            message = chunk.choices[0].delta.content
            if message:
                # 将 AI 响应添加到会话历史
                client_sessions[request.sid].append({"role": "ai", "content": message})
                emit('response', message)
                socketio.sleep(0)  # 考虑是否需要
    except Exception as e:
        print(f"处理消息时出错: {e}")
        emit('response', "处理您的消息时出错。")

@app.route('/')
def index():
    return render_template('index.html')  # 渲染前端页面

if __name__ == '__main__':
    socketio.run(app, port=8888)