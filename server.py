from config.settings import get_config
from utils.logging import setup_logging, get_logger
from fastmcp import FastMCP
from fastmcp.server.auth.providers.workos import AuthKitProvider

# Initialize configuration and logging
config = get_config()
setup_logging(config.logging)

logger = get_logger(__name__)
logger.info(
    "Starting Intervals.icu MCP Server - environment: %s, intervals_url: %s",
    config.environment,
    config.intervals.base_url,
)

auth_provider = AuthKitProvider(
    authkit_domain="https://sweet-portal-24-staging.authkit.app",
    base_url="http://localhost:8002"
)

# Create FastMCP instance with unique name
mcp = FastMCP("intervals-icu-mcp-server", auth=auth_provider)
