import os
import subprocess
import random
import argparse
import time

rootDir = "/home/david/"
users = ["","B","C","D","E"]
idList = ["A","B","C","D","E"]
accounts = dict()


confFiles = [ "-conf=" + rootDir + ".bitcoin" + user + "/bitcoin.conf" for user in users]
dataDirs = [ "-datadir=" + rootDir + ".bitcoin" + user for user in users]

confFileOracle = "-conf=" + rootDir + ".bitcoinOracle" + "/bitcoin.conf"
dataDirOracle = "-datadir=" + rootDir + ".bitcoinOracle"




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

def initBitcoinFolder():
    for user in users:
        if os.path.exists(rootDir + ".bitcoin" + user + "/") == False:
            print("e")
            os.makedirs(rootDir + ".bitcoin" + user + "/")


def initAccountAddressAndBalance():
    # Create accounts data structure and randomly choose their balance
    for id_ in idList:
        balance = random.randint(1, 10)
        accounts[id_] = {
            "balance" : balance,
            "netBalance" :  balance,
            "addresses" : []
        }
    

    for i in range(len(dataDirs)):
        # Create new address for each user
        address = sendBitcoinCall(dataDirs[i], confFiles[i], "getnewaddress")
        accounts[idList[i]]["addresses"].append(address[:-1]) # remove \n character from address  

        # Send money to users to initialize their balance
        args = [address[:-1],  accounts[idList[i]]["balance"]]
        sendBitcoinCall(dataDirOracle,confFileOracle, "sendtoaddress", args)

    #Print initial state of accounts
    print("[INFO] Accounts initialization ...")
    print(accounts)

    # Generate 1 block to update balance
    args = [1]
    print("[INFO] Generating 1 block ...")
    print(sendBitcoinCall(dataDirOracle,confFileOracle, "generate", args))


# arg : number of transaction per period to generate. Default is 10 transactions per second
def generateTransactions(nbTransactions = 10, period = 1):

    starttime = time.time()

    # Sender / Receiver Id order used for speedtest.
    txSenderIdOrder = []
    txReceiverIdOrder = []
    txData = []
    for i in range(nbTransactions):
        ids_ = list(accounts.keys())
        amount = random.randint(11, 20)
        senderId = random.choice(ids_)
        receiverId = random.choice(ids_)
        while(receiverId == senderId):
            receiverId = random.choice(ids_)
        

        txSenderIdOrder.append(senderId)
        txReceiverIdOrder.append(receiverId)

        receiverAddress = accounts[receiverId]['addresses'][0]
        index = idList.index(senderId)
        args = [receiverAddress, amount]

        # Send to Oracle
        #print(senderId + " sends " + str(amount) + " to " + receiverId)
        #txHash = sendBitcoinCall(dataDirs[index], confFiles[index], "sendtoaddressLSM", args)
        #print(txHash)

        # Save txData
        txData.append({ "datadir" :dataDirs[index], "conf" : confFiles[index], "method" : "sendtoaddressLSM" , "args": args})
    
    return txSenderIdOrder, txReceiverIdOrder, txData
    #time.sleep(period - ((time.time() - starttime) % period))



def readCommand():
	# construct the argument parse and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transactions",type=int, default=10, help="Number of transactions per second")
    args = vars(parser.parse_args())
    return args

# WARNING : Start all users nodes -> todo : start ./startNodes.sh before starting sppedTestCase.py

if __name__=="__main__":
    # Read and parse commands line
    args = readCommand()

    # Init bitcoin folders
    initBitcoinFolder()

    # Create new addresses and send initial balance form oracle
    initAccountAddressAndBalance()

    #while(1):
    generateTransactions(args['transactions'])
