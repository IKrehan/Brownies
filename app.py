from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/encomenda')
def encomenda():
    return render_template('encomenda.html')


if __name__ == "__main__":
    app.run(debug=True)