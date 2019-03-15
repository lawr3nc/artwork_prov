from hashlib import sha256
import time
import json
import requests
from flask import request
from app import app
from app.provenance import choose_tx


class Block:
    def __init__(self, index, transactions, timest, prev_hash):
        self.index = index
        self.transactions = transactions
        self.timest = timest
        self.prev_hash = prev_hash
        self.nonce = 0

    def generate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 5

    def __init__(self):
        self.pending_transactions = []
        self.chain = []
        self.generate_genesisblock()

    def generate_genesisblock(self):
        genesisblock = Block(0, [], time.time(), "0")
        genesisblock.hash = genesisblock.generate_hash()
        self.chain.append(genesisblock)

    @property
    def lastblock(self):
        return self.chain[-1]

    def addblock(self, block, proof):
        prev_hash = self.lastblock.hash
        if prev_hash != block.prev_hash:
            return False

        if not Blockchain.is_proof_valid(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def addnewTransactions(self, transaction):
        self.pending_transactions.append(transaction)

    def proof_of_work(self, block):
        block.nonce = 0

        generated_hash = block.generate_hash()
        while not generated_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            generated_hash = block.generate_hash()

        return generated_hash

    def mine(self):
        if not self.pending_transactions:
            return False

        lastblock = self.lastblock

        newblock = Block(index=lastblock.index + 1,
                        transactions=self.pending_transactions,
                        timest=time.time(),
                        prev_hash=lastblock.hash)

        proof = self.proof_of_work(newblock)
        self.addblock(newblock, proof)

        self.pending_transactions = []
        announce_newblock(newblock)
        return newblock.index

    @classmethod
    def is_proof_valid(cls, block, blockhash):
        return (blockhash.startswith('0' * Blockchain.difficulty) and
                blockhash == block.generate_hash())

    @classmethod
    def chain_validity(cls, chain):
        result = True
        prev_hash = "0"

        for block in chain:
            blockhash = block.hash
            delattr(block, "hash")

            if not cls.is_proof_valid(block, block.hash) or prev_hash != block.prev_hash:
                result = False
                break

            block.hash, prev_hash = blockhash, blockhash

        return result


blockchain = Blockchain()

peers = set()


@app.route('/newtransaction', methods=['POST'])
def newtransaction():
    print(getchain())
    transaction_data = request.get_json()
    transaction_data["timestamp"] = time.time()
    blockchain.addnewTransactions(transaction_data)
    choose_tx()
    print(get_pendingtransactions())

    return "Success", 201


@app.route('/chain', methods=['GET'])
def getchain():
    consensus()
    chaindata = []
    for block in blockchain.chain:
        chaindata.append(block.__dict__)
    return json.dumps({"length": len(chaindata),
                       "chain": chaindata,
                       "peers": list(peers)})


@app.route('/mine', methods=['GET'])
def mine_pending_transactions():
    result = blockchain.mine()
    if not result:
        return "Enter provenance to mine."
    return "Block #{} is mined.".format(result)


@app.route('/add_node', methods=['POST'])
def add_newpeers():
    nodeaddress = request.get_json()["nodeaddress"]
    if not nodeaddress:
        return "Invalid data", 400

    peers.add(nodeaddress)

    return getchain()


@app.route('/registerwith', methods=['POST'])
def registerwith_existingnode():
    nodeaddress = request.get_json()["nodeaddress"]
    if not nodeaddress:
        return "Invalid data", 400

    data = {"nodeaddress": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(nodeaddress + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = createchain_fromdump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def createchain_fromdump(chain_dump):
    blockchain = Blockchain()
    for index, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if index > 0:
            added = blockchain.addblock(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # the block is a genesis block, no verification needed
            blockchain.chain.append(block)
    return blockchain


@app.route('/addblock', methods=['POST'])
def validate_and_addblock():
    blockdata = request.get_json()
    block = Block(blockdata["index"],
                  blockdata["transactions"],
                  blockdata["timest"],
                  blockdata["prev_hash"])

    proof = blockdata['hash']
    added = blockchain.addblock(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


@app.route('/pendingtransactions')
def get_pendingtransactions():
    return json.dumps(blockchain.pending_transactions)


def consensus():
    global blockchain

    longestchain = None
    currentlength = len(blockchain.chain)

    for peer in peers:
        response = request.get('{}chain'.format(peer))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > currentlength and blockchain.chain_validity(chain):
            currentlength = length
            longestchain = chain

    if longestchain:
        blockchain = longestchain
        return True

    return False


def announce_newblock(block):
    for peer in peers:
        url = "{}addblock".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))
