from flask import Flask, render_template, request, redirect
import mysql.connector
import os

app = Flask(__name__)

def delete_last_message():
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'example'),
        database=os.environ.get('MYSQL_DATABASE', 'appdb')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM messages ORDER BY id DESC LIMIT 1;")
    result = cursor.fetchone()
    if result:
        last_id = result[0]
        cursor.execute("DELETE FROM messages WHERE id = %s;", (last_id,))
        conn.commit()
    cursor.close()
    conn.close()


@app.route('/delete_last', methods=['POST'])
def delete_last():
    delete_last_message()
    return redirect('/')



def insert_message(text):
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'example'),
        database=os.environ.get('MYSQL_DATABASE', 'appdb')
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (text) VALUES (%s)", (text,))
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    insert_message(text)
    return redirect('/')


def get_messages():
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'example'),
        database=os.environ.get('MYSQL_DATABASE', 'appdb')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM messages ORDER BY id ASC;")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in results]


@app.route('/')
def index():
    messages = get_messages()
    return render_template("index.html", messages=messages)
