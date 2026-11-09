import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_SERVER = StdioServerParameters(command="python", args=["-m", "tools.mcp_server"])


def _text_of(result):
    parts = []
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts) if parts else str(result)


def _to_openai_schema(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


async def _adiscover():
    async with stdio_client(_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resp = await session.list_tools()
            return list(resp.tools)


async def _acall(name, arguments):
    async with stdio_client(_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            return _text_of(result)


def call_mcp_tool(name, arguments):
    return asyncio.run(_acall(name, arguments))


def _make_wrapper(name):
    return lambda **kwargs: call_mcp_tool(name, kwargs)


def discover_mcp_tools():
    tools = asyncio.run(_adiscover())
    schemas = [_to_openai_schema(t) for t in tools]
    registry = {t.name: _make_wrapper(t.name) for t in tools}
    return schemas, registry
