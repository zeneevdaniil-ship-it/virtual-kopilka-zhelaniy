from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SelectField, DateField, FileField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import datetime, timedelta

class RegistrationForm(FlaskForm):
    phone = StringField('Номер телефона', validators=[
        DataRequired(message='Введите номер телефона'),
        Length(min=10, max=20, message='Номер телефона должен содержать 10-20 символов')
    ])
    name = StringField('Ваше имя', validators=[
        DataRequired(message='Введите ваше имя'),
        Length(min=2, max=100, message='Имя должно содержать от 2 до 100 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    phone = StringField('Номер телефона', validators=[
        DataRequired(message='Введите номер телефона')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    submit = SubmitField('Войти')

class WishForm(FlaskForm):
    title = StringField('Название желания', validators=[
        DataRequired(message='Введите название желания'),
        Length(max=200)
    ])
    description = TextAreaField('Описание (опционально)', validators=[Optional()])

    wish_type = SelectField('Тип желания', choices=[
        ('money', 'Накопить деньги'),
        ('progress', 'Прогресс (км, страницы, часы)')
    ], validators=[DataRequired()])

    target_amount = FloatField('Целевая сумма / Количество', validators=[
        DataRequired(message='Введите целевую сумму'),
        NumberRange(min=1, message='Значение должно быть больше 0')
    ])

    unit_label = SelectField('Единица измерения', choices=[
        ('руб.', 'Рубли (руб.)'),
        ('$', 'Доллары ($)'),
        ('€', 'Евро (€)'),
        ('км', 'Километры (км)'),
        ('м', 'Метры (м)'),
        ('стр.', 'Страницы (стр.)'),
        ('книг', 'Книги (книг)'),
        ('час', 'Часы (час)'),
        ('мин', 'Минуты (мин)'),
        ('раз', 'Раз (раз)'),
        ('дней', 'Дней (дней)'),
        ('шт.', 'Штуки (шт.)'),
        ('другое', 'Другое (указать)')
    ], default='руб.')

    custom_unit = StringField('Своя единица', validators=[Optional(), Length(max=50)])

    deadline = DateField('Дедлайн (опционально)', validators=[Optional()], format='%Y-%m-%d')

    is_public = BooleanField('Публичное желание (видно в ленте)')
    is_magic_slot_enabled = BooleanField('Участвует в Магическом слоте', default=True)

    icon = FileField('Иконка желания (опционально)')

    submit = SubmitField('Создать желание')

class ContributionForm(FlaskForm):
    amount = FloatField('Сумма / Количество', validators=[
        DataRequired(message='Введите сумму'),
        NumberRange(min=0.01, message='Сумма должна быть больше 0')
    ])
    note = StringField('Примечание (опционально)', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Пополнить')

class MagicSlotForm(FlaskForm):
    amount = FloatField('Сумма для Магического слота', validators=[
        DataRequired(message='Введите сумму'),
        NumberRange(min=1, message='Сумма должна быть больше 0')
    ])
    submit = SubmitField('Кинуть монетку!')

class VoteForm(FlaskForm):
    wish_id = HiddenField('Wish ID', validators=[DataRequired()])
    submit = SubmitField('Голосовать')

class CompleteWishForm(FlaskForm):
    submit = SubmitField('Исполнено!')

class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    submit = SubmitField('Сохранить')

class ShareForm(FlaskForm):
    is_public = BooleanField('Сделать публичным')
    submit = SubmitField('Поделиться')
