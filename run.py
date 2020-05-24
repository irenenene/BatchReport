from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
from io import StringIO
from werkzeug.wrappers import Response

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thequickbrownfoxjumpedoverthelazydog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@35.230.17.75/finalproj'
db = SQLAlchemy(app)


class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    batches = db.relationship('Batch', backref='operator', lazy=True)
    isActive = db.Column(db.Boolean, default=True)

    def __init__(self, fname, lname, email):
        self.firstName = fname
        self.lastName = lname
        self.email = email
        self.isActive = True


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerName = db.Column(db.String(50), nullable=False)
    primaryAddress = db.Column(db.String(100), nullable=False)
    contactEmail = db.Column(db.String(30), nullable=False)
    batches = db.relationship('Batch', backref='customer', lazy=True)
    isActive = db.Column(db.Boolean, default=True)

    def __init__(self, customerName, primaryAddress, contactEmail):
        self.customerName = customerName
        self.primaryAddress = primaryAddress
        self.contactEmail = contactEmail
        self.isActive = True


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workstationName = db.Column(db.String(20), nullable=False)
    batchType = db.Column(db.String(10), nullable=False)
    receivedTime = db.Column(db.DateTime, nullable=False)
    createdTime = db.Column(db.DateTime, nullable=False)
    releasedTime = db.Column(db.DateTime, nullable=False)
    operatorId = db.Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    customerId = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    docCount = db.Column(db.Integer, nullable=False)
    isDeleted = db.Column(db.Boolean, default=False)

    def __init__(self, workstationName, batchType, receivedTime, createdTime,\
                    releasedTime, operatorId, customerId, docCount):
        self.workstationName = workstationName
        self.batchType = batchType
        self.receivedTime = receivedTime
        self.createdTime = createdTime
        self.releasedTime = releasedTime
        self.operatorId = operatorId
        self.customerId = customerId
        self.docCount = docCount
        self.isDeleted = False


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    currDate = datetime.today().strftime("%Y-%m-%d")
    query = 'SELECT CONCAT(firstName, \' \', lastName) as Operator'\
            ' FROM operator'\
            ' WHERE id IN (SELECT DISTINCT operatorId FROM batch '\
                            ' WHERE releasedTime LIKE \'%' + currDate + '%\')'
    records = db.session.execute(query)

    return render_template('home.html', title='Home', records=records)

# Begin Operator Section ------------------------------------------------------

@app.route('/operators', methods=['GET', 'POST'])
def operators():
    ops = Operator.query.all()
    return render_template('operators.html', title='Operators', ops=ops)


@app.route('/operators/add', methods=['POST'])
def add_operator():
    if request.method == 'POST':
        fname = request.form['FirstName']
        lname = request.form['LastName']
        email = request.form['Email']

        new_op = Operator(fname, lname, email)
        db.session.add(new_op)
        db.session.commit()

        flash('Operator Added', 'success')

        return redirect(url_for('operators'))


@app.route('/operators/edit', methods=['GET','POST'])
def edit_operator():
    if request.method == 'POST':
        record = Operator.query.get(request.form.get('ID'))
        record.firstName = request.form['FirstName']
        record.lastName = request.form['LastName']
        record.email = request.form['Email']

        db.session.commit()

        flash('Operator ID ' +  request.form['ID'] + ' Updated', 'success')
        return redirect(url_for('operators'))


@app.route('/operators/delete/<idnum>', methods=['GET','POST'])
def delete_operator(idnum):
    if request.method == 'POST':
        record = Operator.query.get(idnum)
        db.session.delete(record)
        db.session.commit()

        flash('Operator ID ' + idnum + ' Deleted', 'success')
        return redirect(url_for('operators'))

# End Operator Section --------------------------------------------------------
# Begin Customer Section ------------------------------------------------------

@app.route('/customers', methods=['GET'])
def customers():
    cust = Customer.query.all()
    return render_template('customers.html', title='Customers', customers=cust)


