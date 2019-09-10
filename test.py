import os
import subprocess
import time


BITCOIN_CONF = ('-regtest', '-daemon', '-rpcpassword=test', '-rpcport=8332')


'''
This code is written in python2.7, and its purpose is to demonstrate
how to call another contract from within a contract
'''


def gen_bitcoin_command(exe, *args):
    command = [exe] + list(BITCOIN_CONF)
    if args:
        command += list(args)

    return command


def run_script():

    '''
    First we have to generate 101 blocks, because the new mined bitcoin (coinbase)
    need to wait 100 blocks before it can be spent
    '''
    subprocess.check_output(gen_bitcoin_command('bitcoin-cli', 'generate', '101'))

    '''
    Now we deploy the two contract: hello.c and caller.c
    and the scenario is caller.c will call hello.c

    subprocess.check_output() will spawn a process to execute a command
    and return the string written to stdout

    gen_bitcoin_command is just a helpful function to return the bitcoin command
    in the way check_ouput() requires, which is a just list.

    So in this case, it is equal to run
    bitcoin-cli -regtest -daemon -rpcpassword=test -rpcport=12345 deplycontract `path_to_hello.c` INIT
    in terminal
    
    The part from -regtest to -rpcport=12345 is just passing configure arguments to bitcoin-cli
    this part may change if you have different configuration, but in this example,
    we're starting a whole new bitcoind process with this particular configuration.

    And the deploycontract `path_to_hello.c` INIT is how to delpoy a contract
    '''

    hello_path = os.path.join(os.getcwd(), 'hello.c')
    caller_path = os.path.join(os.getcwd(), 'caller.c')

    print('deploying hello.c')
    r = subprocess.check_output(
        gen_bitcoin_command(
            'bitcoin-cli', 
            'deploycontract', 
            hello_path,
            'INIT',
        )
    )
    print(r)

    '''
    We save the contract_id for later use, and generate 1 block to include the deploycontract transaction
    '''
    hello_contract_id = r[r.find('contract address'):].split('\n')[0].split(':')[1].strip()[1:-1]
    subprocess.check_output(gen_bitcoin_command('bitcoin-cli', 'generate', '1'))

    '''
    We do the similar thing to deploy caller.c
    '''
    print('deploying caller.c')
    r = subprocess.check_output(
        gen_bitcoin_command(
            'bitcoin-cli', 
            'deploycontract', 
            caller_path,
            'INIT',
        )
    )
    print(r)

    caller_contract_id = r[r.find('contract address'):].split('\n')[0].split(':')[1].strip()[1:-1]
    subprocess.check_output(gen_bitcoin_command('bitcoin-cli', 'generate', '1'))

    '''
    Now we give the caller.c contract some bitcoin
    This is important because a contract needs to have money
    so it can create a transaction to call another contract

    Notice we use the rpc `sendtocontract` to send bitcoin to `caller_contract_id`
    this is how we send money to a contract
    '''
    print('Give caller money')
    r = subprocess.check_output(
        gen_bitcoin_command(
            'bitcoin-cli', 
            'sendtocontract', 
            caller_contract_id,
            '10',
        )
    )
    print(r)
    subprocess.check_output(gen_bitcoin_command('bitcoin-cli', 'generate', '1'))

    '''
    Finally, we can use caller.c to call hello.c, which is done by
    the normal way we call a contract: the `callcontract` rpc
    In fact, it is same as how we call any contract, except that this contract will
    call another contract
    '''
    print('Contract call contract')
    r = subprocess.check_output(
        gen_bitcoin_command(
            'bitcoin-cli',
            'callcontract',
            caller_contract_id,
            hello_contract_id,
        )
    )
    print(r)
    subprocess.check_output(gen_bitcoin_command('bitcoin-cli', 'generate', '1'))


def main():
    '''
    In this example, we will start a new bitcoind and stop it after the demo is completed.
    Be sure to remove the /regtest directory if it already exists in 
    default data directory (~/.bitcoin/regtest)
    '''
    subprocess.call(gen_bitcoin_command('bitcoind'))
    print('Waiting for bitcoind warm-up')
    time.sleep(3)

    try:
        run_script()
    except Exception as e:
        print(e)
    finally:
        subprocess.call(gen_bitcoin_command('bitcoin-cli', 'stop'))


if __name__ == '__main__':
    main()