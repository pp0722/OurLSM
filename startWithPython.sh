#!/bin/bash

ourcontract-rt contracts lsm init
ourcontract-rt contracts lsm setbalance 0xA 3000
ourcontract-rt contracts lsm setbalance 0xB 4000
ourcontract-rt contracts lsm setbalance 0xC 5000
ourcontract-rt contracts lsm setbalance 0xD 4000
ourcontract-rt contracts lsm setbalance 0xE 3000



if [ "$1" = "fisc" ]
then
	echo '[bash-script] fisc case initialized'
	ourcontract-rt contracts lsm transfer 0xA 0xB 1000
	ourcontract-rt contracts lsm transfer 0xA 0xB 2000
	ourcontract-rt contracts lsm transfer 0xB 0xC 1000
	ourcontract-rt contracts lsm transfer 0xC 0xD 4000
	ourcontract-rt contracts lsm transfer 0xD 0xE 4000
	ourcontract-rt contracts lsm transfer 0xE 0xF 4000
	ourcontract-rt contracts lsm transfer 0xF 0xG 4000
	ourcontract-rt contracts lsm transfer 0xG 0xH 4000
	ourcontract-rt contracts lsm transfer 0xH 0xA 4000
	ourcontract-rt contracts lsm transfer 0xA 0xB 1000
else

	echo '[bash-script] ubin case initialized'
	ourcontract-rt contracts lsm transfer 0xA 0xB 5000
	ourcontract-rt contracts lsm transfer 0xB 0xC 6000
	ourcontract-rt contracts lsm transfer 0xB 0xC 30000
	ourcontract-rt contracts lsm transfer 0xC 0xD 8000
	ourcontract-rt contracts lsm transfer 0xC 0xE 80000
	ourcontract-rt contracts lsm transfer 0xD 0xE 7000
	ourcontract-rt contracts lsm transfer 0xA 0xC 6000
	ourcontract-rt contracts lsm transfer 0xE 0xA 8000
	ourcontract-rt contracts lsm transfer 0xE 0xB 100000
	ourcontract-rt contracts lsm transfer 0xD 0xA 5000


fi


ourcontract-rt contracts lsm accounts
ourcontract-rt contracts lsm activequeue
ourcontract-rt contracts lsm accountqueue
