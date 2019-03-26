#!/bin/sh

SENT_PATH=$1
OUTPUT_FILE=$2
GAMMA=$3
WEIGHT=$4
LOWER=$5
UPPER=$6


C:/Users/utilisateur/Anaconda3/python.exe run.py $SENT_PATH $OUTPUT_FILE $GAMMA $WEIGHT $LOWER $UPPER

#chmod u+x run.sh
#bash run.sh C:\Users\utilisateur\Documents\GITHUB\TP2\code\sents_test.txt C:\Users\utilisateur\Documents\GITHUB\TP2\code\my_output.txt 0.3 0.3


