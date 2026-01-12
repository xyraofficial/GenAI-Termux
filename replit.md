# Nexus AI Chat Application

## Overview

Nexus is a command-line AI chat application that interfaces with the Groq API to provide conversational AI capabilities. The application features a rich terminal interface with formatted output, real-time information retrieval, and Google search integration. It uses the LLaMA 3.3 70B model through Groq's API for generating responses.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure
- **Single-file architecture**: The entire application is contained in `main.py`, making it a lightweight, portable CLI tool
- **State management**: Uses a simple dictionary-based state object to track API key, conversation history, and UI theme preferences
- **Configuration persistence**: Stores user settings in a local JSON file (`nexus_config.json`)

### Core Components

1. **API Integration Layer**
   - Connects to Groq's OpenAI-compatible API endpoint (`api.groq.com`)
   - Uses the `llama-3.3-70b-versatile` model for AI responses
   - Handles API key authentication stored in local config

2. **Terminal UI Layer**
   - Built with the `rich` library for enhanced terminal formatting
   - Supports markdown rendering, syntax highlighting, panels, tables, and progress indicators
   - Configurable color themes

3. **Utility Engines**
   - Real-time information: Fetches current date/time from system
   - Search integration: Uses `googlesearch-python` for web search capabilities

### Dependency Management
- Auto-installs missing dependencies on first run using pip
- Required packages: `rich`, `requests`, `googlesearch-python`

## External Dependencies

### Third-Party Services
| Service | Purpose | Configuration |
|---------|---------|---------------|
| Groq API | LLM inference (LLaMA 3.3 70B) | Requires API key stored in `nexus_config.json` |
| Google Search | Web search functionality | Uses `googlesearch-python` library |

### Python Libraries
- **rich**: Terminal UI formatting and styling
- **requests**: HTTP client for API calls
- **googlesearch-python**: Lightweight Google search integration

### Local Storage
- **nexus_config.json**: Persists API key, conversation history, and theme preferences