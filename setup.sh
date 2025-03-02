#!/bin/bash

# Update apt-get package list and install ffmpeg
apt-get update
apt-get install -y ffmpeg

# Configure Streamlit credentials
mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"unknownuserfrommars@protonmail.com\"\n\
" > ~/.streamlit/credentials.toml

# Configure Streamlit server settings
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
