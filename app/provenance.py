import prov.model as prov
from provstore.api import Api
from app import db
from app.models import ArtID
import json
import requests
import uuid


class Provenance:
    document = prov.ProvDocument()
    document.add_namespace('art', 'http://art.com/')
    document.add_namespace('auction', 'http://auction.com/')
    document.add_namespace('transport', 'http://transport.com/')
    document.add_namespace('gallery', 'http://gallery.com/')


api = Api(base_url='https://openprovenance.org/store/api/v0', username="kym3ni",
          api_key="ef2cff88eb50f915a5fd6653e19392b355ca5c0a")
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:5000"
pendingtransactions_address = "{}/pendingtransactions".format(CONNECTED_NODE_ADDRESS)
minedtransactions_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
derivedentities = {}


def new_art():
    newprov = Provenance()
    response = requests.get(pendingtransactions_address)
    if response.status_code == 200:
        transaction = json.loads(response.content)
        labels = transaction[0]

        docdb = ArtID.query.filter_by(artname=labels['artname']).first()
        if docdb is None:
            prevart = newprov.document.entity('art:'+labels['artid'], {
                'art:name': labels['artname'],
                'art:type': labels['arttype'],
                'art:dateofcreation': labels['dateofcreation'],
                'art:location': labels['location'],
                'art:size': labels['size'],
                'art:weight': labels['weight']
            })
            newprov.document.activity('art:'+labels['activity'])
            newprov.document.agent('art:'+labels['artistid'], {
                prov.PROV_TYPE: 'prov:Person',
                'art:artist': labels['artist'],
                'art:gender': labels['artistgender'],
                'art:dateofbirth': labels['artistdob'],
                'art:dateofdeath': labels['artistdod']
            })
            newprov.document.wasAssociatedWith('art:'+labels['activity'], 'art:'+labels['artistid'])
            newprov.document.wasAttributedTo(prevart, 'art:'+labels['artistid'])
            newprov.document.wasGeneratedBy(prevart, 'art:'+labels['activity'])
            derivedentities[labels['artname']] = prevart
            doc = api.document.create(newprov.document, name=labels['artname'], public=True)
            newart = ArtID(artname=labels['artname'], docid=doc.id)
            db.session.add(newart)
            db.session.commit()
        else:
            print("Artwork is already registered")


def auction():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        chain = json.loads(minedtx.content)
        labels = transaction[0]

        for block in chain["chain"]:
            for tx in block["transactions"]:
                if tx['artname'] == labels['artname']:
                    docdb = ArtID.query.filter_by(artname=labels['artname']).first()
                    break
        retrieved_document = api.document.get(docdb.docid)
        retdoc = retrieved_document.prov

        latestart = derivedentities.get(labels['artname'])
        prevart = retdoc.entity('art:'+labels['artid'], {
            'art:name:': labels['artname'],
            'art:location': labels['location'],
            'art:reserve': labels['reserve'],
        })
        retdoc.activity('auction:'+labels['activity'])
        retdoc.agent('auction:'+labels['consignorid'], {
            prov.PROV_TYPE: 'prov:Person',
            'auction:consignorname': labels['consignorname'],
            'auction:consignorgender': labels['consignorgender'],
            'auction:consignordob': labels['consignordob']
        })
        retdoc.wasAssociatedWith('auction:'+labels['activity'], 'auction:'+labels['consignorid'])
        retdoc.wasAttributedTo(prevart, 'auction:'+labels['consignorid'])
        retdoc.wasGeneratedBy(prevart, 'auction:'+labels['activity'])
        retdoc.wasDerivedFrom(prevart, latestart)
        retdoc.used('auction:'+labels['activity'], latestart)
        derivedentities[labels['artname']] = prevart
        doc = api.document.create(retdoc, name=labels['artname'], public=True)
        docdb.docid = doc.id
        db.session.commit()


