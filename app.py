import peeweedbevolve
from flask import Flask, flash, redirect, render_template, request, url_for
from models import *
import os

app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = os.getenv('APP_SECRET_KEY')


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.cli.command()
def migrate():
    db.evolve(ignore_tables={'base_model'})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/store-management", methods=["GET"])
def show_store_form():
    return render_template("store.html")


@app.route("/store-management", methods=["POST"])
def create_store():
    # Create a new store using the chosen name
    s = Store(name=request.form['name'])

    try:
        if s.save():
            flash("Successfully saved")
            return redirect(url_for('show_store_form'))

    except:
        return render_template("store.html")


@app.route("/stores")
def show_stores():
    # Selects all the stores in the db
    stores = Store.select()
    store_info = {}
    for store in stores:
        # Counts the number of warehouses belonging to the selected store
        store_info[store.name] = Warehouse.select().where(
            Warehouse.store_id == store.id).count()

    return render_template("stores.html", store_info=store_info)


@app.route("/stores", methods=["POST"])
def delete_store():
    # Get the id of the store to be deleted
    Store.delete().where()


@app.route("/stores/<store_id>")
def show_store(store_id):
    # Selects the store based on the ID provided
    store = Store.get_by_id(store_id)

    # Counts the number of warehouses belonging to the selected store
    count = Warehouse.select().where(Warehouse.store_id == int(store_id)).count()
    return render_template("store_page.html", store=store, count=count)


@app.route("/stores/<store_id>", methods=["POST"])
def update_store(store_id):
    u = Store.update(name=request.form.get('new-name')
                     ).where(Store.id == store_id)
    if u.execute():
        flash("Successfully")
    return redirect(url_for('show_store', store_id=store_id))


@app.route("/warehouse-management", methods=["GET"])
def show_warehouse_form():
    stores = Store.select()
    return render_template("warehouse.html", stores=stores)


@app.route("/warehouse-management", methods=["POST"])
def create_warehouse():
    # Get the chosen store by the user
    chosen_store = Store.get_by_id(request.form.get('store_id'))

    # Create a new warehouse using the chosen store
    w = Warehouse(location=request.form['location'], store=chosen_store)

    try:
        if w.save():
            flash("Successfully saved")
            return redirect(url_for('show_warehouse_form'))

    except Exception as exc:
        print(exc)
        return render_template("warehouse.html")


if __name__ == 'main':
    app.run()
