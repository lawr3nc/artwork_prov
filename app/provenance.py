import prov.model as prov
from provstore.api import Api
"""from app import routes, blockchain"""
import json
import requests

api = Api(base_url='https://openprovenance.org/store/api/v0', username="kym3ni", api_key="ef2cff88eb50f915a5fd6653e19392b355ca5c0a")
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:5000"


class Provenance:
    document = prov.ProvDocument()
    document.add_namespace('art', 'http://art.com/')
    document.add_namespace('auction', 'http://auction.com/')
    document.add_namespace('transport', 'http://transport.com/')
    document.add_namespace('gallery', 'http://gallery.com/')


pendingtransactions_address = "{}/pendingtransactions".format(CONNECTED_NODE_ADDRESS)
minedtransactions_address = "{}/get_transactions".format(CONNECTED_NODE_ADDRESS)


def new_art():
    newprov = Provenance()
    response = requests.get(pendingtransactions_address)
    if response.status_code == 200:
        transaction = json.loads(response.content)
        labels = transaction[0]

        newprov.document.entity('art:'+labels['artid'], {
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

        newprov.document.wasAttributedTo('art:'+labels['artid'], 'art:'+labels['artistid'])

        newprov.document.wasGeneratedBy('art:'+labels['artid'], 'art:'+labels['activity'])

        api.document.create(newprov.document, name='CreateArt', public=True)

def auction():
    response = requests.get(pendingtransactions_address)
    minedtx = requests.get(minedtransactions_address)
    if response.status_code == 200 and minedtx.status_code == 200:
        transaction = json.loads(response.content)
        labels = transaction[0]
