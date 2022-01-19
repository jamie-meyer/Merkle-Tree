#!/usr/bin/env bash

clear
echo Executing: ./buildmtree.py \"alice, bob, carlol, david\"
sleep 1
./buildmtree.py "alice, bob, carlol, david"
cat merkle.tree
sleep 8

clear
echo Executing: ./checkinclusion.py richard
./checkinclusion.py richard
sleep 3

clear
echo Executing: ./checkinclusion.py david
./checkinclusion.py david
sleep 3

clear
echo Executing: ./checkconsitency.py \"alice, bob, carlol, david\" \"alice, bob, carlol, david, eve, fred\"
sleep 2
./checkconsistency.py "alice, bob, carlol, david" "alice, bob, carlol, david, eve, fred"
sleep 3
cat merkle.trees
sleep 8

clear
echo Executing: ./checkconsitency.py \"alice, bob, carlol, david\" \"alice, bob, david, eve, fred\"
sleep 3
./checkconsistency.py "alice, bob, carlol, david" "alice, bob, david, eve, fred"
sleep 2
cat merkle.trees
sleep 8

clear
echo Executing: ./checkconsitency.py \"alice, bob, carlol, david\" \"alice, bob, carol, eve, fred, davis\"
sleep 3
./checkconsistency.py "alice, bob, carlol, david" "alice, bob, carol, eve, fred, davis"
sleep 2
cat merkle.trees
