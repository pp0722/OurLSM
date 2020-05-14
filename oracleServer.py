import socket
import os
from _thread import *

import subprocess
import json
import struct
import time
import timeit
import argparse
import csv

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
    id = 1
    def __init__(self,senderId, receiverId, amount, vins, hexVins):
        self.id = Transaction.id
        self.senderId = senderId
        self.receiverId = receiverId
        self.amount = amount
        self.vins = vins
        self.hexVins = hexVins # CONCATENATED hex vins
        Transaction.id = Transaction.id + 1

    def printInfo(self):
        print("TX {}, {}, {}, {} ".format(self.id, self.senderId, self.receiverId, self.amount))
       # print("vins : {}")


# Account transaction order variable, we assume the Oracle can identify a unique sender user for different addresses
txCounter = 0

# Ubin Case
#txSenderIdOrder = ["A", "B", "B", "C","C","D", "A","E","E","D"]
#txReceiverIdOrder = ["B", "C", "C", "D", "E","E", "C", "A","B","A"]

# Speed test case (2 transactions)
txSenderIdOrder = ["A", "B"]
txReceiverIdOrder = ["B","A"]


def initAccounts(case=None):
    if case is None:
        accountsDict = dict()
        idList = ["A","B","C","D","E"]
        for id_ in idList:
            accountsDict[id_] = {
                "balance" : 0,
                "netBalance" : 0,
                "addresses" : []
            }
    elif case=="ubin":
        accountsDict = dict()
        idList = ["A","B","C","D","E"]
        
        accountsDict["A"] = {
            "balance" : 3,
            "netBalance" : 3,
            "addresses" : ["addressA"]
        }

        accountsDict["B"] = {
            "balance" : 4,
            "netBalance" : 4,
            "addresses" : ["addressB"]
        }

        accountsDict["C"] = {
            "balance" : 5,
            "netBalance" : 5,
            "addresses" : ["addressC"]
        }

        accountsDict["D"] = {
            "balance" : 4,
            "netBalance" : 4,
            "addresses" : ["addressD"]
        }

        accountsDict["E"] = {
            "balance" : 3,
            "netBalance" : 3,
            "addresses" : ["addressE"]
        }

    return accountsDict

def initTx(case="ubin", txNumber=0):
    activeTxQueue.list = []
    if case=="ubin": #ubin phase case
         createTransactionAndUpdate("A","B",5, None, None)
         createTransactionAndUpdate("B","C",6, None, None)
         createTransactionAndUpdate("B","C",30, None, None)
         createTransactionAndUpdate("C","D",8, None, None)
         createTransactionAndUpdate("C","E",80, None, None)
         createTransactionAndUpdate("D","E",7, None, None)
         createTransactionAndUpdate("A","C",6, None, None)
         createTransactionAndUpdate("E","A",8, None, None)
         createTransactionAndUpdate("E","B",100, None, None)
         createTransactionAndUpdate("D","A",5, None, None)

    # Generate random transactions with 5 users
    elif txNumber > 0:
        for i in range(txNumber):
            ids_ = list(accounts.keys())
            amount = random.randint(1, 10)
            senderId = random.choice(ids_)
            receiverId = random.choice(ids_)
            while(receiverId == senderId):
                receiverId = random.choice(ids_)
            createTransactionAndUpdate(senderId, receiverId, amount, None, None)

def createTransactionAndUpdate(senderId,receiverId,outValue, vins, hexVins):
    # Create the new transaction 
    newTx = Transaction(senderId, receiverId, outValue, vins, hexVins)

    # Add the transaction to the transactions Queue 
    activeTxQueue.push(newTx)  

    # Add sender id to the accounts Queue
    if (senderId not in accountQueue.list):
        accountQueue.push(senderId)

    # Update the net balance from the transaction output
    accounts[senderId]["netBalance"] -= outValue
    accounts[receiverId]["netBalance"] += outValue

def printAccounts():
    print("\n\n----- Accounts State -----")
    for id_ in accounts:
        print("id : {}, balance : {}, netBalance : {}, addresses : {}".format(id_,accounts[id_]["balance"],accounts[id_]["netBalance"],accounts[id_]["addresses"]))


def printActiveTxQueue():
    print("\n\n----- Active Queue list -----")
    for tx in activeTxQueue.list:
        tx.printInfo()

def printInactiveTxQueue():
    print("\n\n----- Inactive Queue list -----")
    for tx in inactiveTxQueue.list:
        tx.printInfo()


