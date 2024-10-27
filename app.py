from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import mysql.connector

app = Flask(__name__)
app.secret_key = 'temporary_key'
Bootstrap(app)  # Initialize Flask-Bootstrap

# Function to connect to AWS RDS MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='flashdb.c7g4csqm6jl5.us-east-1.rds.amazonaws.com',  
        user='admin',
        password='Flaskdb69',
        database='flashdb'
    )

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            return render_template('login.html')
        finally:
            conn.close()

        if result and check_password_hash(result[0], password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    # Example URLs for course material from S3
    course_urls = [
        "https://flasknm.s3.us-east-1.amazonaws.com/DC_UNIT3.pdf",
        "https://flasknm.s3.us-east-1.amazonaws.com/DL_UNIT3.pdf"
    ]
    return render_template('dashboard.html', course_urls=course_urls)

# Logout Route
@app.route('/logout')
def logout():
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
