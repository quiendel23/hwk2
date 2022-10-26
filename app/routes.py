from app import app
from flask import render_template, redirect, url_for, current_app
from app import db
from app.models import Car
import sqlalchemy as sa
import sys
from app.forms import AddForm, SearchForm


@app.route('/init')
def initialize_db():
    connection_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = sa.create_engine(connection_uri)
    insp = sa.inspect(engine)

    # Create table only if it already doesn't exist
    if not insp.has_table("cars"):
        print('cars table does not exist.  Creating it.', file=sys.stdout)

        # Create the DB table
        db.create_all()

        # Iterate through the data file and add records to DB
        with current_app.open_resource('static/mpg.csv') as file:
            for row in file:
                # convert from bytes to string before manipulating
                toks = row.decode("utf-8").split(',')
                c = Car(name = toks[-1].strip(),
                        year = toks[-3],
                        origin = toks[-2],
                        mpg = toks[1])
                db.session.add(c)

        # Commit all the changes
        db.session.commit()

    return "Initialized DB"


@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    form = AddForm()
    if form.validate_on_submit():
        name = form.name.data
        year = form.year.data 
        origin = form.origin.data
        mpg = form.mpg.data
        c = Car(name, year, origin, mpg)
        db.session.add(c)
        db.session.commit()
        form.origin.data = ''
        form.mpg.data = ''
        form.year.data = ''
        form.name.data = ''
        return redirect(url_for('add_car'))
    return render_template('add_car.html',form = form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        name = form.name.data
        record = db.session.query(Car).filter(Car.name.contains(name))
        if record:
            return render_template('view_cars.html', cars=record)
        else:
            return render_template('not_found.html')
    return render_template('search.html', form=form)
        
@app.route('/sort_model')
def sort_by_model():
    all = db.session.query(Car).order_by(Car.name).all()
    print(all, file=sys.stderr)
    return render_template('view_cars.html', cars=all)

@app.route('/wipe')
def wipe():
    db.drop_all()
    return "Wiped data."

@app.route('/view_all')
def view():
    all = db.session.query(Car).all()
    return render_template('view_cars.html', cars=all)
