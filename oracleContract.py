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
import sys
from datetime import datetime
from speedTestCase import *

# Default Queue structucture for Transaction Queue, Account Queue
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
    def __init__(self,senderId, receiverId, amount, vins, hexVins, createdAt):
        self.id = Transaction.id
        self.senderId = senderId
        self.receiverId = receiverId
        self.amount = amount
        self.vins = vins
        self.hexVins = hexVins # CONCATENATED hex vins
        self.createdAt = createdAt
        self.queueAt = 0
        self.solvedAt = 0
        self.offsetTime = 0  # Time of gridlock solution (with pending time removed) from transaction received to solution creation
        Transaction.id = Transaction.id + 1

    def printInfo(self):
        print("TX {}, {}, {}, {} ".format(self.id, self.senderId, self.receiverId, self.amount))
       # print("vins : {}")

class CODE:
    INFO = "[INFO]"
    ERROR = "[ERROR]"



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

"""
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
    global accounts
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

"""

def printAccounts():
    global accounts
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
    global txCounter

    if txCounter == len(txSenderIdOrder): 
        txCounter = 0 # reset tx counter

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

def gridlock():
    """
    Run the gridlock directly (not used in this script)
    This script uses a contract-based gridlock. See next function 'ourContractGridlock'.
    """

    global accounts
    print("\n-----Pre-gridlock Accounts State -----")
    printAccounts()

    if (len(activeTxQueue.list) == 0):
        print("\n Active Transaction Queue Empty. No gridlock")
        return

    
    print("\n ----- Gridlock has started -----")
    
    while len(accountQueue.list) > 0:
        printActiveTxQueue()
        printAccounts()
        print("Account Queue list : {}".format(accountQueue.list))
        
        currentId = accountQueue.pop()
        print("Account pop {}".format(currentId))
        
        if(accounts[currentId]["netBalance"] >= 0):
            continue # if net balance is positive, we do not need to remove transaction from active queue for the moment.
        while(accounts[currentId]["netBalance"] < 0):
            removeLatestTx(currentId)
            
    print("\n ----- Gridlock has ended -----")
    printActiveTxQueue()
    printInactiveTxQueue()
    printAccounts()
    print("\n ----- ------------------ -----")
        

def ourContractGridlock():
    """ 
    Run gridlock in the deployed contract
    """

    output = ourContractCall("gridlock")
    if output:
        print(CODE.INFO, "Received output (gridlock contract) : {}".format(output))
        decodeContractGridlock(output)

    print(CODE.INFO,"OurContract Gridlock ended.")

    

def decodeContractGridlock(solution):
    """
    Decode the contract gridlock output containing the remaining transactions in the gridlock solution
    The contract returns the transactions in the below format:
                    id,senderAddress,receiverAddress,amount
    """

    txs = solution.split("\n")[:-1] 
    ids = [int(tx[0]) for tx in txs] 
    inactiveTxQueue.list = [tx for tx in activeTxQueue.list if tx.id not in ids]
    activeTxQueue.list = [tx for tx in activeTxQueue.list if tx.id in ids]
    
    # Update balance from the solution given by the contract
    for tx in inactiveTxQueue.list:
        accounts[tx.senderId]["netBalance"] += tx.amount
        accounts[tx.receiverId]["netBalance"] -= tx.amount


def removeLatestTx(id_):
    """
    Remove transaction by id from the active transaction queue and push into inactive transaction queue
    Update the netBalance of the transaction's sender and receiver
    Add the transaction's receiver into the account queue
    """
    global accounts
    print("RemoveLatestTx call ...")
    if len(activeTxQueue.list) == 0:
        print("\n Active transaction queue is empty.")
        return
    
    # initialize tx index in active Queue, remove only the first one and check again
    for index, tx in enumerate(activeTxQueue.list):
        if tx.senderId == id_:
            
            accounts[tx.senderId]["netBalance"] += tx.amount
            accounts[tx.receiverId]["netBalance"] -= tx.amount

            # delete from activeQueue
            del activeTxQueue.list[index]
            
            # Removed TX
            print("Removed TX :")
            tx.printInfo()

            # push to inactiveQueue
            inactiveTxQueue.push(tx)


            # queue receiver in accounts queue as its net balance changed.
            if tx.receiverId not in accountQueue.list:
                print("Account push : {}".format(tx.receiverId))
                accountQueue.push(tx.receiverId)
            
            break

            

