from flask import Flask, request, jsonify
import pymysql
import bcrypt

app = Flask(__name__)

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'chat_db'
}


def get_db_connection():
    return pymysql.connect(**db_config)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        return jsonify({'message': '注册成功！'}), 201
    except pymysql.IntegrityError:
        return jsonify({'message': '用户名已存在！'}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return jsonify({'message': '登录成功！'}), 200
        else:
            return jsonify({'message': '用户名或密码错误！'}), 401
    finally:
        cursor.close()
        conn.close()


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, message))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '消息发送成功！'}), 201


@app.route('/get_messages', methods=['GET'])
def get_messages():
    user1 = request.args.get('user1')
    user2 = request.args.get('user2')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT sender, receiver, message, timestamp FROM messages 
                      WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)
                      ORDER BY timestamp''', (user1, user2, user2, user1))

    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(messages), 200


if __name__ == '__main__':
    app.run(debug=True)
