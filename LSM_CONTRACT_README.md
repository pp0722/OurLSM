# Oracle-based LSM using smart contract

# 0. Clone bitbucket repo : https://bitbucket.org/lab408/ourchain-release/src/lsm/
# Checkout on lsm branch

# 1. Start Oracle server using oracleContract.py
# By default the oracle server generate blocks every 20 seconds.
# Listen for any user connection and waiting for their LSM transactions. Upon receiving a new transaction the Oracle server will decode it and update the LSM state then call the LSM contract to run gridlock every 15 seconds.
# NB : the flag -c set the current test case which enables the Oracle to know the transaction's receiver / sender unique identifier solving temporarily the multiaddressing issue.

# ex usage: python3 oracleContract.py -c ubin


# 2. Start nodes 
# By default, 5 users nodes and 1 oracle is going to be run). Please update the data directory of each node to your own local environment.
# ex usage : ./startNodes.sh


# 3. Start test case
# Two test cases are currently available. 
# i. Bilateral test case using only 2 users and involving 2 transactions.
# ii. Ubin test case using 5 users and 10 transactions


# ex usage: ./testCase ubin


# Stop Nodes
# To properly stop all the nodes, use stopNodes.sh
# ex usage : ./stopNodes.sh

|  A |  B |  C |  D |  E |
|----|----|----|----|----|
|  3 |  4 |  5 |  4 |  3 |
| -5 |  5 |    |    |    |
|    | -6 |  6 |    |    |
|    |-30 | 30 |    |    |
|    |    | **-8** |  **8** |    |
|    |    |-80 |    |  80|
|    |    |    | -7 |   7|
| -6 |    |  6 |    |    |
|  8 |    |    |    |  -8|
|    |100 |    |    |-100|
|  **5** |    |    | **-5** |    |
