# MindSonic Installation Guide

This guide provides detailed instructions for installing and setting up the MindSonic project.

## Prerequisites

- Python >=3.10 <3.13
- Git (for cloning the repository)
- OpenAI API key

## Installation Methods

### Method 1: Installing with uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast, reliable Python package installer and resolver that significantly improves the installation experience.

#### Step 1: Install uv

```bash
# Using pip
pip install uv

# On macOS with Homebrew
brew install uv
```

#### Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/mind_sonic.git
cd mind_sonic
```

#### Step 3: Create a Virtual Environment and Install Dependencies

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Method 2: Using crewAI CLI

If you have the crewAI CLI installed, you can use it for a simplified installation:

```bash
# Navigate to the project directory
cd mind_sonic

# Install dependencies
crewai install
```

### Method 3: Traditional pip Installation

If you prefer using traditional pip:

```bash
# Clone the repository
git clone https://github.com/yourusername/mind_sonic.git
cd mind_sonic

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Environment Setup

Create a `.env` file in the project root with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Directory Structure Setup

Ensure the following directories exist for proper operation:

```bash
# Create knowledge directories
mkdir -p knowledge/txt knowledge/csv knowledge/docx knowledge/html knowledge/md knowledge/pdf knowledge/pptx knowledge/xlsx

# Create archive directory
mkdir -p archive
```

## Verifying Installation

To verify that everything is installed correctly:

```bash
# Run a simple test
python -c "from mind_sonic.main import plot; plot()"
```

This should generate a `crewai_flow.html` file that visualizes the flow structure.

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'mind_sonic'**
   - Make sure you've installed the package with `-e` flag
   - Verify that your virtual environment is activated

2. **OpenAI API Key Issues**
   - Check that your `.env` file is in the correct location
   - Verify that the API key is valid and has sufficient credits

3. **Vector Database Errors**
   - Ensure the storage directory exists and is writable
   - Check that the correct dependencies are installed for your chosen vector database

### Getting Help

If you encounter issues not covered here, please:

- Check the [CrewAI documentation](https://docs.crewai.com)
- Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- Open an issue on the project repository