def transport():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        chain = json.loads(minedtx.content)
        labels = transaction[0]

        for block in chain["chain"]:
            for tx in block["transactions"]:
                if tx['artname'] == labels['artname']:
                    docdb = ArtID.query.filter_by(artname=labels['artname']).first()
                    break
        retrieved_document = api.document.get(docdb.docid)
        retdoc = retrieved_document.prov

        latestart = derivedentities.get(labels['artname'])
        prevart = retdoc.entity('art:'+labels['artid'], {'art:name': labels['artname']})
        retdoc.activity('transport:'+labels['activity'], None, None, {
            'transport:modeoftransport': labels['modeoftransport'],
            'transport:trackingno': labels['trackingno'],
            'transport:destination': labels['destination'],
            'transport:vehicletemp': labels['vehicletemp'],
            'transport:deliveryco': labels['deliveryco']
        })
        retdoc.agent('transport:'+labels['transporterid'], {
            'transport:transportername': labels['transportername'],
            'transport:transportergender': labels['transportergender'],
            'transport:transporterdob': labels['transporterdob']
        })
        retdoc.wasAssociatedWith('transport:' + labels['activity'], 'transport:' + labels['transporterid'])
        retdoc.wasAttributedTo(prevart, 'transport:' + labels['transporterid'])
        retdoc.wasGeneratedBy(prevart, 'transport:' + labels['activity'])
        retdoc.wasDerivedFrom(prevart, latestart)
        retdoc.used('transport:' + labels['activity'], latestart)
        derivedentities[labels['artname']] = prevart
        doc = api.document.create(retdoc, name=labels['artname'], public=True)
        docdb.docid = doc.id
        db.session.commit()


def purchase():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        chain = json.loads(minedtx.content)
        labels = transaction[0]

        for block in chain["chain"]:
            for tx in block["transactions"]:
                if tx['artname'] == labels['artname']:
                    docdb = ArtID.query.filter_by(artname=labels['artname']).first()
                    break
        retrieved_document = api.document.get(docdb.docid)
        retdoc = retrieved_document.prov

        auctionartid = str(uuid.uuid4())[:7]
        latestart = derivedentities.get(labels['artname'])
        retdoc.entity('art:'+auctionartid, {
            'art:name': labels['artname'],
            'auction:buyerspremium': labels['buyerspremium'],
            'auction: amountpaid': labels['amountpaid']
        })
        prevart = retdoc.entity('art:'+labels['artid'], {
            'art:name': labels['artname'],
            'auction:hammerprice': labels['hammerprice']
        })
        retdoc.activity('auction:auctionpreparation')
        retdoc.activity('auction:'+labels['activity'], None, None, {
            'auction:saledate': labels['saledate']
        })
        retdoc.agent('auction:'+labels['specialistid'], {
            'auction:specialistname': labels['specialistname'],
            'auction:specialistdob': labels['specialistdob'],
            'auction:specialistgender': labels['specialistgender'],
            'auction:auctionhouse': labels['auctionhouse']
        })
        retdoc.agent('auction:' + labels['purchaserid'], {
            'auction:purchasername': labels['purchasername'],
            'auction:purchaserdob': labels['purchaserdob'],
            'auction:purchasergender': labels['purchasergender']
        })
        retdoc.wasAttributedTo('art:'+auctionartid, 'auction:'+labels['specialistid'])
        retdoc.wasAttributedTo(prevart, 'auction:'+labels['purchaserid'])
        retdoc.wasAssociatedWith('auction:auctionpreparation', 'auction:'+labels['specialistid'])
        retdoc.wasAssociatedWith('auction:'+labels['activity'], 'auction:'+labels['purchaserid'])
        retdoc.wasGeneratedBy('art:'+auctionartid, 'auction:auctionpreparation')
        retdoc.wasGeneratedBy(prevart, 'auction:'+labels['activity'])
        retdoc.used('auction:'+labels['activity'], 'art:'+auctionartid)
        retdoc.used('auction:auctionpreparation', latestart)
        retdoc.wasDerivedFrom('art:'+labels['artid'], 'art:'+auctionartid)
        retdoc.wasDerivedFrom('art:'+auctionartid, latestart)
        derivedentities[labels['artname']] = prevart
        doc = api.document.create(retdoc, name=labels['artname'], public=True)
        docdb.docid = doc.id
        db.session.commit()


