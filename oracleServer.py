import socket
import os
from _thread import *

import subprocess
import json
import struct
import time

class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

class Transaction:
    id = -1
    def __init__(self,senderId, receiverId, amount, vins):
        self.senderId = senderId
        self.receiverId = receiverId
        self.amount = amount
        self.vins = vins
        Transaction.id = Transaction.id + 1

    def printInfo(self):
        print("TX {}, {}, {}, {} ".format(self.id, self.senderId, self.receiverId, self.amount))
       # print("vins : {}")


# Account transaction order variable, we assume the Oracle can identify a unique sender user for different addresses
txCounter = 0
txSenderIdOrder = ["A", "B", "B", "C","C","D", "A","E","E","D"]
txReceiverIdOrder = ["B", "C", "C", "D", "E","E", "C", "A","B","A"]

def initAccounts():
    accountsDict = dict()
    idList = ["A","B","C","D","E"]
    for id_ in idList:
        accountsDict[id_] = {
            "balance" : 0,
            "netBalance" : 0,
            "addresses" : []
        }
    return accountsDict

def printAccounts():
    print("\n\n----- Accounts State -----")
    for id_ in accounts:
        print("id : {}, balance : {}, netBalance : {}, addresses : {}".format(id_,accounts[id_]["balance"],accounts[id_]["netBalance"],accounts[id_]["addresses"]))


def printActiveTxQueue():
    print("\n\n----- Active Queue list -----")
    for tx in activeTxQueue.list:
        tx.printInfo()

# Method returning the owner of the transaction.
# For the moment, we assume the Oracle knows the transaction order and each user will be identified with the following ID : "A", "B", "C", "D", "E"
def getOwnerId():
    return txSenderIdOrder[txCounter], txReceiverIdOrder[txCounter]

# Method returning the hexEncoded vins which will concatenated in the gridlock solution
# Return the original hex encoded tx sent by the user without the txout part by using the txout version(or number of txout ? "01") and the output value
def getHexVin(hexEncodedTx, outValue):
    outValueFormatted = amountToSatoshis(outValue)
    separator = "01" + amountToHex(outValueFormatted) # separator is formed with the output version (OR number of txout ? "01") and output value 
    vInHex = hexEncodedTx.split(separator)[0]    # Save input hex data

    return vInHex

def amountToHex(amount):
    amountHex = hex(amount)[2:].zfill(2*8)
    return BigToLittleEndian(amountHex)

def BigToLittleEndian(bigHex):
    littleBytesArray = []
    for i in range(len(bigHex) -1 , 0 , -2):
      littleBytesArray.append(bigHex[i-1])
      littleBytesArray.append(bigHex[i])

    littleHex = ''.join(littleBytesArray)
    
    print(littleHex)
    return littleHex

def amountToSatoshis(amount):
    outValueFormatted = int(float(format(amount, '.8f')) * (10**8))
    return outValueFormatted 



def threaded_gridlock(period):
    starttime=time.time() 
    while True:

        # Start Gridlock
        print(" {} seconds passed ! Gridlock starting ...".format(period))
        # decoderawtransaction from hex encoded tx


        # Create transaction from gridlock solution
        # We can't use -createrawtransaction API call as the inputs are already signed. Therefore we need to concatenate inputs and output hex data

            # inputs - concatenate the inputs hex data

            # output - 
            # Number of TxOut (Variable Integer)
            # Satoshis (8 bytes - little endian)
            # pubScriptKey size (Variable Integer - default : 1 byte)
            # pubScriptKey (Variable Integer - usually : 19 bytes ) call -validateaddress to generate the scriptPubKey from the receiver bitcoin address
            # Sequence (4 bytes - TBD : 42000000)

        

        # Send transaction to blockchain

        # Execute gridlock again after -period seconds
        time.sleep(period - ((time.time() - starttime) % period))
    

