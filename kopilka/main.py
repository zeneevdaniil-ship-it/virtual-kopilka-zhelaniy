from flask import Flask, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('landing.html', day=7)

@app.route('/about')
def about():
    return 'Страница о проекте WishBox'

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', day=7)

@app.route('/auth/login')
def login():
    return 'Форма входа'

@app.route('/auth/register')
def register():
    return 'Форма регистрации'

@app.route('/wish/create')
def wish_create():
    return 'Создание желания'

@app.route('/wish/my')
def my_wishes():
    return 'Мои желания'

if __name__ == '__main__':
    app.run(debug=True, port=8080)
