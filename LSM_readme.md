# Start oracle server. 
# Fee must be set with the -s flag.
# Enable end to end test with -e flag. Oracle absolute processing (without gridlock start waiting time) is saved in solving_speed.csv
python3 oracleServer.py -s 0.001 -e


# Start  Nodes
./startNodes

# Optional : Start speed test (speed test intefrated in oracleServer.py)
# Set -t flag to configure number of transaction per second. Default is 10 transactions per second
python3 speedTestCase.py -t 10




# Stop Nodes
./stopNodes