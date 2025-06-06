from sys import maxsize
from flask import Flask, render_template, redirect, request, send_file
from xlsxwriter import Workbook
import pandas as pd
import numpy as np

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
    secondReport = request.files["secondReport"]
    mincircs = int(request.form.get("mincircs"))
    maxcircs = request.form.get("maxcircs")
    lostbooks = request.form.get("lostbooks")
    data = pd.read_excel(report, sheet_name=0)
    sort = request.form.get("sort")
    secondSort = request.form.get("secondSort")
    sortOrder = request.form.get("sortOrder")
    secondSortOrder = request.form.get("secondSortOrder")
    mindate = (request.form.get("mindate"))
    maxdate = (request.form.get("maxdate"))
    title = (request.form.get("title"))

    if (secondReport.read1()):
        moreData = pd.read_excel(secondReport, sheet_name=0)["Circs"]
        data.insert(loc=9, column="Recent Circs", value=moreData)

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

    if ("Year" in filtered.columns):
        filtered["Year"] = filtered["Year"].fillna(-1).astype(int).replace(-1, "")
    filtered["Date Acquired"] = filtered["Date Acquired"].dt.date
    filtered["Sublocation"] = filtered["Sublocation"].fillna("")
    filtered["Author"] = filtered["Author"].fillna("")
    filtered["Barcode"] = filtered["Barcode"].fillna("")
    
    if (sort not in filtered.columns or secondSort not in filtered.columns):
        raise RuntimeError
        return render_template("report template.html", table="", title="Error: tried to sort by data not provided.")
    filtered.sort_values(by=[sort, secondSort], inplace=True, ascending=[sortOrder == "ascending", secondSortOrder == "ascending"])
    
    return render_template("report template.html", table=filtered.to_html(index=False), title=title) 

@app.route('/barcodes')
def barcode_staging():
    return render_template('barcodes.html')

@app.route('/barcodes', methods=["POST"])
def barcode_accept():
    reportString = request.form.get("report")
    isUsed = reportString.split()[0] == "Used"
    availableNums = list()
    requiredNumbers = request.form.get("count", default=maxsize)
    end = int(request.form.get("end"))
    if end > 9999999:
        end = 9999999
    if requiredNumbers == "":
        requiredNumbers = maxsize
    else:
        requiredNumbers = int(requiredNumbers)
    if isUsed:
        availableNums.extend(range(int(request.form.get('start')), end))
    foundNums = 0
    for string in reportString.split('\n'):
        if not string.startswith('T'):
            continue
        if string.find('-') == -1:
            if isUsed:
                val = int(string.split()[1])
                if (int(string.split()[1]) in availableNums):
                    availableNums.remove(int(string.split()[1]))
                foundNums += 1
                if foundNums > requiredNumbers:
                    break
            else:
                availableNums.append(int(string.split()[1]))
        else:
            valueRange = range(int(string.split()[1]), int(string.split()[4]) + 1)
            if isUsed:
                for i in valueRange:
                    if (i in availableNums):
                        availableNums.remove(i)
                foundNums += len(valueRange)
                if foundNums > requiredNumbers:
                    break
            else:
                availableNums.extend(valueRange)
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