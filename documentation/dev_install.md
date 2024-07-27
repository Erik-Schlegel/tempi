# Developer Setup

## Before modifying any .puml files, be sure to run the below setup

## Setup Git hooks
```sh
git config core.hooksPath .githooks
```

## Rendering PlantUML Documentation
- There are two methods: fast IDE iteration; local render
- Fast IDE Iteration:
  - NOTE!! This renders puml content in the cloud -- not private!!
  - In order to render the plantuml diagrams in the documentation folder:
  - `sudo apt install graphviz plantuml`
  - Install VSCode extension: "PlantUML (by jebbs)".
  - In puml file, ctrl + p
- To render .puml files securely from command line (necessary for github precommit action):
   - Install necessary packages: `sudo apt install default-jre graphviz plantuml`
   - Get the plantuml jar: `wget https://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O plantuml.jar`
   - Render: `java -jar plantuml.jar -tsvg *.puml`
   - might be able to do something here with vscode actions (tasks?) and a file watcher
