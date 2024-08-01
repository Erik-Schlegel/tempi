# Developer Setup

## Before committing changes to .puml files, run `./githooks/install_tooling.sh`

## Rendering PlantUML Documentation
- In order to iterate quickly locally:
  - NOTE!! This renders puml content in the cloud -- not private!!
  - `sudo apt install graphviz plantuml`
  - Install VSCode extension: "PlantUML (by jebbs)".
  - In .puml file, ctrl + p
  - Vscode will render a live-reloading preview.

- To render .puml files securely as svg files from command line:
  - See the body of the .githooks/pre-commit script.
  - We'll end up manually calling puml_to_svg.sh <filePath/name.puml> each time the file updates
  - TODO: Low Priority - Rebuild svgs on puml change to support secure svg render.