def getNumberOfInputs():
    counter = 0
    for tx in activeTxQueue.list:
        counter += len(tx.vins)
    return counter



def createTransactionFromSolution(startGridlockTime,fee=0):
    """
    Build the transaction by concatenating hex data (not used in this script)
    See Bitcoin Byte-map on : https://en.bitcoin.it/wiki/File:TxBinaryMap.png

    """
    global accounts

    if fee > 0:
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

        # Number of outputs (Variable Integer - default : 1 byte)
        outId = []
        for tx in activeTxQueue.list:
            if tx.senderId not in outId:
                outId.append(tx.senderId)
            if tx.receiverId not in outId:
                outId.append(tx.receiverId)
        counterOutputs = len(outId)
        hexEncodedTx += getHexCounterOfOutputs(counterOutputs)


        # outputs - concatenate the outputs hex data
        for receiverId in outId:

        # Satoshis (8 bytes - little endian) - added fees
            satoshis = amountToSatoshis(accounts[receiverId]["netBalance"] - fee)
            hexAmount = amountToHex(satoshis)
            hexEncodedTx += hexAmount


        # pubScriptKey size / length in bytes (Variable Integer - default : 1 byte = 0x19 -> 25 bytes )
            receiverAddress = accounts[receiverId]["addresses"][0]
            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "validateaddress", receiverAddress  ],stdout=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8')

            receiverInfoJson = json.loads(dsubProcessCall)
            bytesCounter = int(len(receiverInfoJson["scriptPubKey"]) / 2)
            # Assume it is 1 byte and always 0x19
            hexEncodedTx += hex(bytesCounter)[2:]

        # pubScriptKey (Variable Integer - usually : 19 bytes ) call -validateaddress to generate the scriptPubKey from the receiver bitcoin address
            hexEncodedTx += receiverInfoJson["scriptPubKey"]


        # Save processing time by the Oracle from received tx time to final tx inclusion
        
        saveGridlockTime(startGridlockTime)


        # Sequence (4 bytes - TBD : 42000000, 66000000)
        hexEncodedTx += "00000000"

        print("Hex encoded tx : ")
        print(hexEncodedTx)
        print("Length bytes : {}".format(len(hexEncodedTx) /  2))
        return hexEncodedTx

    else:
        print("Unsuffiscient Fees. Please set a minimum tx fee using --settxfee when starting the oracleServer")
        sys.exit(0)


def sendTransaction(hexEncodedTx): 
    """
    Send a hex-encoded transaction to the miners using bitcoin API call -sendrawtransaction
    This script does not use this method. 
    """

    print(CODE.INFO,"Send Final transaction to the blockchain ...")
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "sendrawtransaction", hexEncodedTx  ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    print(CODE.INFO,"sendrawtransaction : {}".format(dsubProcessCall))

def sendTransactionFromOracle():
    """
    Send a transaction to the miners using bitcoin API call -sendmany using the Oracle money.
    The transaction's outputs in built from the gridlock solution :
        - outputs'receivers are the receivers from the remaining transactions in the active queue
        - outputs' amounts are the receivers bet balance
    """

    print(CODE.INFO,"Send Final transaction to the blockchain...")
    dummy = "\"\"".encode()
    cmd = "{"
    for id_ in accounts:
        if accounts[id_]["addresses"] != [] and accounts[id_]["netBalance"] > 0:
            #cmd += "\\\"{}\\\" : {},".format(str(accounts[id_]["addresses"][0]), str(accounts[id_]["netBalance"]))
            cmd +=   "\"" + str(accounts[id_]["addresses"][0])  +"\"" + ":" + str(accounts[id_]["netBalance"]) + ","
    cmd = cmd[:-1] # remove last comma
    cmd += "}"
    
    cmd = cmd.encode()
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "sendmany","", cmd  ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    print(CODE.INFO,"sendmany - txid : {}".format(dsubProcessCall))


def generateNewBlock():
    
    subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "generate", "1" ],stdout=subprocess.PIPE)
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    print("{}".format(dsubProcessCall))

# Update balance from sent UTXO
def updateBalance():
    global accounts
    print(CODE.INFO,"Updating balance ...")
    for tx in activeTxQueue.list:
        accounts[tx.senderId]['balance'] = 0
        accounts[tx.senderId]['netBalance'] = 0

    activeTxQueue.list = [] # Reset active queue

