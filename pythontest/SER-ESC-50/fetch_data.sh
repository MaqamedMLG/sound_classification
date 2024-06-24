#!/bin/bash

# check the directory for master.zip
# if master.zip does not exist, fetch it via download

test ! -f "master.zip" && curl -o "master.zip" "https://github.com/karoldvl/ESC-50/archive/refs/heads/master.zip"

# unzip master.zip

unzip -qq master.zip

# set up needed directories for additional test data and model storage

mkdir -p data
mkdir -p models

# change directory to data and fetch additional test data via download

cd data

curl -o "dog.wav" 'http://soundbible.com/grab.php?id=2215&type=wav'
curl -o "cat.wav" 'http://soundbible.com/grab.php?id=1954&type=wav'

cd ../
