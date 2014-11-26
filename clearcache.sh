#!/bin/bash
#echo $password | sudo -S su
kill -USR1 $(pgrep polipo)
sleep 0.1
polipo -x
kill -USR2 $(pgrep polipo)
