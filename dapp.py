import datetime
import hashlib
import json
from flask import Flask, jsonify, request  #get_json will be used to connect nodes in decentralised system
 
import requests

#It will be used to catch the right nodes when we check that all
#the nodes in d-centralised ntrk to apply consesnus
 
from uuid import uuid4
from urllib.parse import urlparse
#It will create an address for each node in the ntrk and to parse the
#URL of ease of these nodes

#create a blockchain
 
class Blockchain:
    def __init__(self):
        self.chain = []
       
        self.transactions = [{"songname":"default","artist":"default"}]
        self.create_block(proof=1,previous_hash=0)
       
        self.nodes = set()
       
    def create_block(self,proof,previous_hash):
        #Define Dict. for essential keys of block
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'song':self.transactions}
       
        self.transactions = [] #Transaction list must be empty after added to the block
        self.chain.append(block)
        return block
       
    def get_previous_block(self):
        return self.chain[-1]
       
    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_value=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_value[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
   
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
   
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
           
            if block['previous_hash'] != self.hash(previous_block):
                return False
           
            previous_proof = previous_block['proof']
            new_proof = block['proof']
            hash_value=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_value[:5] != '00000':
                return False
           
            previous_block = block
            block_index += 1
        return True
   
    #create a format of transaction
    #i.e. Format with Sender,Receiver, Amount
    def add_song(self,songname,artist):
        self.transactions.append({'songname':songname,
                                  'artist':artist,
                                })
        previous_block = self.get_previous_block()
        return previous_block['index']+1
           
       
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
     
       
    def replace_chain(self):
        network=self.nodes #all present nodes
        max_length=len(self.chain) #lenght of chain of current nodes
        longest_chain=None
        print('max',max_length)

        for node in network:
            print(node)
            response=requests.get(f'http://{node}/get_chain')
            print(response.status_code)
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length>max_length and self.is_chain_valid(chain):
                    max_length=length
                    longest_chain=chain

        print(longest_chain)

        if longest_chain:
            self.chain=longest_chain
            return True
        return False




app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block',methods=['GET'])
def mine_block():

    previous_block = blockchain.get_previous_block()

    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)

    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof,previous_hash)

    response = {'message':'block is mined',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash']}
    return jsonify(response), 200

@app.route('/get_chain',methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid',methods=['GET'])
def is_valid():
    is_valid=blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message':'Your chain is validatted'}
    else:
        response = {'message':'Your chain is not valid'}
    return jsonify(response), 200

@app.route('/addToBlockChain',methods=['POST'])
def add_song():
    json = request.get_json()
    transaction_keys = ['songname','artist']
    if not all(key in json for key in transaction_keys):
        return 'Some elements are missing', 400
    index = blockchain.add_song(json['songname'],
                                json['artist'],)
    response = {'Message':f'The song is added to block {index}'}
    return jsonify(response), 201

@app.route('/connect_nodes',methods=['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')

    if nodes is None:
        return 'No Nodes',400
    for node in nodes:
        blockchain.add_node(node)

    response = {'message':'all nodes are now connected',
                'Total nodes':list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
    is_chain_replace=blockchain.replace_chain()
    print(is_chain_replace)
    if is_chain_replace:
        response = {'message':'chain replaced',
                    'new_chain':blockchain.chain}
    else:
        response = {'message':'chain not replaced','new_chain':blockchain.chain}
    return jsonify(response), 200


app.run(host='127.0.0.1',port = 5001)

# {"nodes" :["http://127.0.0.1:5001", "http://127.0.0.1:5002"]}