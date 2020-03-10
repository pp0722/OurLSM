#!/bin/bash


if [ "$2" == "fisc" ];then
        bitcoin-cli callcontract $1 transfer 0xA 0xB 1000
        bitcoin-cli callcontract $1 transfer 0xA 0xB 2000
        bitcoin-cli callcontract $1 transfer 0xB 0xC 1000
        bitcoin-cli callcontract $1 transfer 0xC 0xD 4000
        bitcoin-cli callcontract $1 transfer 0xD 0xE 4000
        bitcoin-cli callcontract $1 transfer 0xE 0xF 4000
        bitcoin-cli callcontract $1 transfer 0xF 0xG 4000
        bitcoin-cli callcontract $1 transfer 0xG 0xH 4000
        bitcoin-cli callcontract $1 transfer 0xH 0xA 4000
        bitcoin-cli callcontract $1 transfer 0xA 0xB 1000
else

        
        bitcoin-cli callcontract $1 transfer 0xA 0xB 5000
	sleep 0.5
        bitcoin-cli callcontract $1 transfer 0xB 0xC 6000
	sleep 0.5
        bitcoin-cli callcontract $1 transfer 0xB 0xC 30000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xC 0xD 8000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xC 0xE 80000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xD 0xE 7000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xA 0xC 6000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xE 0xA 8000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xE 0xB 100000
        sleep 0.5
       	bitcoin-cli callcontract $1 transfer 0xD 0xA 5000


fi


bitcoin-cli callcontract $1 accounts
bitcoin-cli callcontract $1 activequeue
bitcoin-cli callcontract $1 accountqueue
bitcoin-cli callcontract $1 gridlock

