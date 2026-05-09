from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Wish, Achievement, db
from .forms import CompleteWishForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        active_wishes = Wish.query.filter_by(
            user_id=current_user.id,
            is_completed=False
        ).order_by(Wish.created_at.desc()).limit(6).all()

        total_wishes = Wish.query.filter_by(user_id=current_user.id).count()
        completed_wishes = Achievement.query.filter_by(user_id=current_user.id).count()
        total_saved = sum(w.current_amount for w in Wish.query.filter_by(user_id=current_user.id))

        for wish in active_wishes:
            wish.calculate_growth()
        db.session.commit()

        recent_achievements = Achievement.query.filter_by(
            user_id=current_user.id
        ).order_by(Achievement.completed_at.desc()).limit(3).all()

        return render_template('dashboard.html',
                             wishes=active_wishes,
                             total_wishes=total_wishes,
                             completed_wishes=completed_wishes,
                             total_saved=total_saved,
                             recent_achievements=recent_achievements)

    return render_template('landing.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/achievements')
@login_required
def achievements():
    user_achievements = Achievement.query.filter_by(
        user_id=current_user.id
    ).order_by(Achievement.completed_at.desc()).all()

    return render_template('achievements.html', achievements=user_achievements)
