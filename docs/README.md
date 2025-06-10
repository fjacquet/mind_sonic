# MindSonic Documentation

This folder contains documentation for the MindSonic project.

## Contents

- [Installation Guide](INSTALLATION.md): Detailed instructions for installing and setting up the project
- [Configuration Guide](CONFIGURATION.md): Configuration options and settings for the project
- [Design Principles](DESIGN_PRINCIPLES.md): Detailed explanation of our design philosophy and coding standards
- [Project Requirements](prompt.txt): Original requirements for the project

## Project Structure

MindSonic follows a modular architecture:

```
mind_sonic/
├── documentation/       # Project documentation
├── src/
│   └── mind_sonic/     # Main source code
│       ├── crews/      # CrewAI crew definitions
│       ├── models.py   # Data models
│       ├── utils.py    # Utility functions
│       └── main.py     # Main flow implementation
├── knowledge/          # Directory for files to be processed
└── archive/           # Directory for processed files
```

## Flow Visualization

Run `crewai flow plot` to generate a visual representation of the flow in `crewai_flow.html`.
