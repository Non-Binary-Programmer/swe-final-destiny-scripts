from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/batchedit')
def batch_staging():
    return render_template('batch.html')

@app.route('/batchedit', methods=["POST"])
def batch_accept():
    return redirect("/")

@app.route('/report')
def circulation_staging():
    return render_template('report.html')

@app.route('/report', methods=["POST"])
def circulation_accept():
    return redirect("/")

@app.route('/barcodes')
def barcode_staging():
    return render_template('barcodes.html')

@app.route('/barcodes', methods=["POST"])
def barcode_accept():
    return redirect("/")