def display():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        chain = json.loads(minedtx.content)
        labels = transaction[0]

        for block in chain["chain"]:
            for tx in block["transactions"]:
                if tx['artname'] == labels['artname']:
                    docdb = ArtID.query.filter_by(artname=labels['artname']).first()
                    break
        retrieved_document = api.document.get(docdb.docid)
        retdoc = retrieved_document.prov

        galleryid = str(uuid.uuid4())[:7]
        latestart = derivedentities.get(labels['artname'])
        prevart = retdoc.entity('art:'+labels['artid'], {'art:name': labels['artname']})

        retdoc.activity('gallery:'+labels['activity'], None,  None,
                        {'gallery:displayroomtemp': labels['displayroomtemp']})
        retdoc.agent('gallery:'+galleryid, {
            'gallery:name': labels['galleryname'],
            'gallery:location': labels['gallerylocation'],
            'gallery:owner': labels['galleryowner']
        })
        retdoc.wasAssociatedWith('gallery:'+labels['activity'], 'gallery:'+galleryid)
        retdoc.wasAttributedTo(prevart, 'gallery:'+galleryid)
        retdoc.wasGeneratedBy(prevart, 'gallery:'+labels['activity'])
        retdoc.wasDerivedFrom(prevart, latestart)
        retdoc.used('gallery:'+labels['activity'], latestart)
        derivedentities[labels['artname']] = prevart
        doc = api.document.create(retdoc, name=labels['artname'], public=True)
        docdb.docid = doc.id
        db.session.commit()


def storage():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        chain = json.loads(minedtx.content)
        labels = transaction[0]

        for block in chain["chain"]:
            for tx in block["transactions"]:
                if tx['artname'] == labels['artname']:
                    docdb = ArtID.query.filter_by(artname=labels['artname']).first()
                    break
        retrieved_document = api.document.get(docdb.docid)
        retdoc = retrieved_document.prov

        storageid = str(uuid.uuid4())[:7]
        latestart = derivedentities.get(labels['artname'])
        prevart = retdoc.entity('art:' + labels['artid'], {'art:name': labels['artname']})
        retdoc.activity('gallery:' + labels['activity'], None, None,
                        {'gallery:storagetemp': labels['storagetemp']})
        retdoc.agent('gallery:' + storageid, {
            'gallery:name': labels['storagename'],
            'gallery:location': labels['storagelocation']
        })
        retdoc.wasAssociatedWith('gallery:'+labels['activity'], 'gallery:'+storageid)
        retdoc.wasAttributedTo(prevart, 'gallery:'+storageid)
        retdoc.wasGeneratedBy(prevart, 'gallery:'+labels['activity'])
        retdoc.wasDerivedFrom(prevart, latestart)
        retdoc.used('gallery:'+labels['activity'], latestart)
        derivedentities[labels['artname']] = prevart
        doc = api.document.create(retdoc, name=labels['artname'], public=True)
        docdb.docid = doc.id
        db.session.commit()


def choose_tx():
    response = requests.get(pendingtransactions_address)
    if response.status_code == 200:
        transaction = json.loads(response.content)
        labels = transaction[0]

        if labels['activity'] == 'painting' or labels['activity'] == 'sculpting' or labels['activity'] == 'drawing':
            return new_art()
        elif labels['activity'] == 'submit':
            return auction()
        elif labels['activity'] == 'deliver':
            return transport()
        elif labels['activity'] == 'purchase':
            return purchase()
        elif labels['activity'] == 'display':
            return display()
        elif labels['activity'] == 'store':
            return storage()
