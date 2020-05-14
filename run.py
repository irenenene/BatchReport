from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thequickbrownfoxjumpedoverthelazydog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@35.230.17.75/finalproj'
db = SQLAlchemy(app)

# rename and recreate this table later?
class Operators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(20))
    lastName = db.Column(db.String(20))
    email = db.Column(db.String(30))
    batches = db.relationship('Batch', backref='operator', lazy=True)

    def __init__(self, fname, lname, email):
        self.firstName = fname
        self.lastName = lname
        self.email = email


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerName = db.Column(db.String(50))
    primaryAddress = db.Column(db.String(100))
    contactEmail = db.Column(db.String(30))
    batches = db.relationship('Batch', backref='customer', lazy=True)

    def __init__(self, customerName, primaryAddress, contactEmail):
        self.customerName = customerName
        self.primaryAddress = primaryAddress
        self.contactEmail = contactEmail

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workstationName = db.Column(db.String(20), nullable=False)
    batchType = db.Column(db.String(10), nullable=False)
    receivedTime = db.Column(db.DateTime, nullable=False)
    createdTime = db.Column(db.DateTime, nullable=False)
    releasedTime = db.Column(db.DateTime, nullable=False)
    isPaper = db.Column(db.Boolean, default=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

# START HERE ------------------------------------------------------------------
# Do the constructor next, then make sure to migrate / delete & recreate tables



@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

# Operator Section ------------------------------------------------------------

@app.route('/operators', methods=['GET', 'POST'])
def operators():
    ops = Operators.query.all()
    return render_template('operators.html', title='Operators', ops=ops)


@app.route('/operators/add', methods=['POST'])
def add_operator():
    if request.method == 'POST':
        fname = request.form['FirstName']
        lname = request.form['LastName']
        email = request.form['Email']

        new_op = Operators(fname, lname, email)
        db.session.add(new_op)
        db.session.commit()

        flash('Operator Added', 'success')

        return redirect(url_for('operators'))


@app.route('/operators/edit', methods=['GET','POST'])
def edit_operator():
    if request.method == 'POST':
        record = Operators.query.get(request.form.get('ID'))
        record.firstName = request.form['FirstName']
        record.lastName = request.form['LastName']
        record.email = request.form['Email']

        db.session.commit()

        flash('Operator ID ' +  request.form['ID'] + ' Updated', 'success')
        return redirect(url_for('operators'))


@app.route('/operators/delete/<idnum>', methods=['GET','POST'])
def delete_operator(idnum):
    if request.method == 'POST':
        record = Operators.query.get(idnum)
        db.session.delete(record)
        db.session.commit()

        flash('Operator ID ' + idnum + ' Deleted', 'success')
        return redirect(url_for('operators'))

# End Operator Section --------------------------------------------------------
# Customer Section ------------------------------------------------------------

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

# End Customer Section --------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