# Update balance inactive tx moved back to active tx for the next round
def updateBalanceBack():
    global accounts
    print(CODE.INFO,"Updating balance BACK ...")
    for tx in activeTxQueue.list:
        accounts[tx.senderId]['netBalance'] -= tx.amount
        accounts[tx.receiverId]['netBalance']+= tx.amount
        # push tx account back in queue
        accountQueue.push(tx.senderId)

def saveGridlockTime(startGridlockTime):
    endGridlockTime = datetime.now()
    
    # Remove gridlock time to get the absolute gridlock time
   # solvedAt = datetime.now()
    #tx.solvedAt = solvedAt
    with open('solving_speed.csv', 'a') as f:
            writer = csv.writer(f)
            for tx in activeTxQueue.list:
                tx.solvedAt = endGridlockTime
                tx.offsetTime = tx.offsetTime + (endGridlockTime - startGridlockTime)
                writer.writerow([tx.id, int((tx.offsetTime).microseconds) ]) # write micro


def threaded_generate_block(period):       
        starttime = time.time()
        
        while True:
            time.sleep(period - ((time.time() - starttime) % period))
            print(CODE.INFO,"{} seconds passed ! Generating block ...".format(period))
            generateNewBlock()

def threaded_gridlock(period):          

        global solutionCounter
        starttime = time.time()
        
        while True:
            # Execute gridlock again after -period seconds
            time.sleep(period - ((time.time() - starttime) % period))
            print(CODE.INFO,"{} seconds passed ! Gridlock starting ...".format(period))

            startGridlockTime = datetime.now() # Used to remove the time where gridlock is sleeping ...
            ourContractGridlock() # Call gridlock in smart contract
            
            # Send TX from oracle
            if (len(activeTxQueue.list) == 0):
                print(CODE.INFO,"No solution found")
            else:
                sendTransactionFromOracle()
                updateBalance()

            
            # Move back removed transaction to the active queue. NB : at this point, active queue should still be locked for all the client threads.
            if inactiveTxQueue.list != []:
                activeTxQueue.list = inactiveTxQueue.list[::-1] # Reverse list to keep the time order
                updateBalanceBack()
                inactiveTxQueue.list = [] # reset inactiveTx

            # To be implemented : Unlock ressources for client threads

            
        
def threaded_speed(delay = 5):
    global txSenderIdOrder
    global txReceiverIdOrder

    time.sleep(delay) # Delay to let user start nodes
    # Init bitcoin folders
    initBitcoinFolder()

    # Create new addresses and send initial balance form oracle # reinitialize accounts
    initAccountAddressAndBalance()

    while(1):
        print("[INFO] Generate transactions ... (and store sender/receiver order for Oracle")
        txSenderIdOrder, txReceiverIdOrder, txData = generateTransactions(10)
        print("[INFO] Generated {} transactions ".format(len(txSenderIdOrder)))
        print("[INFO] Sender order ")
        print(txSenderIdOrder)
        print("[INFO] Receiver order ")
        print(txReceiverIdOrder)


        time.sleep(0.01)
        print("Sending transactions ...")
        for index, data in enumerate(txData):
            print("[INFO] Waiting tx ....")
            time.sleep(0.01)
            print("[INFO] " + txSenderIdOrder[index] + " sends " + str(data['args'][1]) + " to " + txReceiverIdOrder[index])
            txHash = sendBitcoinCall(data["datadir"], data["conf"], data["method"], data["args"])
            print("[INFO] txHash : " + txHash)
        time.sleep(1)


