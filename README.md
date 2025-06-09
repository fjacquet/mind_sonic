# MindSonic

A lightweight file processing flow with poetic output, powered by [crewAI](https://crewai.com). MindSonic processes various file types and generates a poem using CrewAI's flow system. The design follows the principles of simplicity and elegance - like a haiku.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [uv](https://docs.astral.sh/uv/) for dependency management and package handling.

### Quick Start

```bash
# Install uv if you don't have it
pip install uv

# Clone the repository and navigate to it
git clone https://github.com/yourusername/mind_sonic.git
cd mind_sonic

# Set up environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

For detailed installation instructions including alternative methods, troubleshooting, and environment setup, see the [Installation Guide](documentation/INSTALLATION.md).

### Why uv?

- **Speed**: uv is significantly faster than pip for dependency resolution and installation
- **Reliability**: Better dependency resolution with fewer conflicts
- **Caching**: Efficient caching of wheels and other artifacts
- **Compatibility**: Works seamlessly with existing Python projects

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/mind_sonic/config/agents.yaml` to define your agents
- Modify `src/mind_sonic/config/tasks.yaml` to define your tasks
- Modify `src/mind_sonic/crew.py` to add your own logic, tools and specific args
- Modify `src/mind_sonic/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your flow and begin execution, run this from the root folder of your project:

```bash
crewai run
```

To visualize the flow structure:

```bash
crewai flow plot
```

This will generate a `crewai_flow.html` file that you can open in your browser to see the flow visualization.

## Design Principles

MindSonic follows these key principles:

- **Simple and easy to understand**: The code is structured with clarity as a priority
- **Light as a haiku**: Minimal, elegant, and purposeful
- **KISS (Keep It Simple, Stupid)**: Avoiding unnecessary complexity
- **YAGNI (You Aren't Gonna Need It)**: Only implementing what's needed now
- **DRY (Don't Repeat Yourself)**: Eliminating redundancy through abstraction

For more detailed information about our design principles, see the [Design Principles](documentation/DESIGN_PRINCIPLES.md) document in the documentation folder.

## Flow Structure

The MindSonic flow follows a simple pattern:

1. **List files**: Find all files in the knowledge directory
2. **Process in parallel**: Handle each file type concurrently
3. **Generate poem**: Create a poem when processing is complete

The flow is visualized in `crewai_flow.html` which you can view in any browser.

## Documentation

Additional documentation can be found in the `documentation` folder:

- [Installation Guide](documentation/INSTALLATION.md): Detailed instructions for installing and setting up the project
- [Configuration Guide](documentation/CONFIGURATION.md): Configuration options and settings
- [Design Principles](documentation/DESIGN_PRINCIPLES.md): Detailed explanation of our design philosophy
- [Project Requirements](documentation/prompt.txt): Original requirements for the project

## Support

For support, questions, or feedback regarding the {{crew_name}} Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
