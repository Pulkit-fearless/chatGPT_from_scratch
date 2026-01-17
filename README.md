# chatGPT_from_scratch

## Overview
This project demonstrates how to build a robust chat application on top of a raw LLM API (Anthropic Claude). It explores concepts like context engineering, token compaction, and prompt caching.

## Features
- **CLI Chat Interface:** Interactive terminal-based chat.
- **Context Management:** Automatically estimates tokens and compacts older conversation history to stay within context limits.
- **Session Persistence:** Save and resume chat sessions.
- **Streaming:** Real-time text streaming from the API.

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key:**
   Export your Anthropic API key as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

## Usage

**Run the CLI:**
```bash
python main.py
```

**Commands:**
- Type your message and press Enter to chat.
- `/save`: Save the current session to the `data/` directory.
- `/new`: Start a fresh conversation.
- `/quit`: Exit the application.

## Development Journey
See `journey_so_far.md` for the log of our learning process and experiments.