def threaded_client(connection):

    #connection.send(str.encode('Welcome to the Server\n'))

    global txCounter
    global txOrder
    global accounts

    while True:
        data = connection.recv(2048) 
        if not data:
            break

        # Validate data - format : Hex-serialized transaction

        # Parse (call bitcoin-cli API gettransaction )
        if (len(data) != 128 and len(data) != 24 and len(data) != 104): # TEST : len 128 -> bitcoin hello
            createdAt = datetime.now()
            print("----- NEW TRANSACTION HAS BEEN DETECTED ----- {}\n".format(createdAt))
            #print("Length bytes : {}".format(len(data)))
            hexEncodedTx = data.decode('utf-8')
            print("----- Hex Encoded TX -----")
            print(hexEncodedTx)
            # Decode raw transaction
            dsubProcessCall = sendBitcoinCall(dataDirOracle, confFileOracle, "decoderawtransaction", args=[hexEncodedTx])

            print("\n-----Decoded Hex TX -----")
            jsonTx = json.loads(dsubProcessCall)
            print(json.dumps(jsonTx))

            

            # Get sender and receiver ID  - TEMPORARY TODO
            senderId, receiverId = getOwnerId()
            print("\n Sender ID  : {} , Receiver ID : {}".format(senderId,receiverId))
            txCounter = txCounter + 1


            # Get vIn inputs sum - represent the money (balance) the user is willing to contribute in LSM
            vins = jsonTx["vin"] # raw vins
            if vins != []:
                vIn = [
                    {"txid" : vin["txid"],
                    "vout" : vin["vout"]
                    } for vin in jsonTx["vin"]]
            else:
                vIn = None


            sumInputs = getSumOfInputs(vIn)
            # Update balance and net balance from the inputs given by the user
            accounts[senderId]["balance"] += sumInputs
            accounts[senderId]["netBalance"] += sumInputs
            # CONTRACT CALL : update balance
            ourContractCall("setbalance", args = [senderId, sumInputs])


            # Get the amount sent to the recipient
            outValue = jsonTx["vout"][0]["value"]
            print("\n Outputs: {}".format(outValue)) 


            # Retrieve the receiver address
            receiverAddress = jsonTx["vout"][0]["scriptPubKey"]["addresses"][0]
            #print("\n Receiver address : {}".format(receiverAddress))
            if receiverAddress not in accounts[receiverId]["addresses"]:
                accounts[receiverId]["addresses"].append(receiverAddress) # The first account address will be used as receiver address in the gridlock solution

            # Get concatenated hexVins
            hexVins = getHexVins(hexEncodedTx, outValue)
            #print("\n hexVins extraction : {}".format(hexVins))
            
            # CONTRACT CALL : transfer money
            ourContractCall("transfer", args=[senderId, receiverId, outValue])
            # Create the new transaction 
            newTx = Transaction(senderId, receiverId, outValue, vins, hexVins, createdAt)
            newTx.queueAt = datetime.now()
            newTx.offsetTime = newTx.queueAt - newTx.createdAt # Time between transaction receive and transaction queue
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
    if inputs is None:
        print(" No inputs ...")
        return amount
    else:
        for inp in inputs:

            # getrawtransaction from txid
            #print("getrawtransaction {}".format(inp['txid']))
            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "getrawtransaction", inp['txid'] ],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8')[:-1] # decoded output, remove the last empty character

            # Catch errors
            if(subProcessCall.stderr.decode('utf-8') != ''):
                print("getrawtransaction : error")
                break

            
            

            # decoderawtransaction from hex encoded tx
            #print("decoderawtransaction {}".format(dsubProcessCall))
            subProcessCall = subprocess.run(["bitcoin-cli","-regtest", "-datadir=/home/david/.bitcoinOracle/", "-conf=/home/david/.bitcoinOracle/bitcoin.conf", "decoderawtransaction", dsubProcessCall ],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subProcessString = subProcessCall.stdout
            dsubProcessCall = subProcessString.decode('utf-8') # decoded output

            # Catch errors
            if (subProcessCall.stderr.decode('utf-8') != ''):
                print("decoderawtransaction : error")
                break


            

            #print("Decoded Hex TX")
            jsonTx = json.loads(dsubProcessCall)
            #print(json.dumps(jsonTx))

            voutIndex = inp['vout']
            amount += jsonTx['vout'][voutIndex]['value']


        print("\n Inputs total Amount : {}".format(amount))
        return amount



def sendBitcoinCall(datadir, conf, method, args = None):
    if args is None:
        subProcessCall = subprocess.run(["bitcoin-cli","-regtest", datadir, conf, method ],stdout=subprocess.PIPE)
    else:
        cmd = ["bitcoin-cli","-regtest", datadir, conf, method ]
        for arg in args:
            cmd.append(str(arg))
        subProcessCall = subprocess.run(cmd,stdout=subprocess.PIPE)



    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    return dsubProcessCall

def ourContractCall( method, args = None):
    if args is None:
        cmd = ["ourcontract-rt","contracts", "lsm", method]
        print("[INFO] ", cmd)
        subProcessCall = subprocess.run( cmd,stdout=subprocess.PIPE)
    else:
        cmd = ["ourcontract-rt","contracts", "lsm", method ]
        print("[INFO] ", cmd)
        for arg in args:
            cmd.append(str(arg))
        subProcessCall = subprocess.run(cmd,stdout=subprocess.PIPE)
        
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    return dsubProcessCall

def compileContract():
    cmd = ["ourcontract-mkdll", "contracts", "lsm"]
    subProcessCall = subprocess.run( cmd,stdout=subprocess.PIPE)
    print("[INFO] LSM contract compiled successfuly. ")
    subProcessString = subProcessCall.stdout
    dsubProcessCall = subProcessString.decode('utf-8')
    return dsubProcessCall

def printGridlockParams():
    print(CODE.INFO, "Block generation period :", blockPeriod)
    print(CODE.INFO, "Oracle server, host :", host, "port :",port)
    print(CODE.INFO, "Gridlock period :", gridLockPeriod )
    
def setTestCase(case):
    global txSenderIdOrder, txReceiverIdOrder
    if case == "bilateral":
        txSenderIdOrder = ["A", "B"]
        txReceiverIdOrder = ["B","A"]
    elif case == "ubin":
        txSenderIdOrder = ["A", "B", "B", "C","C","D", "A","E","E","D"]
        txReceiverIdOrder = ["B", "C", "C", "D", "E","E", "C", "A","B","A"]
    elif case == "random":
        pass
    else:
        print(CODE.ERROR, "The set case is not available.")
        sys.exit(0)

    print(CODE.INFO, "Test case set to : {}".format(case))


def readCommand():
	# construct the argument parse and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--case",default="bilateral", help="Set the test case to perform a speed test (bilateral|ubin|random)")
    parser.add_argument("-r", "--rootDir", help="Set the root directory for the bitcoin folders")
    parser.add_argument("-t", "--test",action="store_true", help="Enable the speed test")
    parser.add_argument("-n", "--txNumber", type=int, help="Set the tx number")
    parser.add_argument("-d", "--debug",action='store_true', help="Set debug flag") # TODO
    args = vars(parser.parse_args())
    return args




# Bitcoin API calls configuration
rootDir = "/home/david/"
confFileOracle = "-conf=" + rootDir + ".bitcoinOracle" + "/bitcoin.conf"
dataDirOracle = "-datadir=" + rootDir + ".bitcoinOracle"



# Server configuration
ServerSocket = socket.socket()
MAX_ADDRESSES = 10
host = '127.0.0.1'
port = 8080
ThreadCount = 0

# Gridlock, block generation thread periods
gridLockPeriod = 15 # seconds
blockPeriod = 20 # seconds



# Initialize Queue and account state
activeTxQueue = Queue()
inactiveTxQueue = Queue()
accountQueue = Queue()
accounts = initAccounts()


# Original transactions counter and final transaction counter
txCounter = 0 # tansaction counter used with -txSenderIdOrder, -txReceiverIdORder variables to retrieve the tx sender/receiver
solutionCounter = 1

# Transactions' senders and receivers order
txSenderIdOrder = []
txReceiverIdOrder = []



if __name__=="__main__":

    args = readCommand()
    setTestCase(args["case"])
    if args["rootDir"]:
        rootDir = args["rootDir"]

    printGridlockParams()

    # full test for 5 users
    
    if args["test"]:
        import random
        txNumbers = [10,100,1000,5000,10000]
        timeAverage = [0,0,0,0,0]
        txAverage = [0,0,0,0,0]
        roundNumber = 1
        """
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
                writer.writerow([txNumbers[i],timeAverage[i], txAverage[i]] )
        """
       
    # REAL ORACLE SERVER
    else:
        try:
            
            ServerSocket.bind((host, port))

        except socket.error as e:
            print(str(e))
            raise SystemExit

        print(CODE.INFO,'Listening for connection on port {}..'.format(port))
        ServerSocket.listen(MAX_ADDRESSES)

        # Compile LSM contract
        compileContract()
        # Deploy LSM contract
        ourContractCall("init")
        # Start generate blocks thread
        start_new_thread(threaded_generate_block, (blockPeriod,))
        # Start gridlock thread
        start_new_thread(threaded_gridlock,(gridLockPeriod,))

        
        # Listen for connections
        while True:
            Client, address = ServerSocket.accept()
            print(CODE.INFO, 'Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(threaded_client, (Client, ))
            ThreadCount += 1
            print(CODE.INFO,'Thread Number: ' + str(ThreadCount))

        ServerSocket.close()
