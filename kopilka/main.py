from flask import Flask, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('landing.html', day=1)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
