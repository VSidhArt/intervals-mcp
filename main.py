from server import mcp
import tools.activities  # noqa: F401
import tools.wellness  # noqa: F401

if __name__ == "__main__":
    mcp.run(transport="stdio")
