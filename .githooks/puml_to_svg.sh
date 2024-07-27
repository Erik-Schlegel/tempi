#!/bin/bash

# receive the path to the file to render as an argument
java -jar ./.githooks/plantuml.jar -tsvg $1

#add the .svg file to the commit
git add "${1%.*}.svg"
