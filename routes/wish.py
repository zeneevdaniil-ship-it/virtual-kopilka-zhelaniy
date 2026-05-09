from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import Wish, Contribution, Vote, db, MagicSlotSession
from .forms import WishForm, ContributionForm, MagicSlotForm, CompleteWishForm, VoteForm
from werkzeug.utils import secure_filename
from .config import Config
import os
import random
from datetime import datetime
from uuid import uuid4

wish_bp = Blueprint('wish', __name__, url_prefix='/wish')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@wish_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = WishForm()

    if request.method == 'POST':
        if form.validate():
            try:
                unit_label = form.unit_label.data
                if unit_label == 'другое' and form.custom_unit.data:
                    unit_label = form.custom_unit.data

                icon_path = None
                if form.icon.data and hasattr(form.icon.data, 'filename') and form.icon.data.filename:
                    file = form.icon.data
                    if allowed_file(file.filename):
                        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                        _, ext = os.path.splitext(file.filename)
                        filename = secure_filename(f"{current_user.id}_{uuid4().hex}{ext.lower()}")
                        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                        file.save(filepath)
                        icon_path = filename
                    else:
                        flash('Неподдерживаемый формат изображения. Используйте PNG, JPG, JPEG, GIF или WEBP.', 'warning')

                deadline = None
                if form.deadline.data:
                    deadline = datetime.combine(form.deadline.data, datetime.min.time())

                wish = Wish(
                    user_id=current_user.id,
                    title=form.title.data,
                    description=form.description.data,
                    wish_type=form.wish_type.data,
                    target_amount=form.target_amount.data,
                    unit_label=unit_label,
                    deadline=deadline,
                    is_public=form.is_public.data,
                    is_magic_slot_enabled=form.is_magic_slot_enabled.data,
                    icon_path=icon_path
                )

                db.session.add(wish)
                db.session.commit()

                # пересчет после создания
                if deadline:
                    wish.calculate_daily_target()
                wish.update_flower_stage()
                db.session.commit()

                flash('Желание успешно создано!', 'success')
                return redirect(url_for('main.index'))

            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при создании желания: {str(e)}', 'danger')
                print(f"Error creating wish: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Ошибка в поле {field}: {error}', 'danger')

    return render_template('wish/create.html', form=form)


@wish_bp.route('/<int:wish_id>')
@login_required
def detail(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id != current_user.id and not wish.is_public:
        flash('У вас нет доступа к этому желанию', 'danger')
        return redirect(url_for('main.index'))

    wish.calculate_growth()
    db.session.commit()

    daily_target = 0
    days_left = None
    if wish.deadline and not wish.is_completed:
        days_left = (wish.deadline - datetime.utcnow()).days
        if days_left > 0:
            daily_target = (wish.target_amount - wish.current_amount) / days_left

    contributions = wish.contributions.order_by(Contribution.created_at.desc()).limit(10).all()

    vote_count = wish.get_vote_count()
    contribution_form = ContributionForm()
    complete_form = CompleteWishForm()
    vote_form = VoteForm()
    vote_form.wish_id.data = str(wish.id)

    return render_template('wish/detail.html',
                         wish=wish,
                         contributions=contributions,
                         daily_target=daily_target,
                         days_remaining=days_left,
                         vote_count=vote_count,
                         is_owner=wish.user_id == current_user.id,
                         contribution_form=contribution_form,
                         complete_form=complete_form,
                         vote_form=vote_form)


@wish_bp.route('/<int:wish_id>/contribute', methods=['POST'])
@login_required
def contribute(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id != current_user.id:
        flash('Вы можете пополнять только свои желания', 'danger')
        return redirect(url_for('main.index'))

    if wish.is_completed:
        flash('Это желание уже исполнено!', 'info')
        return redirect(url_for('wish.detail', wish_id=wish.id))

    form = ContributionForm()
    if form.validate_on_submit():
        wish.add_contribution(form.amount.data, form.note.data)
        flash(f'Добавлено {form.amount.data} {wish.unit_label}!', 'success')

        if wish.is_completed:
            flash('Поздравляем! Желание исполнено!', 'success')
            return redirect(url_for('main.achievements'))

    return redirect(url_for('wish.detail', wish_id=wish.id))


@wish_bp.route('/<int:wish_id>/complete', methods=['POST'])
@login_required
def complete(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id != current_user.id:
        flash('Вы можете отмечать только свои желания', 'danger')
        return redirect(url_for('main.index'))

    if wish.is_completed:
        flash('Это желание уже исполнено', 'info')
        return redirect(url_for('wish.detail', wish_id=wish.id))

    form = CompleteWishForm()
    if form.validate_on_submit():
        wish.complete_wish()
        flash('Поздравляем! Желание исполнено и перенесено в галерею достижений!', 'success')
        return redirect(url_for('main.achievements'))

    return redirect(url_for('wish.detail', wish_id=wish.id))


@wish_bp.route('/<int:wish_id>/vote', methods=['POST'])
@login_required
def vote(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id == current_user.id:
        flash('Вы не можете голосовать за свои желания', 'warning')
        return redirect(url_for('wish.detail', wish_id=wish.id))

    vote_exists = Vote.query.filter_by(wish_id=wish_id, voter_id=current_user.id).first()
    if vote_exists:
        flash('Вы уже голосовали за это желание', 'info')
        return redirect(url_for('wish.detail', wish_id=wish.id))

    vote = Vote(wish_id=wish_id, voter_id=current_user.id)
    db.session.add(vote)
    db.session.commit()

    flash('Ваш голос учтен!', 'success')
    return redirect(url_for('wish.detail', wish_id=wish.id))


@wish_bp.route('/<int:wish_id>/delete', methods=['POST'])
@login_required
def delete(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id != current_user.id:
        flash('Вы можете удалять только свои желания', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(wish)
    db.session.commit()

    flash('Желание удалено', 'info')
    return redirect(url_for('main.index'))


@wish_bp.route('/magic-slot', methods=['GET', 'POST'])
@login_required
def magic_slot():
    form = MagicSlotForm()

    wishes = Wish.query.filter_by(
        user_id=current_user.id,
        is_completed=False,
        is_magic_slot_enabled=True
    ).all()

    if not wishes:
        flash('У вас нет активных желаний, участвующих в Магическом слоте. Создайте желание или включите опцию "Магический слот" в существующих.', 'warning')
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        amount = form.amount.data

        pick_wish = random.choice(wishes)

        spin = MagicSlotSession(
            user_id=current_user.id,
            amount=amount,
            target_wish_id=pick_wish.id
        )
        db.session.add(spin)

        pick_wish.add_contribution(amount, 'Магический слот', is_magic=True)

        flash(f'Монетка в {amount} {pick_wish.unit_label} упала в желание "{pick_wish.title}"!', 'success')
        return redirect(url_for('wish.detail', wish_id=pick_wish.id))

    return render_template('wish/magic_slot.html', form=form, wishes=wishes)


@wish_bp.route('/my')
@login_required
def my_wishes():
    active_wishes = Wish.query.filter_by(
        user_id=current_user.id,
        is_completed=False
    ).order_by(Wish.created_at.desc()).all()

    completed_wishes = Wish.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(Wish.completed_at.desc()).all()

    for wish in active_wishes:
        wish.calculate_growth()
    db.session.commit()

    return render_template('wish/my_wishes.html',
                         active_wishes=active_wishes,
                         completed_wishes=completed_wishes)


@wish_bp.route('/<int:wish_id>/toggle-public', methods=['POST'])
@login_required
def toggle_public(wish_id):
    wish = Wish.query.get_or_404(wish_id)

    if wish.user_id != current_user.id:
        flash('Вы можете изменять только свои желания', 'danger')
        return redirect(url_for('main.index'))

    wish.is_public = not wish.is_public
    db.session.commit()

    if wish.is_public:
        flash('Желание теперь публичное и видно в ленте', 'success')
    else:
        flash('Желание теперь приватное', 'info')

    return redirect(url_for('wish.detail', wish_id=wish.id))
