from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Wish, db

feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feed_bp.route('/')
def index():
    pub_wishes = Wish.query.filter_by(
        is_public=True,
        is_completed=False
    ).order_by(Wish.created_at.desc()).limit(50).all()

    for wish in pub_wishes:
        wish.calculate_growth()
    db.session.commit()

    return render_template('feed/index.html', wishes=pub_wishes)


@feed_bp.route('/user/<int:user_id>')
def user_wishes(user_id):
    wishes = Wish.query.filter_by(
        user_id=user_id,
        is_public=True,
        is_completed=False
    ).order_by(Wish.created_at.desc()).all()

    if not wishes:
        flash('У этого пользователя нет публичных желаний', 'info')
        return redirect(url_for('feed.index'))

    owner = wishes[0].owner if wishes and wishes[0].owner else None

    for wish in wishes:
        wish.calculate_growth()
    db.session.commit()

    return render_template('feed/user_wishes.html', wishes=wishes, owner=owner)


@feed_bp.route('/vote/<int:wish_id>', methods=['POST'])
@login_required
def vote_wish(wish_id):
    from .models import Vote

    wish = Wish.query.get_or_404(wish_id)

    if not wish.is_public:
        flash('Это желание недоступно для голосования', 'danger')
        return redirect(url_for('feed.index'))

    if wish.user_id == current_user.id:
        flash('Вы не можете голосовать за свои желания', 'warning')
        return redirect(url_for('feed.index'))

    vote_exists = Vote.query.filter_by(wish_id=wish_id, voter_id=current_user.id).first()
    if vote_exists:
        flash('Вы уже голосовали за это желание', 'info')
        return redirect(url_for('feed.index'))

    vote = Vote(wish_id=wish_id, voter_id=current_user.id)
    db.session.add(vote)
    db.session.commit()

    flash('Ваш голос учтен!', 'success')
    return redirect(url_for('feed.index'))
