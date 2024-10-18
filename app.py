from flask import Flask, request, render_template, redirect, url_for, session, flash
import psycopg2
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Consider using an environment variable for production
bcrypt = Bcrypt(app)

# Database connection parameters
db_params = {
    'dbname': 'webapp',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**db_params)

@app.route('/')
def home():
    signup_success = request.args.get('signup')
    return render_template('index.html', signup_success=signup_success)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password)
                    )
                    conn.commit()
            flash("User successfully signed up!", "success")
            return redirect(url_for('home', signup='success'))
        except Exception as e:
            print(f"Error occurred: {e}")
            flash("Signup failed. Please try again.", "danger")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                    result = cursor.fetchone()

                    if result and bcrypt.check_password_hash(result[0], password):
                        session['username'] = username
                        flash("Login successful!", "success")
                        return redirect(url_for('dashboard'))  # Redirect to dashboard
                    else:
                        flash("Invalid username or password.", "danger")
        except Exception as e:
            print(f"Error occurred during login: {e}")
            flash("An error occurred. Please try again.", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if username:
        return render_template('dashboard.html', username=username)
    else:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

@app.route('/user_details')
def user_details():
    username = session.get('username')
    if username:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
                    result = cursor.fetchone()
                    email = result[0] if result else None
            return render_template('user_details.html', username=username, email=email)
        except Exception as e:
            print(f"Error occurred while fetching user details: {e}")
            flash("Could not retrieve user details.", "danger")
            return redirect(url_for('dashboard'))
    else:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

@app.route('/devops_tools')
def devops_tools():
    return render_template('devops.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
