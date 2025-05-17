from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model for login
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    java = db.Column(db.Float, nullable=False)
    python = db.Column(db.Float, nullable=False)
    dbms = db.Column(db.Float, nullable=False)
    os = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    # Create default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Dashboard - list students
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    students = Student.query.all()
    return render_template('dashboard.html', students=students)

# Add student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            year=request.form['year'],
            branch=request.form['branch'],
            java=float(request.form['java']),
            python=float(request.form['python']),
            dbms=float(request.form['dbms']),
            os=float(request.form['os'])
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

# Edit student
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.year = request.form['year']
        student.branch = request.form['branch']
        student.java = float(request.form['java'])
        student.python = float(request.form['python'])
        student.dbms = float(request.form['dbms'])
        student.os = float(request.form['os'])
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_student.html', student=student)

# Delete student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# Change password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
