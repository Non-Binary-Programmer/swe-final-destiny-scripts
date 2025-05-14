from sys import maxsize
from flask import Flask, render_template, redirect, request, send_file
from xlsxwriter import Workbook
from pandas import read_excel
from numpy import datetime64, isnat

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if (__name__ == "__main__"):
    wb = Workbook("hello.xlsx")
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
    report = request.files["report"]
    mincircs = int(request.form.get("mincircs"))
    maxcircs = request.form.get("maxcircs")
    lostbooks = request.form.get("lostbooks")
    data = read_excel(report, sheet_name=0)
    sort = request.form.get("sort")
    secondSort = request.form.get("secondSort")
    sortOrder = request.form.get("sortOrder")
    secondSortOrder = request.form.get("secondSortOrder")
    mindate = (request.form.get("mindate"))
    maxdate = (request.form.get("maxdate"))
    filtered = data[mincircs <= data["Circs"]]
    try:
        filtered = filtered[filtered["Circs"] <= int(maxcircs)]
    except ValueError:
        pass
    try:
        filtered = filtered[filtered["Year"] >= int(mindate)]
    except ValueError:
        pass
    try:
        filtered = filtered[filtered["Year"] <= int(maxdate)]
    except ValueError:
        pass
    if lostbooks == "excluded":
        filtered = filtered[filtered["Status"] != "Lost"]
    elif lostbooks == "only":
        filtered = filtered[filtered["Status"] == "Lost"]
    filtered.sort_values(by=[sort, secondSort], inplace=True, ascending=[sortOrder == "ascending", secondSortOrder == "ascending"])
    return filtered.to_html(index=False)

@app.route('/barcodes')
def barcode_staging():
    return render_template('barcodes.html')

@app.route('/barcodes', methods=["POST"])
def barcode_accept():
    reportString = request.form.get("report")
    isUsed = reportString.split()[0] == "Used"
    availableNums = list()
    requiredNumbers = request.form.get("count", default=maxsize)
    if requiredNumbers == "":
        requiredNumbers = maxsize
    else:
        requiredNumbers = int(requiredNumbers)
    if isUsed:
        availableNums.extend(range(int(request.form.get('start')), int(request.form.get('end'))))
    for string in reportString.split('\n'):
        if not string.startswith('T'):
            continue
        if string.find('-') == -1:
            if isUsed:
                if (int(string.split()[1]) in availableNums):
                    availableNums.remove(int(string.split()[1]))
            else:
                availableNums.append(int(string.split()[1]))
                if (len(availableNums) > requiredNumbers):
                    break
        else:
            valueRange = range(int(string.split()[1]), int(string.split()[4]) + 1)
            if isUsed:
                for i in valueRange:
                    if (i in availableNums):
                        availableNums.remove(i)
            else:
                availableNums.extend(valueRange)
                if (len(availableNums) > requiredNumbers):
                    break
    if (len(availableNums) > requiredNumbers):
        availableNums = availableNums[:requiredNumbers]
    wb = Workbook('/tmp/barcodes.xlsx')
    worksheet = wb.add_worksheet("Copy Barcode Labels")
    worksheet.freeze_panes(1,0)
    bold = wb.add_format({'bold': True})
    worksheet.write(0, 0, "BarcodeNumber", bold)
    row = 1
    for i in availableNums:
        worksheet.write(row, 0, 'T ' + str(i))
        row += 1
    wb.close()
    return send_file('/tmp/barcodes.xlsx')