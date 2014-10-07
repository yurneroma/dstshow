import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash



# configuration
DATABASE = './dstshow.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)



def connect_db():
    return sqlite3.connect(app.config['DATABASE'])



@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route("/")
def show_entries():
    cur = g.db.execute('select processed, unprocessed  from dstshow')
    dstshows = [dict(processed=row[0], unprocessed=row[1]) for row in cur.fetchall()]
    return render_template('dstshow.html', dstshows=dstshows)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into dstshow (processed, unprocessed) values (?, ?)',
                 [request.form['processed'], request.form['unprocessed']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)




@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    app.run()