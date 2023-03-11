from flask import Flask, render_template, request
import sqlite3

from werkzeug.utils import redirect

app = Flask(__name__)


@app.route('/',methods=['GET', 'POST'])
def index():
    Address = request.form.get('Address',"")
    conn = sqlite3.connect('places.db')
    cur = conn.cursor()
    cur.execute("select * from places where Address like '%{}%'".format(Address))
    list = cur.fetchall()
    print(list[0])
    return render_template('index.html', list=list)

@app.route('/add',methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        Address = request.form.get('Address', "")
        conn = sqlite3.connect('places.db')
        cur = conn.cursor()
        cur.execute("insert into places(Address) values ('{}')".format(Address))
        conn.commit()
        return redirect('/')
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)