# Method returning the owner of the transaction.
# For the moment, we assume the Oracle knows the transaction order and each user will be identified with the following ID : "A", "B", "C", "D", "E"
def getOwnerId():
    return txSenderIdOrder[txCounter], txReceiverIdOrder[txCounter]

# Method returning the hexEncoded vins which will concatenated in the gridlock solution
# Return the original hex encoded tx sent by the user without the txout part by using the txout version(or number of txout ? "01") and the output value
def getHexVins(hexEncodedTx, outValue):
    outValueFormatted = amountToSatoshis(outValue)
    separator = "01" + amountToHex(outValueFormatted) # separator is formed with the number of txout (01 generally) and output value 
    vInsHex = hexEncodedTx.split(separator)[0]    # Remove outputs

    
    return vInsHex[2 * (1+39):] # Remove tx version (1byte) and inputs counter (39 bytes)

# Return transaction sent amount in Little Endian hex format.
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

# Return counter of inputs on 39 bytes in Big Endian
def getHexCounterOfInputs(counter):
    hexCounter = hex(counter)[2:]
    hexCounter = (2 * 39 - len(hexCounter)) * "0" + hexCounter
    return hexCounter

# Return counter of outputs on 1 byte
def getHexCounterOfOutputs(counter):
    hexCounter = hex(counter)[2:]
    hexCounter = (2 * 1 - len(hexCounter)) * "0" + hexCounter
    return hexCounter

# Return list of transactions that is part of the gridlock solution
def gridlock():

    print("\n-----Pre-gridlock Accounts State -----")
    printAccounts()

    if (len(activeTxQueue.list) == 0):
        print("\n Active Transaction Queue Empty. No gridlock")
        return

    
    print("\n ----- Gridlock has started -----")
    while len(accountQueue.list) > 0:
        currentId = accountQueue.pop()
        
        
        if(accounts[currentId]["netBalance"] >= 0):
            continue # if net balance is positive, we do not need to remove transaction from active queue for the moment.
        while(accounts[currentId]["netBalance"] < 0):
            removeLatestTx(currentId)
            
    print("\n ----- Gridlock has ended -----")
    printActiveTxQueue()
    printInactiveTxQueue()
    printAccounts()
    
    print("\n ----- ------------------ -----")
        

def removeLatestTx(id_):
    if len(activeTxQueue.list) == 0:
        print("\n Active transaction queue is empty.")
        return
    
    # initialize tx index in active Queue
    txIndex = 0
    for index, tx in enumerate(activeTxQueue.list):
        if tx.senderId == id_:
            
            accounts[tx.senderId]["netBalance"] += tx.amount
            accounts[tx.receiverId]["netBalance"] -= tx.amount

            # queue receiver in accounts queue as its net balance changed.
            if tx.receiverId not in accountQueue.list:
                accountQueue.push(tx.receiverId)

            # delete from activeQueue
            del activeTxQueue.list[index]
            
            # Removed TX
            print("Removed TX :")
            tx.printInfo()

            # push to inactiveQueue
            inactiveTxQueue.push(tx)
            break

def getNumberOfInputs():
    counter = 0
    for tx in activeTxQueue.list:
        counter += len(tx.vins)
    return counter

# Create new address for oracle to receive the fee deducted from his added locking UTXO.

def createNewAddress():
    print("Generating new address for Oracle ... ")
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "getnewaddress" ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    print(dsubProcessCall)
    return dsubProcessCall

def getFirstUTXO():
    print("Generating new address for Oracle ... ")
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "listunspent" ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    
    receiverInfoJson = json.loads(dsubProcessCall)
    txAddress = receiverInfoJson[0]["address"]
    txId = receiverInfoJson[0]["txid"]
    amount = receiverInfoJson[0]["amount"]
    print(" Getting first Oracle UTXO ...")
    print(txAddress, txId, amount)
    return txAddress, txId, amount