def threaded_client(connection):

    #connection.send(str.encode('Welcome to the Server\n'))

    global txCounter
    global txOrder

    while True:
        data = connection.recv(2048) 
        if not data:
            break

        # Validate data - format : Hex-serialized transaction

        # Parse (call bitcoin-cli API gettransaction )
        if (len(data) != 128 and len(data) != 24 and len(data) != 104): # TEST : len 128 -> bitcoin hello
            print("----- NEW TRANSACTION HAS BEEN DETECTED -----\n")
            print("Length bytes : {}".format(len(data)))
            hexEncodedTx = data.decode('utf-8')
            print("----- Hex Encoded TX -----")
            print(hexEncodedTx)

            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "decoderawtransaction", hexEncodedTx ],stdout=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8')

            print("\n-----Decoded Hex TX -----")
            jsonTx = json.loads(dsubProcessCall)

            print(json.dumps(jsonTx))

            

            # Get sender and receiver ID  - TEMPORARY TODO
            senderId, receiverId = getOwnerId()
            print("\n Sender ID  : {} , Receiver ID : {}".format(senderId,receiverId))
            txCounter = txCounter + 1


            # Get vIn inputs sum - represent the money (balance) the user is willing to contribute in LSM
            vins = jsonTx["vin"] # raw vins
            vIn = [
                {"txid" : vin["txid"],
                 "vout" : vin["vout"]
                } for vin in jsonTx["vin"]]

            sumInputs = getSumOfInputs(vIn)
            # Update balance and net balance from the inputs given by the user
            accounts[senderId]["balance"] += sumInputs
            accounts[senderId]["netBalance"] += sumInputs


            # Get the amount sent to the recipient
            outValue = jsonTx["vout"][0]["value"]
            print("\n Outputs: {}".format(outValue)) 


            # Retrieve the receiver address
            receiverAddress = jsonTx["vout"][0]["scriptPubKey"]["addresses"][0]
            print("\n Receiver address : {}".format(receiverAddress))
            accounts[receiverId]["addresses"].append(receiverAddress) # The first account address will be used as receiver address in the gridlock solution

            # Create the new transaction 
            newTx = Transaction(senderId, receiverId, outValue, vins)

            # Add the transaction to the transactions Queue 
            activeTxQueue.push(newTx)  
            printActiveTxQueue()

            # Add sender id to the accounts Queue
            if (senderId not in accountQueue.list):
                accountQueue.push(senderId)

            # Update the net balance from the transaction output
            accounts[senderId]["netBalance"] -= outValue
            accounts[receiverId]["netBalance"] += outValue

            # print accounts state
            printAccounts()

        

    print('Client left ! ')
    connection.close()
    #ThreadCount -= 1

# Calculate the sum of the inputs value
# inputs : array of objects { "txid" : ..., "vout" : ...}
def getSumOfInputs(inputs):
    
    amount = 0
    print(" \n ----- Inputs decoding (Get Sum of Inputs) -----")
    for inp in inputs:

        # getrawtransaction from txid
        print("getrawtransaction {}".format(inp['txid']))
        subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "getrawtransaction", inp['txid'] ],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        subProcessString = subProcessCall.stdout
        dsubProcessCall = subProcessString.decode('utf-8')[:-1] # decoded output, remove the last empty character

        # Catch errors
        if(subProcessCall.stderr.decode('utf-8') != ''):
            print("getrawtransaction : error")
            break

        
        

        # decoderawtransaction from hex encoded tx
        print("decoderawtransaction {}".format(dsubProcessCall))
        subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "decoderawtransaction", dsubProcessCall ],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subProcessString = subProcessCall.stdout
        dsubProcessCall = subProcessString.decode('utf-8') # decoded output

        # Catch errors
        if (subProcessCall.stderr.decode('utf-8') != ''):
            print("decoderawtransaction : error")
            break


        

        print("Decoded Hex TX")
        jsonTx = json.loads(dsubProcessCall)
        print(json.dumps(jsonTx))

        voutIndex = inp['vout']
        amount += jsonTx['vout'][voutIndex]['value']


    print("\n Inputs total Amount : {}".format(amount))
    return amount

ServerSocket = socket.socket()
MAX_ADDRESSES = 10
host = '127.0.0.1'
port = 8080
ThreadCount = 0
gridLockPeriod = 5

activeTxQueue = Queue()
inactiveTxQueue = Queue()
accountQueue = Queue()
accounts = initAccounts()

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
    raise SystemExit
    #cmd : fuser -k 8080/tcp

print('Listening for connection on port {}..'.format(port))
ServerSocket.listen(MAX_ADDRESSES)



# Start gridlock thread
start_new_thread(threaded_gridlock,(gridLockPeriod,))

# Listen for connection
while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

    


ServerSocket.close()
