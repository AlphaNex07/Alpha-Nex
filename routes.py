import os
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Upload, Review, Strike, WithdrawalRequest, AdminAction
from forms import SignupForm, LoginForm, UploadForm, ReviewForm, WithdrawalForm
from utils import allowed_file, get_file_size, calculate_xp_reward
from openai_service import detect_duplicate_content, check_content_quality

# Route definitions for the Alpha Nex platform
# Handles user authentication, content management, and platform features

@app.route('/')
def index():
    """Landing page for Alpha Nex platform"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration endpoint"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now start uploading and reviewing content.', 'success')
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('auth/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_banned:
                flash('Your account has been banned due to violations.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user stats
    upload_count = Upload.query.filter_by(user_id=current_user.id).count()
    review_count = Review.query.filter_by(reviewer_id=current_user.id).count()
    
    # Get recent uploads
    recent_uploads = Upload.query.filter_by(user_id=current_user.id)\
                                .order_by(Upload.uploaded_at.desc()).limit(5).all()
    
    # Check daily upload limit
    daily_remaining = current_user.get_daily_upload_remaining()
    daily_remaining_mb = daily_remaining / (1024 * 1024)
    
    return render_template('dashboard.html', 
                         upload_count=upload_count,
                         review_count=review_count,
                         recent_uploads=recent_uploads,
                         daily_remaining_mb=daily_remaining_mb)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if current_user.is_banned:
        flash('Your account is banned and cannot upload content.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        if file and allowed_file(file.filename):
            # Check file size and daily limit
            file_size = get_file_size(file)
            
            if not current_user.can_upload(file_size):
                flash('Upload would exceed daily 500MB limit.', 'error')
                return render_template('uploader/upload.html', form=form)
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(file_path)
                
                # Create upload record
                upload = Upload(
                    user_id=current_user.id,
                    filename=unique_filename,
                    original_filename=filename,
                    file_path=file_path,
                    file_size=file_size,
                    description=form.description.data,
                    category=form.category.data,
                    ai_consent=form.ai_consent.data
                )
                
                # Update user's daily upload count
                current_user.daily_upload_bytes += file_size
                
                db.session.add(upload)
                db.session.commit()
                
                # Run AI analysis (in background ideally, but simplified here)
                try:
                    duplicate_score, spam_score = detect_duplicate_content(file_path, form.description.data)
                    upload.duplicate_score = duplicate_score
                    upload.spam_score = spam_score
                    
                    # Auto-flag if scores are high
                    if duplicate_score > 0.8 or spam_score > 0.7:
                        upload.status = 'flagged'
                        current_user.add_strike('uploader', f'High duplicate ({duplicate_score:.2f}) or spam ({spam_score:.2f}) score')
                    
                    db.session.commit()
                except Exception as e:
                    app.logger.error(f"AI analysis failed: {e}")
                
                flash('File uploaded successfully! Status: Pending - Will be approved within 24 hours.', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Upload failed: {str(e)}', 'error')
    
    # Calculate remaining daily upload capacity
    daily_remaining = current_user.get_daily_upload_remaining()
    daily_remaining_mb = daily_remaining / (1024 * 1024)
    
    return render_template('uploader/upload.html', form=form, daily_remaining_mb=daily_remaining_mb)

@app.route('/review')
@login_required
def review_content():
    if current_user.is_banned:
        flash('Your account is banned and cannot review content.', 'error')
        return redirect(url_for('dashboard'))
    
    # Create a dummy "website review" object for users to review the platform itself
    # Instead of reviewing uploaded content, users now review the website/platform
    
    # Check if user has already submitted a website review today
    from datetime import date
    today_review = Review.query.filter_by(
        reviewer_id=current_user.id,
        upload_id=0  # Using 0 as special ID for website reviews
    ).filter(
        func.date(Review.created_at) == date.today()
    ).first()
    
    if today_review:
        flash('You have already reviewed our website today. Come back tomorrow!', 'info')
        return redirect(url_for('dashboard'))
    
    # Create a mock upload object representing the website itself
    class WebsiteReview:
        id = 0
        original_filename = "Alpha Nex Platform"
        category = "website"
        file_size = 0
        description = "Rate our website and platform! Tell us what you think about the user interface, features, and overall experience."
        uploaded_at = datetime.utcnow()
        reviews = []
        duplicate_score = 0
        spam_score = 0
        
        def get_average_rating(self):
            website_reviews = Review.query.filter_by(upload_id=0).all()
            if not website_reviews:
                return None
            good_reviews = sum(1 for r in website_reviews if r.rating == 'good')
            return good_reviews / len(website_reviews)
    
    upload = WebsiteReview()
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Create review (using upload_id=0 for website reviews)
        review = Review(
            upload_id=0,  # Special ID for website reviews
            reviewer_id=current_user.id,
            rating=form.rating.data,
            description=form.description.data,
            xp_earned=calculate_xp_reward('review')
        )
        
        # Award XP to reviewer
        current_user.xp_points += review.xp_earned
        
        db.session.add(review)
        db.session.commit()
        
        flash(f'Review submitted! You earned {review.xp_earned} XP points.', 'success')
        return redirect(url_for('review_content'))
    
    return render_template('reviewer/review.html', upload=upload, form=form)

@app.route('/profile')
@login_required
def profile():
    # Get user's strikes and violation history
    strikes = Strike.query.filter_by(user_id=current_user.id)\
                         .order_by(Strike.created_at.desc()).all()
    
    # Get withdrawal requests
    withdrawals = WithdrawalRequest.query.filter_by(user_id=current_user.id)\
                                        .order_by(WithdrawalRequest.created_at.desc()).all()
    
    return render_template('profile.html', strikes=strikes, withdrawals=withdrawals)

@app.route('/delete_upload/<int:upload_id>')
@login_required
def delete_upload(upload_id):
    upload = Upload.query.get_or_404(upload_id)
    
    if upload.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate penalty if beyond free deletion window
    penalty = upload.get_deletion_penalty()
    
    if penalty > 0:
        if current_user.xp_points < penalty:
            flash(f'Insufficient XP to delete. Penalty: {penalty} XP (You have: {current_user.xp_points} XP)', 'error')
            return redirect(url_for('dashboard'))
        
        current_user.xp_points -= penalty
        flash(f'Content deleted with {penalty} XP penalty.', 'warning')
    else:
        flash('Content deleted within free window.', 'success')
    
    # Delete file and record
    try:
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
    except Exception as e:
        app.logger.error(f"Failed to delete file {upload.file_path}: {e}")
    
    db.session.delete(upload)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/request_withdrawal', methods=['GET', 'POST'])
@login_required
def request_withdrawal():
    form = WithdrawalForm()
    
    if form.validate_on_submit():
        amount_xp = form.amount_xp.data
        
        if amount_xp > current_user.xp_points:
            flash('Insufficient XP points.', 'error')
            return render_template('profile.html', form=form)
        
        if amount_xp < 100:
            flash('Minimum withdrawal is 100 XP.', 'error')
            return render_template('profile.html', form=form)
        
        # Calculate USD amount (example: 100 XP = $1)
        amount_usd = amount_xp / 100.0
        
        withdrawal = WithdrawalRequest(
            user_id=current_user.id,
            amount_xp=amount_xp,
            amount_usd=amount_usd,
            payment_method=form.payment_method.data,
            payment_details=form.payment_details.data
        )
        
        db.session.add(withdrawal)
        db.session.commit()
        
        flash(f'Withdrawal request submitted for {amount_xp} XP (${amount_usd:.2f}).', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', withdrawal_form=form)

@app.route('/admin')
@login_required
def admin_panel():
    # Simple admin check (in production, use proper role system)
    if current_user.email not in ['admin@alphanex.com']:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get pending items
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    flagged_content = Upload.query.filter_by(status='flagged').count()
    total_users = User.query.count()
    
    # Get recent violations
    recent_strikes = Strike.query.order_by(Strike.created_at.desc()).limit(10).all()
    
    return render_template('admin/panel.html', 
                         total_users=total_users,
                         pending_withdrawals=pending_withdrawals,
                         flagged_content=flagged_content,
                         recent_strikes=recent_strikes)

# API endpoint for countdown timer updates
@app.route('/api/upload_status/<int:upload_id>')
@login_required
def upload_status(upload_id):
    upload = Upload.query.get_or_404(upload_id)
    
    if upload.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    time_remaining = upload.deletion_deadline - datetime.utcnow()
    hours_remaining = max(0, time_remaining.total_seconds() / 3600)
    
    return jsonify({
        'hours_remaining': hours_remaining,
        'can_delete_free': upload.can_delete_free(),
        'penalty': upload.get_deletion_penalty()
    })