def createTransactionFromSolution(fee=0):


    if fee > 0:
        # NB : We can't use -createrawtransaction API call as tthe flag to perform a speed testhe inputs are already signed. Therefore we need to concatenate inputs and output hex data
        print("\n ----- Creating Transaction from solution ...")
        hexEncodedTx = ""
        # Transaction version (1 byte - default : "02")
        hexEncodedTx += "02"
        
        # Number of inputs ( 39 bytes ) 
        counterInputs = getNumberOfInputs() 
        hexEncodedTx += getHexCounterOfInputs(counterInputs)

        # inputs - concatenate the inputs hex data
        for tx in activeTxQueue.list:
            hexEncodedTx += tx.hexVins

        # output - 

        # Number of TxOut (Variable Integer - default : 1 byte)
        counterOutputs = len(activeTxQueue.list)
        hexEncodedTx += getHexCounterOfOutputs(counterOutputs)

        for tx in activeTxQueue.list:

        # Satoshis (8 bytes - little endian) - added fees
            satoshis = amountToSatoshis(accounts[tx.receiverId]["netBalance"] - fee)
            hexAmount = amountToHex(satoshis)
            hexEncodedTx += hexAmount


        # pubScriptKey size / length in bytes (Variable Integer - default : 1 byte = 0x19 -> 25 bytes )
            receiverAddress = accounts[tx.receiverId]["addresses"][0]
            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "validateaddress", receiverAddress  ],stdout=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8')

            receiverInfoJson = json.loads(dsubProcessCall)
            bytesCounter = int(len(receiverInfoJson["scriptPubKey"]) / 2)
            # Assume it is 1 byte and always 0x19
            hexEncodedTx += hex(bytesCounter)[2:]

        # pubScriptKey (Variable Integer - usually : 19 bytes ) call -validateaddress to generate the scriptPubKey from the receiver bitcoin address
            hexEncodedTx += receiverInfoJson["scriptPubKey"]
        
        # Sequence (4 bytes - TBD : 42000000, 66000000)
        hexEncodedTx += "00000000"

        print("Hex encoded tx : ")
        print(hexEncodedTx)
        return hexEncodedTx
    else:
        print("Unsuffiscient Fees. Please set a minimum tx fee using --settxfee when starting the oracleServer")
        # NB : We can't use -createrawtransaction API call as tthe flag to perform a speed testhe inputs are already signed. Therefore we need to concatenate inputs and output hex data
        print("\n ----- Creating Transaction from solution ...")
        hexEncodedTx = ""
        # Transaction version (1 byte - default : "02")
        hexEncodedTx += "02"
        
        # Number of inputs ( 39 bytes )
        counterInputs = getNumberOfInputs()
        hexEncodedTx += getHexCounterOfInputs(counterInputs)

        # inputs - concatenate the inputs hex data
        for tx in activeTxQueue.list:
            hexEncodedTx += tx.hexVins

        # output - 

        # Number of TxOut (Variable Integer - default : 1 byte)
        counterOutputs = len(activeTxQueue.list)
        hexEncodedTx += getHexCounterOfOutputs(counterOutputs)

        for tx in activeTxQueue.list:

        # Satoshis (8 bytes - little endian)
            satoshis = amountToSatoshis(accounts[tx.receiverId]["netBalance"])
            hexAmount = amountToHex(satoshis)
            hexEncodedTx += hexAmount


        # pubScriptKey size / length in bytes (Variable Integer - default : 1 byte = 0x19 -> 25 bytes )
            receiverAddress = accounts[tx.receiverId]["addresses"][0]
            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "validateaddress", receiverAddress  ],stdout=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8')

            receiverInfoJson = json.loads(dsubProcessCall)
            bytesCounter = int(len(receiverInfoJson["scriptPubKey"]) / 2)
            # Assume it is 1 byte and always 0x19
            hexEncodedTx += hex(bytesCounter)[2:]

        # pubScriptKey (Variable Integer - usually : 19 bytes ) call -validateaddress to generate the scriptPubKey from the receiver bitcoin address
            hexEncodedTx += receiverInfoJson["scriptPubKey"]
        
        # Sequence (4 bytes - TBD : 42000000, 66000000)
        hexEncodedTx += "00000000"

        print("Hex encoded tx : ")
        print(hexEncodedTx)
        return hexEncodedTx


def sendTransaction(hexEncodedTx):
    print("\n ----- Send Final transaction to the blockchain ...")
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "sendrawtransaction", hexEncodedTx  ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    print("\n sendrawtransaction : {}".format(dsubProcessCall))

def generateNewBlock(period):
    
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "generate", "1" ],stdout=subprocess.PIPE)
    #subProcessString = subProcessCall.stdout
    #dsubProcessCall = subProcessString.decode('utf-8')

def updateBalance():
    print("Updating balance ...")
    for tx in activeTxQueue.list:
        accounts[tx.senderId]['balance'] = 0
        accounts[tx.senderId]['netBalance'] = 0
    


def threaded_generate_block(period):            #cmd : fuser -k 8080/tcp

        # Start Gridlock
        
        
        starttime = time.time()
        
        while True:
            
            generateNewBlock(period)
            print(" {} seconds passed ! Generating block ...".format(period))
            print(period - ((time.time() - starttime) % period))
            time.sleep(period - ((time.time() - starttime) % period))

