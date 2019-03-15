from datetime import datetime, date
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ArtPieceForm, AuctionForm, TransportForm, \
    SaleForm, DisplayArtForm, StoreArtForm, ActivityForm
from app.models import User
import requests
import json


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    transactions = fetch_transactions()
    form = ActivityForm()
    activity = form.activity.data
    if form.validate_on_submit():
        if activity == 'new':
            return redirect(url_for('art_transaction'))
        elif activity == 'submit':
            return redirect(url_for('auction_transaction'))
        elif activity == 'delivery':
            return redirect(url_for('transport_transaction'))
        elif activity == 'payment':
            return redirect(url_for('purchaser_transaction'))
        elif activity == 'store':
            return redirect(url_for('storage_transaction'))
        elif activity == 'display':
            return redirect(url_for('display_transaction'))
    return render_template('index.html', title='Home', node_address=CONNECTED_NODE_ADDRESS, form=form,
                           transactions=transactions)


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


@login_required
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
                content.append(tx)
        print(content)
        return sorted(content, key=lambda k: k['timestamp'], reverse=True)

def myconverter(o):
    if isinstance(o, date):
        return o.__str__()


@app.route('/art_transaction', methods=['GET', 'POST'])
@login_required
def art_transaction():
    form = ArtPieceForm()
    if form.validate_on_submit():
        artid = form.artid.default
        artname = form.artname.data
        arttype = form.arttype.data
        size = form.size.data
        weight = form.weight.data
        dateofcreation = form.dateofcreation.data
        location = form.location.data
        artistid = form.artistid.default
        artist = form.artist.data
        artistgender = form.artistgender.data
        artistdob = form.artistdob.data
        artistdod = form.artistdod.data
        if arttype == "painting":
            activity = "painting"
        elif arttype == "sculptor":
            activity = "sculpting"
        else:
            activity = "drawing"

        transaction_object = {
            'artid': artid,
            'artname': artname,
            'arttype': arttype,
            'artist': artist,
            'dateofcreation': myconverter(dateofcreation),
            'location': location,
            'size': size,
            'weight': weight,
            'artistid': artistid,
            'artistgender': artistgender,
            'artistdob': myconverter(artistdob),
            'artistdod': myconverter(artistdod),
            'activity': activity
        }

        # Submit a transaction
        new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)
        requests.post(new_tx_address,
                      json=transaction_object,
                      headers={'Content-type': 'application/json'})
        return redirect(url_for('index'))
    flash("There's an error in the form. Form was not submitted")
    return render_template('artpiece.html', title='Art Piece', form=form)


@app.route('/auction_transaction', methods=['GET', 'POST'])
@login_required
def auction_transaction():
    form = AuctionForm()
    if form.validate_on_submit():
        consignorid = form.consignorid.default
        consignorname = form.consignorname.data
        consignordob = form.consignordob.data
        consignorgender = form.consignorgender.data
        artid = form.artid.default
        artname = form.artname.data
        location = form.location.data
        reserve = form.reserve.data
        activity = "submit"

        transaction_object = {
            'consignorid': consignorid,
            'consignorname': consignorname,
            'consignordob': myconverter(consignordob),
            'consignorgender': consignorgender,
            'artid': artid,
            'artname': artname,
            'location': location,
            'reserve': reserve,
            'activity': activity
        }

        new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=transaction_object,
                      headers={'Content-type': 'application/json'})
        return redirect(url_for('index'))
    return render_template('auction.html', title='Auction', form=form)


@app.route('/transport_transaction', methods=['GET', 'POST'])
@login_required
def transport_transaction():
    form = TransportForm()
    if form.validate_on_submit():
        transporterid = form.transporterid.default
        transportername = form.tranportername.data
        deliveryco = form.deliveryco.data
        transportergender = form.transportergender.data
        transporterdob = form.transporterdob.data
        modeoftransport = form.modeoftransport.data
        trackingno = form.trackingno.default
        destination = form.destination.data
        vehicletemp = form.vehicletemp.data
        artid = form.artid.default
        artname = form.artname.data
        activity = "deliver"

        transaction_object = {
            'transporterid': transporterid,
            'transportername': transportername,
            'deliveryco': deliveryco,
            'transportergender': transportergender,
            'transporterdob': myconverter(transporterdob),
            'modeoftransport': modeoftransport,
            'trackingno': trackingno,
            'destination': destination,
            'vehicletemp': vehicletemp,
            'activity': activity,
            'artid': artid,
            'artname': artname
        }

        new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=transaction_object,
                      headers={'Content-type': 'application/json'})
        return redirect(url_for('index'))
    return render_template('transport.html', title='Transport', form=form)


@app.route('/purchaser_transaction', methods=['GET', 'POST'])
@login_required
def purchaser_transaction():
    form = SaleForm()
    if form.validate_on_submit():
        artid = form.artid.default
        artname = form.artname.data
        hammerprice = form.hammerprice.data
        buyerspremium = form.buyerspremium.data
        auctionhouse = form.auctionhouse.data
        specialistid = form.specialistid.default
        specialistname = form.specialistname.data
        specialistdob = form.specialistdob.data
        specialistgender = form.specialistgender.data
        purchaserid = form.purchaserid.default
        purchasername = form.purchasername.data
        purchaserdob = form.purchaserdob.data
        purchasergender = form.purchasergender.data
        activity = "purchase"

        transaction_object = {
            'artid': artid,
            'artname': artname,
            'hammerprice': hammerprice,
            'buyerspremium': buyerspremium,
            'amountpaid': hammerprice + (hammerprice * (buyerspremium/100)),
            'auctionhouse': auctionhouse,
            'specialistid': specialistid,
            'specialistname': specialistname,
            'specialistdob': myconverter(specialistdob),
            'specialistgender': specialistgender,
            'purchaserid': purchaserid,
            'purchasername': purchasername,
            'purchaserdob': myconverter(purchaserdob),
            'purchasergender': purchasergender,
            'activity': activity
        }

        new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=transaction_object,
                      headers={'Content-type': 'application/json'})
        return redirect(url_for('index'))
    return render_template('purchaser.html', title='Purchaser', form=form)


@app.route('/display_transaction', methods=['GET', 'POST'])
@login_required
def display_transaction():
    form = DisplayArtForm()
    if form.validate_on_submit():
        artid = form.artid.default
        artname = form.artname.data
        galleryname = form.galleryname.data
        gallerylocation = form.gallerylocation.data
        galleryowner = form.galleryowner.data
        displayroomtemp = form.displayroomtemp.data
        activity = "display"

        transaction_object = {
            'artid': artid,
            'artname': artname,
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
        return redirect(url_for('index'))
    return render_template('display.html', title='Art Display', form=form)


@app.route('/storage_transaction', methods=['GET', 'POST'])
@login_required
def storage_transaction():
    form = StoreArtForm()
    if form.validate_on_submit():
        artid = form.artid.default
        artname = form.artname.data
        storagename = form.storagename.data
        storagelocation = form.storagelocation.data
        storagetemp = form.storagetemp.data
        activity = "store"

        transaction_object = {
            'artid': artid,
            'artname': artname,
            'storagename': storagename,
            'storagelocation': storagelocation,
            'storagetemp': storagetemp,
            'activity': activity
        }

        new_tx_address = "{}/newtransaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                      json=transaction_object,
                      headers={'Content-type': 'application/json'})
        return redirect(url_for('index'))
    return render_template('storage.html', title='Art Storage', form=form)


def timestamp_to_string(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%H:%M')

