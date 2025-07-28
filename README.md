# Intervals.icu MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with intervals.icu fitness tracking data.

## Features

- Fetch activities data with date filtering
- Retrieve wellness metrics with date filtering
- Clean data output (removes empty/null values)
- Basic authentication with intervals.icu API

## Requirements

- Python 3.12+
- UV package manager
- Intervals.icu API key
- Your intervals.icu athlete ID

## Installation

### 1. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup Project

```bash
git clone <repository-url>
cd intervals-mcp
uv sync
```

### 3. Get Your Intervals.icu Credentials

1. Go to [intervals.icu/settings](https://intervals.icu/settings)
2. Scroll down to "Developer Settings"
3. Generate an API key
4. Note your athlete ID (e.g., `i335136` from your profile URL)

### 4. Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/intervals-mcp",
        "run",
        "main.py"
      ],
      "env": {
        "INTERVALS_API_KEY": "your-api-key-here",
        "INTERVALS_ATHLETE_ID": "your-athlete-id"
      }
    }
  }
}
```

Replace:
- `/path/to/intervals-mcp` with the absolute path to this repository
- `your-api-key-here` with your intervals.icu API key
- `your-athlete-id` with your athlete ID (e.g., `i335136`)

### 5. Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

## Usage

Once configured, you can use these tools in Claude Desktop:

### Get Activities
```
Get my activities from 2025-07-28
```

### Get Wellness Data
```
Show my wellness data from 2025-07-01 to 2025-07-28
```

## Available Tools

### `get_activities(oldest_date, newest_date=None)`
Fetches activities from intervals.icu.

**Parameters:**
- `oldest_date` (required): Start date in YYYY-MM-DD format
- `newest_date` (optional): End date in YYYY-MM-DD format

### `get_wellness(oldest_date, newest_date=None)`
Fetches wellness metrics from intervals.icu.

**Parameters:**
- `oldest_date` (required): Start date in YYYY-MM-DD format
- `newest_date` (optional): End date in YYYY-MM-DD format

## Development

### Testing the Server

```bash
# Test imports and basic structure
INTERVALS_API_KEY=test_key INTERVALS_ATHLETE_ID=i335136 uv run python -c "import tools.activities; import tools.wellness; print('OK')"

# Run the server locally
INTERVALS_API_KEY=your_key INTERVALS_ATHLETE_ID=your_id uv run main.py
```

### Project Structure

```
intervals-mcp/
├── pyproject.toml          # UV project configuration
├── main.py                 # Entry point
├── server.py               # FastMCP server instance
├── tools/
│   ├── activities.py       # Activities data tool
│   └── wellness.py         # Wellness data tool
└── utils/
    └── intervals_client.py # HTTP client with authentication
```

## API Documentation

For more information about the intervals.icu API, visit:
- [API Documentation](https://intervals.icu/api-docs.html)
- [Community Forum](https://forum.intervals.icu/t/api-access-to-intervals-icu/609)

## License

This project is open source and available under the MIT License.