@app.route('/customers/add', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        cname = request.form['CustomerName']
        paddress = request.form['PrimaryAddress']
        cemail = request.form['ContactEmail']

        new_cust = Customer(cname, paddress, cemail)
        db.session.add(new_cust)
        db.session.commit()

        flash('Customer Added', 'success')
        return redirect(url_for('customers'))


@app.route('/customers/edit', methods=['GET','POST'])
def edit_customer():
    if request.method == 'POST':
        record = Customer.query.get(request.form.get('ID'))
        record.customerName = request.form['CustomerName']
        record.primaryAddress = request.form['PrimaryAddress']
        record.contactEmail = request.form['ContactEmail']
        db.session.commit()

        flash('Customer ID ' +  request.form['ID'] + ' Updated', 'success')
        return redirect(url_for('customers'))


@app.route('/customers/delete/<idnum>', methods=['GET','POST'])
def delete_customer(idnum):
    if request.method == 'POST':
        record = Customer.query.get(idnum)
        db.session.delete(record)
        db.session.commit()

        flash('Customer ID ' + idnum + ' Deleted', 'success')
        return redirect(url_for('customers'))

# End Customer Section ---------------------------------------------------------
# Begin Batch Section ----------------------------------------------------------

@app.route('/batches', methods=['GET'])
def batches():
    b = Batch.query.all()
    o = Operator.query.all()
    c = Customer.query.all()
    k = Batch.__table__.columns.keys()
    defaultDate = datetime.today().strftime("%Y-%m-%d")
    return render_template('batches.html', title='Batches', batches=b, ops=o, custs=c, date=defaultDate, cols=k)


@app.route('/batches/filter', methods=['GET', 'POST'])
def filter_batches():
    searchCategory = request.form["Category"]
    searchValue = request.form["SearchValue"]
    # add additioinal query to perform exact match if searching the doc count field
    b = Batch.query.filter(getattr(Batch, searchCategory).like("%" + searchValue + "%")).all()
    o = Operator.query.all()
    c = Customer.query.all()
    k = Batch.__table__.columns.keys()
    defaultDate = datetime.today().strftime("%Y-%m-%d")
    return render_template('batches.html', title='Batches', batches=b, ops=o, custs=c, date=defaultDate, cols=k)


@app.route('/batches/add', methods=['POST'])
def add_batch():
    if request.method == 'POST':
        ws = request.form['Workstation']
        bt = request.form['BatchType']
        op = request.form['Operator']
        cs = request.form['Customer']
        received = request.form['ReceivedTime']
        created = request.form['CreatedTime']
        release = request.form['ReleasedTime']
        c = request.form['DocumentCount']
        # conversions back from string to datetime
        dtReceived = datetime.strptime(str(received),"%Y-%m-%dT%H:%M")
        dtCreated = datetime.strptime(str(created),"%Y-%m-%dT%H:%M")
        dtReleased = datetime.strptime(str(release),"%Y-%m-%dT%H:%M")

        new_batch = Batch(ws, bt, dtReceived, dtCreated, dtReleased, op, cs, c)
        db.session.add(new_batch)
        db.session.commit()

        flash('Batch Added', 'success')
        return redirect(url_for('batches'))

@app.route('/batches/edit', methods=['POST', 'GET'])
def edit_batch():
    if request.method == 'POST':
        record = Batch.query.get(request.form['ID'])
        record.workstationName = request.form['Workstation']
        record.batchType = request.form['BatchType']
        record.operatorId = request.form['Operator']
        record.customerId = request.form['Customer']
        received = request.form['ReceivedTime']
        created = request.form['CreatedTime']
        release = request.form['ReleasedTime']
        record.docCount = request.form['DocumentCount']
        # conversions back from string to datetime
        record.receivedTime = datetime.strptime(str(received),"%Y-%m-%dT%H:%M")
        record.createdTime = datetime.strptime(str(created),"%Y-%m-%dT%H:%M")
        record.releasedTime = datetime.strptime(str(release),"%Y-%m-%dT%H:%M")

        db.session.commit()
        flash('Batch ID ' + request.form['ID'] + ' Updated', 'success')
        return redirect(url_for('batches'))


@app.route('/batches/delete/<idnum>', methods=['POST', 'GET'])
def delete_batch(idnum):
    if request.method == 'POST':
        record = Batch.query.get(idnum)
        db.session.delete(record)
        db.session.commit()
        #record.isActive = 'False'

        flash('Batch ID ' + idnum + ' Deleted', 'success')
        return redirect(url_for('batches'))

# End Batch Section ------------------------------------------------------------
# Begin Report Section ---------------------------------------------------------

@app.route('/customerreports', methods=['GET', 'POST'])
def customer_reports():
    formDate = datetime.today().strftime("%Y-%m-%d")
    formMonth = datetime.today().strftime("%Y-%m")

    if request.method == 'POST':
        formDate = request.form["ReleaseDate"]
        formMonth = request.form["ReleaseMonth"]

    dateQuery = 'SELECT customerName as Customer,'\
                ' IFNULL((SELECT SUM(docCount) FROM batch b WHERE b.customerId=A.id and'\
                ' DATE_FORMAT(b.releasedTime, \'%Y-%m-%d\') = \''\
                + formDate + '\'),0) as Total FROM customer A'
    dailyTotals = db.session.execute(dateQuery)
    monthQuery = 'SELECT customerName as Customer,'\
                ' IFNULL((SELECT SUM(docCount) FROM batch b WHERE b.customerId=A.id and'\
                ' DATE_FORMAT(b.releasedTime, \'%Y-%m\') = \''\
                + formMonth + '\'),0) as Total FROM customer A'
    monthlyTotals = db.session.execute(monthQuery)

    return render_template('customer_reports.html',
                            title='Customer Reports',
                            dateString=formDate,
                            monthString=formMonth,
                            dailyTotals=dailyTotals,
                            monthlyTotals=monthlyTotals)


@app.route('/operatorreports', methods=['GET', 'POST'])
def operator_reports():
    formDate = datetime.today().strftime("%Y-%m-%d")
    formMonth = datetime.today().strftime("%Y-%m")

    if request.method == 'POST':
        formDate = request.form["ReleaseDate"]
        formMonth = request.form["ReleaseMonth"]

    dateQuery = 'SELECT CONCAT(firstName, \' \', lastName) as Operator,'\
                ' IFNULL((SELECT SUM(docCount) FROM batch b WHERE b.operatorId=A.id and'\
                ' DATE_FORMAT(b.releasedTime, \'%Y-%m-%d\') = \''\
                + formDate + '\'),0) as Total FROM operator A'
    dailyTotals = db.session.execute(dateQuery)
    monthQuery = 'SELECT CONCAT(firstName, \' \', lastName) as Operator,'\
                ' IFNULL((SELECT SUM(docCount) FROM batch b WHERE b.operatorId=A.id and'\
                ' DATE_FORMAT(b.releasedTime, \'%Y-%m\') = \''\
                + formMonth + '\'),0) as Total FROM operator A'
    monthlyTotals = db.session.execute(monthQuery)

    return render_template('operator_reports.html',
                            title='Operator Reports',
                            dateString=formDate,
                            monthString=formMonth,
                            dailyTotals=dailyTotals,
                            monthlyTotals=monthlyTotals)


@app.route('/exports')
def exports():

    return render_template('exports.html', title='Export')


# download_full will export the batch table with joined info from operators and customers
@app.route('/exports/allbatches', methods=['GET', 'POST'])
def download_full():
    def generate():
        query = ( 'SELECT batch.id, batchType, customerName, CONCAT(firstName, \' \', lastName) as operatorName, receivedTime, createdTime, releasedTime, docCount, workstationName'
                    ' FROM batch JOIN customer ON customer.id = batch.customerId JOIN operator ON batch.operatorId=operator.id'
                    ' ORDER BY batch.id')

        dictList = []
        colNames = db.session.execute(query + ' LIMIT 1').keys()
        rows = db.session.execute(query)

        for item in rows:
            dict = {}
            for col in colNames:
                dict[col] = item[col]
            dictList.append(dict)

        print(dictList)

        data = StringIO()
        writer = csv.DictWriter(data, colNames)
        writer.writeheader()
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for dict in dictList:
            writer.writerow(dict)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="log.csv")
    return response


@app.route('/times', methods=['GET'])
def get_times():
    query = 'SELECT batch.Id,'\
            ' CONCAT(firstname, \' \', lastName) as Operator,'\
            ' customer.customerName,'\
            ' receivedTime,'\
            ' releasedTime,'\
            ' Hour(TIMEDIFF(releasedTime, receivedtime)) as Hours'\
            ' FROM batch JOIN operator ON batch.operatorId = operator.Id'\
            ' JOIN customer ON batch.customerId = customer.Id'\
            ' ORDER BY customer.customerName'
    records = db.session.execute(query)

    return render_template('times.html', title='Times', records=records)


# End Report Section -----------------------------------------------------------
# Begin Search Section ---------------------------------------------------------



if __name__ == "__main__":
    app.run(debug=True)
