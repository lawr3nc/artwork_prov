from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ArtPieceForm, AuctionForm, TransportForm, \
    PurchaserForm, DisplayArtForm, StoreArtForm, ActivityForm
from app.models import User
import requests
import json


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    form = ActivityForm()
    activity = form.activity.data

    if activity == 'new':
        return redirect(url_for('artpiece'))
    elif activity == 'submit':
        return redirect(url_for('auction'))
    elif activity == 'delivery':
        return redirect(url_for('transport'))
    elif activity == 'payment':
        return redirect(url_for('purchaser'))
    elif activity == 'store':
        return redirect(url_for('storage'))
    elif activity == 'display':
        return redirect(url_for('display'))
    return render_template('index.html', title='Activity', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


CONNECTED_NODE_ADDRESS = "http://127.0.0.1:5000"

transactions = []


def fetch_transactions():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global transactions
        transactions = sorted(content, key=lambda k: k['timestamp'], reverse=True)


@app.route('/artpiece', methods=['POST'])
@login_required
def art_transaction():
    """
    Endpoint to create a new transaction via our application.
    """
    form = ArtPieceForm()
    artname = form.artname.data
    artist = form.artist.data
    dateofcreation = form.dateofcreation.data
    location = form.location.data
    size = form.size.data
    weight = form.weight.data
    activity = form.activity.data

    transaction_object = {
        'artname': artname,
        'artist': artist,
        'dateofcreation': dateofcreation,
        'location': location,
        'size': size,
        'weight': weight,
        'activity': activity
    }

    # Submit a transaction
    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('artpiece.html', title='Art Piece', form=form)


@app.route('/auction', methods=['POST'])
@login_required
def auction_transaction():
    form = AuctionForm()
    consignorname = form.consignorname.data
    consignordob = form.consignordob.data
    consignorgender = form.consignorgender.data
    specialistname = form.specialistname.data
    auctionhouse = form.actionhouse.data
    specialistdob = form.specialistdob.data
    specialistgender = form.specialistgender.data
    activity = form.activity.data

    transaction_object = {
        'consignorname': consignorname,
        'consignordob': consignordob,
        'consignorgender': consignorgender,
        'specialistname': specialistname,
        'auctionhouse': auctionhouse,
        'specialistdob': specialistdob,
        'specialistgender': specialistgender,
        'activity': activity
    }

    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('auction.html', title='Auction', form=form)


@app.route('/transport', methods=['POST'])
@login_required
def transport_transaction():
    form = TransportForm()
    tranportername = form.tranportername.data
    deliveryco = form.deliveryco.data
    transportergender = form.transportergender.data
    transporterdob = form.transporterdob.data
    modeoftransport = form.modeoftransport.data
    trackingno = form.trackingno.data
    destination = form.destination.data
    vehicletemp = form.vehicletemp.data
    activity = form.activity.data

    transaction_object = {
        'transportername': tranportername,
        'deliveryco': deliveryco,
        'transportergender': transportergender,
        'transporterdob': transporterdob,
        'modeoftransport': modeoftransport,
        'trackingno': trackingno,
        'destination': destination,
        'vehicletemp': vehicletemp,
        'activity': activity
    }

    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('transport.html', title='Transport', form=form)


@app.route('/purchaser', methods=['POST'])
@login_required
def purchaser_transaction():
    form = PurchaserForm()
    purchasername = form.purchasername.data
    purchaserdob = form.purchaserdob.data
    purchasergender = form.purchasergender.data
    activity = form.activity.data

    transaction_object = {
        'purchasername':purchasername,
        'purchaserdob': purchaserdob,
        'purchasergender': purchasergender,
        'activity': activity
    }

    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('purchaser.html', title='Purchaser', form=form)


@app.route('/display', methods=['POST'])
@login_required
def display_transaction():
    form = DisplayArtForm()
    galleryname = form.galleryname.data
    gallerylocation = form.gallerylocation.data
    galleryowner = form.galleryowner.data
    displayroomtemp = form.displayroomtemp.data
    activity = form.activity.data

    transaction_object = {
        'galleryname': galleryname,
        'gallerylocation': gallerylocation,
        'galleryowner': galleryowner,
        'displayroomtemp': displayroomtemp,
        'activity': activity
    }

    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('display.html', title='Art Display', form=form)


@app.route('/storage', methods=['POST'])
@login_required
def storage_transaction():
    form = StoreArtForm()
    storagename = form.storagename.data
    storagelocation = form.storagelocation.data
    storagetemp = form.storagetemp.data
    activity = form.activity.data

    transaction_object = {
        'storagename': storagename,
        'storagelocation': storagelocation,
        'storagetemp': storagetemp,
        'activity': activity
    }

    new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return render_template('storage.html', title='Art Storage', form=form)


@app.route('/activity', methods=['POST'])
@login_required
def activity():
    form = ActivityForm()
    activity = form.activity.data

    if activity == 'new':
        return redirect(url_for('artpiece'))
    elif activity == 'submit':
        return redirect(url_for('auction'))
    elif activity == 'delivery':
        return redirect(url_for('transport'))
    elif activity == 'payment':
        return redirect(url_for('purchaser'))
    elif activity == 'store':
        return redirect(url_for('storage'))
    elif activity == 'display':
        return redirect(url_for('display'))
    return render_template('activity.html', title='Activity', form=form)


def timestamp_to_string(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%H:%M')


