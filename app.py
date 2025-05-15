from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)

# Basic config
app.config['SECRET_KEY'] = 'some-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

# Email config - replace with your actual email and app password (no spaces)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kabacheuniv@gmail.com'       # <-- your email here
app.config['MAIL_PASSWORD'] = 'uwmdhomjmozopkrr'           # <-- your app password (no spaces)
app.config['MAIL_DEFAULT_SENDER'] = 'kabacheuniv@gmail.com' # <-- your email here

db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_coupon_code(length=8):
    """Generate a random coupon code."""
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials. Try again.')
            return redirect(url_for('login'))
        login_user(user)
        print(f"User found: {user.email}, Password correct")  # Debug print
        return redirect(url_for('submit_waste'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_waste():
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        description = request.form.get('description')
        coupon = generate_coupon_code()
        flash(f"Submission successful! Your coupon code is: {coupon}")
        

        return render_template('confirmation.html', coupon_code=coupon)

    return render_template('submit_waste.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
