from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads/encrypted'

from models import db, User, File, Share

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('base.html')

from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
import os
from werkzeug.utils import secure_filename
from crypto_utils import generate_key, encrypt_file, decrypt_file
from drive_storage import upload_encrypted, download_encrypted

@app.route('/dashboard')
@login_required
def dashboard():
    files = File.query.filter_by(owner_id=current_user.id).all()
    return render_template('dashboard.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    data = file.read()
    key = generate_key()
    encrypted = encrypt_file(data, key)

    filename = secure_filename(file.filename) or 'uploaded-file'
    drive_file_id = upload_encrypted(encrypted, filename + '.enc')

    new_file = File(
        filename=filename,
        encrypted_path='gdrive:' + drive_file_id,
        owner_id=current_user.id,
        key=key.decode()
    )
    db.session.add(new_file)
    db.session.commit()
    flash('File uploaded and encrypted')
    return redirect(url_for('dashboard'))
@app.route('/share/<int:file_id>', methods=['POST'])
@login_required
def share_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.owner_id != current_user.id:
        flash('Not authorized')
        return redirect(url_for('dashboard'))

    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('dashboard'))

    share = Share(file_id=file.id, shared_with_id=user.id)
    db.session.add(share)
    db.session.commit()
    flash('File shared')
    return redirect(url_for('dashboard'))
@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)

    # Check if owner or shared with current user
    shared = Share.query.filter_by(file_id=file.id, shared_with_id=current_user.id).first()
    if file.owner_id != current_user.id and not shared:
        flash('Access denied')
        return redirect(url_for('dashboard'))

    if not file.encrypted_path.startswith('gdrive:'):
        flash('This file is not connected to Google Drive.', 'error')
        return redirect(url_for('dashboard'))

    encrypted = download_encrypted(file.encrypted_path.removeprefix('gdrive:'))

    decrypted = decrypt_file(encrypted, file.key.encode())
    download_name = secure_filename(file.filename) or 'downloaded-file'
    return send_file(BytesIO(decrypted), as_attachment=True, download_name=download_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)