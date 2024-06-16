#!/bin/bash

# install ollama via homebrew. See https://brew.sh/ if needed
brew install ollama
ollama serve

# pull some ollama models
ollama pull phi:latest
#ollama pull llama3:latest
#ollama pull llava:latest

# create a python virtual environment ans activate it
python3 -m venv venv
source ./venv/bin/activate

# install our package dependencies
pip3 install -r requirements.txt


