#!/bin/sh

# Install packages required to render plantuml c4model diagrams to svg
sudo apt update && \
  sudo apt install -y default-jre graphviz plantuml && \
  if [ ! -f plantuml.jar ]; then
    wget https://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O ./.githooks/plantuml.jar
  fi