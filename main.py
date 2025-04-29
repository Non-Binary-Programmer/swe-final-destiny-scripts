from sys import maxsize
from flask import Flask, render_template, redirect, request
import requests
import xlsxwriter

app = Flask(__name__)

if (__name__ == "__main__"):
    wb = xlsxwriter.Workbook("hello.xlsx")
    sheet = wb.add_worksheet()
    for i in range(0, 5):
        sheet.write(i, 0, i)
    wb.close()

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
    reportString = request.form.get("report")
    isUsed = reportString.split()[0] == "Used"
    availableNums = list()
    requiredNumbers = int(request.form.get("count", default=maxsize))
    if isUsed:
        availableNums.extend(range(int(request.form.get('start')), int(request.form.get('end'))))
    for string in reportString.split('\n'):
        if not string.startswith('T'):
            continue
        if string.find('-') == -1:
            if isUsed:
                availableNums.remove(int(string.split()[1]))
            else:
                availableNums.append(int(string.split()[1]))
                if (len(availableNums) > requiredNumbers):
                    break
        else:
            valueRange = range(int(string.split()[1]), int(string.split()[4]))
            if isUsed:
                for i in valueRange:
                    availableNums.remove(i)
            else:
                availableNums.extend(valueRange)
                if (len(availableNums) > requiredNumbers):
                    break
    if (len(availableNums) > requiredNumbers):
        availableNums = availableNums[:requiredNumbers]
    print(availableNums)
    return redirect("/")