def threaded_gridlock(period, fee = 0):            #cmd : fuser -k 8080/tcp

        # Start Gridlock
        
        
        starttime = time.time()
        
        while True:
            gridlock() # update active tx queue and keeps only transactions that solves the gridlock

            # Create transaction from gridlock solution
            if (len(activeTxQueue.list) == 0):
                print(" \n No solution found")
            else :
                print(" \n Solution Found !")

                if fee > 0:
                    hexEncodedTx = createTransactionFromSolution(fee)
                else:
                    hexEncodedTx = createTransactionFromSolution() 

                # Send transaction to blockchain
                sendTransaction(hexEncodedTx)

                # Update balance and net balance (because we use UTXO, all the money is given back so balance/netbalance is set to 0)
                updateBalance()

            # Move back removed transaction to the active queue. NB : at this point, active queue should still be locked for all the client threads.
            activeTxQueue.list = inactiveTxQueue.list[::-1] # Reverse list to keep the time order

            # To be implemented : Unlock ressources for client threads

            # Execute gridlock again after -period seconds
            print(" {} seconds passed ! Gridlock starting ...".format(period))
            print(period - ((time.time() - starttime) % period))
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

            # Get concatenated hexVins
            hexVins = getHexVins(hexEncodedTx, outValue)
            print("\n hexVins extraction : {}".format(hexVins))

            # Create the new transaction 
            newTx = Transaction(senderId, receiverId, outValue, vins, hexVins)

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


def readCommand():
	# construct the argument parse and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fulltest",action='store_true', help="Set the flag to perform a full speed test")
    parser.add_argument("-t", "--test",action='store_true', help="Set the flag to perform a speed test")
    parser.add_argument("-n", "--txNumber", type=int, help="Set the tx number")
    parser.add_argument("-s", "--settxfee",type=float, help="Set the tx fee")
    args = vars(parser.parse_args())
    return args


ServerSocket = socket.socket()
MAX_ADDRESSES = 10
host = '127.0.0.1'
port = 8080
ThreadCount = 0
gridLockPeriod = 5 # seconds
blockPeriod = 10 # seconds

activeTxQueue = Queue()
inactiveTxQueue = Queue()
accountQueue = Queue()
accounts = initAccounts()


if __name__=="__main__":

    args = readCommand()

    # TEST GRIDLOCK SPEED

    # full test for 5 users
    if args["fulltest"]:
        import random
        txNumbers = [10,100,1000,5000,10000]
        timeAverage = [0,0,0,0,0]
        txAverage = [0,0,0,0,0]
        roundNumber = 1

        for i in range(roundNumber):
            for index,txNumber in enumerate(txNumbers):

                accounts = initAccounts("ubin")
                initTx(case="random", txNumber=txNumber)

                time = timeit.timeit(gridlock, number = 1)

                timeAverage[index] += time
                txAverage[index] += (len(activeTxQueue.list) * 100) / txNumber
                # write initial tx number, gridlock speed time and number of tx that is part of the solution
        
        timeAverage = [ time/roundNumber for time in timeAverage]
        txAverage = [ txCounter/roundNumber for txCounter in txAverage]

        with open('gridlock_speed_test.csv', 'w') as f:
            writer = csv.writer(f)
            
            writer.writerow(["Number of transactions","Gridlock time", "Settled transactions (sec)"] )
            for i in range(len(txNumbers)):
                writer.writerow([txNumbers[i],timeAverage[i], txAverage[i]] ) # todo 


    # manual testing
    elif args["test"]:
        import random


        print("\n ----- GRIDLOCK SPEED TEST -----")
        # init account State
        accounts = initAccounts("ubin")
        # init active transaction queue


        if( args["txNumber"]):
            #python3 oracleServer.py -t -n 100
            initTx(case="random", txNumber=int(args["txNumber"]))
        else:
            #python3 oracleServer.py -t 
            initTx("ubin")

        # print state
        printActiveTxQueue()
        printAccounts()

        # start gridlock
        time = timeit.timeit(gridlock, number=1)
        print("Gridlock execution time : {} s".format(time))
        
    # REAL ORACLE SERVER
    else:
        try:
            ServerSocket.bind((host, port))
        except socket.error as e:
            print(str(e))
            raise SystemExit

        print('Listening for connection on port {}..'.format(port))
        ServerSocket.listen(MAX_ADDRESSES)


        # Start generate blocks thread
        start_new_thread(threaded_generate_block, (blockPeriod,))
        # Start gridlock thread
        start_new_thread(threaded_gridlock,(gridLockPeriod,args["settxfee"],))

        # Listen for connection
        while True:
            Client, address = ServerSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(threaded_client, (Client, ))
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))

            


        ServerSocket.close()
