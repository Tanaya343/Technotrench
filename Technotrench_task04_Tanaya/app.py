from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message 
import MySQLdb.cursors 
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'
#testing
# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootkali'
app.config['MYSQL_DB'] = 'phishing_simulation'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tanbr973@gmail.com'
app.config['MAIL_PASSWORD'] = 'rohp slyn scgx qngu'

mail = Mail(app)

# Routes

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        # Direct comparison with the plain text password
        if user and user['password'] == password:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return 'Incorrect username/password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Store the plain text password directly

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'employee'))
        mysql.connection.commit()

        return 'User registered successfully'
    return render_template('register.html')


@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            # template = request.form['template']
            target_group = request.form['target_group']
            subject = request.form['subject']  # Get subject from form
            email_body = request.form['email_body']  # Get email body from form
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO campaigns (name, template, target_group) VALUES (%s, %s, %s)', (name, email_body, target_group))
            mysql.connection.commit()

            # Retrieve the campaign_id of the newly created campaign
            campaign_id = cursor.lastrowid

            # Fetch target employees
            cursor.execute('SELECT * FROM users WHERE role="employee"')
            employees = cursor.fetchall()

            # Send phishing email to each employee
            for employee in employees:
                token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                # Include campaign_id in the link
                link = f"http://localhost:5000/click/{employee[0]}/{campaign_id}/{token}"
                
                # Customize the email body with the generated link
                customized_body = f"{email_body}\n\nClick on the following link: {link}"

                msg = Message(subject, sender='tanbr973@gmail.com', recipients=[employee[1]])
                msg.body = customized_body
                mail.send(msg)

            return redirect(url_for('index'))
        return render_template('create_campaign.html')
    return redirect(url_for('login'))

@app.route('/click/<int:user_id>/<int:campaign_id>/<string:token>')
def click(user_id, campaign_id, token):
    cursor = mysql.connection.cursor()
    
    # Check if the user has already clicked for this campaign
    cursor.execute('SELECT clicked FROM interactions WHERE user_id = %s AND campaign_id = %s', (user_id, campaign_id))
    interaction = cursor.fetchone()
    
    if interaction:
        # Increment the clicked field if the record exists
        cursor.execute('UPDATE interactions SET clicked = clicked + 1 WHERE user_id = %s AND campaign_id = %s', (user_id, campaign_id))
    else:
        # Insert a new record if no interaction exists
        cursor.execute('INSERT INTO interactions (user_id, campaign_id, clicked) VALUES (%s, %s, %s)', (user_id, campaign_id, 1))
    
    mysql.connection.commit()
    return redirect(url_for('education'))
@app.route('/report')
def report():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM interactions')
        results = cursor.fetchall()
        return render_template('report.html', results=results)
    return redirect(url_for('login'))

@app.route('/education')
def education():
    return render_template('education.html')

if __name__ == "__main__":
    app.run(debug=True)
