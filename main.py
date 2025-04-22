from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/batchedit')
def batch_staging():
    return render_template('batch.html')

@app.route('/batchedit', methods=["GET", "POST"])
def batch_accept():
    return redirect("/")