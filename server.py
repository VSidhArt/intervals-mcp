from mcp.server.fastmcp import FastMCP
from config.settings import get_config
from utils.logging import setup_logging, get_logger

# Initialize configuration and logging
config = get_config()
setup_logging(config.logging)

logger = get_logger(__name__)
logger.info(
    "Starting Intervals.icu MCP Server - environment: %s, intervals_url: %s",
    config.environment,
    config.intervals.base_url,
)

# Create FastMCP instance with unique name
mcp = FastMCP("intervals-icu-mcp-server")
