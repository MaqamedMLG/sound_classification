from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, AudioFile
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import cast, String, func
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mailman import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# send email function
def send_lock_email(user):
    sender_email = "flaskktu@fastmail.com"
    receiver_email = user.email

    msg = EmailMessage(
        "Account Locked Notification",
        f"Dear {user.firstName},\n\nYour account has been locked due to suspicious activity. Please contact the administrator for further assistance.\n\nBest Regards,\n\nMLG Sound Team",
        sender_email,
        [receiver_email]
    )
    try:
        msg.send()
        print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if user.locked:
                send_lock_email(user)
                flash('⚠️ Your account has been locked. Please contact the administrator flaskktu@fastmail.com.', category='false')
                return render_template("login.html", user=current_user)

            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                if user.email == 'admin@gmail.com':
                    return redirect(url_for('auth.admin_page'))
                return redirect(url_for('views.home'))
            else:
                flash('⚠️ Incorrect password. Please try again', category='false')
        else:
            flash('⚠️ This email does not exist', category='false')
        
    return render_template("login.html", user=current_user)

# delete user route
@auth.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    if current_user.email == 'admin@gmail.com':
        user_to_delete = User.query.get_or_404(id)
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('✅ User was successfully deleted!', category='true')
        return redirect(url_for('auth.admin_page'))
    else:
        return redirect(url_for('views.home'))

# admin route
@auth.route('/admin')
@login_required
def admin_page():
    if current_user.email == 'admin@gmail.com':
        page = request.args.get('page', 1, type=int)
        per_page = 5
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort')
        
        query = User.query.filter(User.email != 'admin@gmail.com')
        
        if search_query:
            search_filter = (cast(User.id, String).startswith(search_query)) | \
                            (User.firstName.startswith(search_query)) | \
                            (User.email.startswith(search_query))
            query = query.filter(search_filter)
        
        if sort_by == 'name':
            query = query.order_by(User.firstName.asc())
        elif sort_by == 'date':
            query = query.order_by(User.date.desc())
        elif sort_by == 'uploads':
            query = query.outerjoin(AudioFile, User.id == AudioFile.user_id) \
                         .group_by(User.id) \
                         .order_by(func.count(AudioFile.id).desc())

        users_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        uploads_count = {}
        for user in users_pagination.items:
            count = AudioFile.query.filter_by(user_id=user.id).count()
            uploads_count[user.id] = count
        
        uploads_types = {}
        for user in users_pagination.items:
            mime_types = AudioFile.query.with_entities(AudioFile.mimetype).filter_by(user_id=user.id).all()
            uploads_types[user.id] = list({mime_type[0] for mime_type in mime_types})

        return render_template(
            "admin.html",
            user=current_user,
            users=users_pagination.items,
            pagination=users_pagination,
            search_query=search_query,
            uploads_count=uploads_count,
            uploads_types=uploads_types,
            sort_by=sort_by
        )
    else:
        return redirect(url_for('views.home'))

# logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# new user route for admin
@auth.route('/create-user', methods=['POST'])
@login_required
def create_user():
    if current_user.email == 'admin@gmail.com':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, firstName=name, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('✅ New user added successfully!', category='true')
        return redirect(url_for('auth.admin_page'))
    else:
        flash('⚠️ You do not have permission to add users', category='false')
        return redirect(url_for('views.home'))

# update user info
@auth.route('/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    user_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        email = request.form.get('email')
        password = request.form.get('password')    
        
        user_to_update.firstName = firstName
        user_to_update.email = email   
        
        if password:
            hashed_password = generate_password_hash(password)
            user_to_update.password = hashed_password
        
        db.session.commit()
        
        flash('✅ User information updated successfully!', category='true')
        return redirect(url_for('auth.admin_page'))
    
    return render_template('update_user.html', user=user_to_update)

# lock user route
@auth.route('/lock-user/<int:id>')
@login_required
def lock_user(id):
    if current_user.email == 'admin@gmail.com':
        user_to_lock = User.query.get_or_404(id)
        user_to_lock.locked = True
        db.session.commit()
        send_lock_email(user_to_lock)
        flash('✅ User account has been locked', category='true')
        return redirect(url_for('auth.admin_page'))

# unlock user route
@auth.route('/unlock-user/<int:id>')
@login_required
def unlock_user(id):
    if current_user.email == 'admin@gmail.com':
        user_to_unlock = User.query.get_or_404(id)
        user_to_unlock.locked = False
        db.session.commit()
        flash('✅ User account has been unlocked', category='true')
        return redirect(url_for('auth.admin_page'))

# register route
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('⚠️ This email already exists', category='false')
        elif len(email) < 6:
            flash('⚠️ The email must be greater than 5 characters', category='false')
        elif len(firstName) < 2:
            flash('⚠️ The first name must be greater than 1 character', category='false')
        elif password1 != password2:
            flash('⚠️ The passwords don\'t match', category='false')
        elif len(password1) < 8:
            flash('⚠️ The password must be at least 8 characters', category='false')
        else:
            hashed_password = generate_password_hash(password1)
            new_user = User(email=email, firstName=firstName, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash('✅ Account created!', category='true')
            return redirect(url_for('views.home'))
        
    return render_template("signup.html", user=current_user)