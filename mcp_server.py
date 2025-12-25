# Main MCP server file
import argparse
import logging
import os
from typing import Callable, cast
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
import uvicorn

# Import the interface and the concrete implementation
from src.data_source_interface import FinancialDataSource
from src.baostock_data_source import BaostockDataSource
from src.utils import setup_logging

# 导入各模块工具的注册函数
from src.tools.stock_market import register_stock_market_tools
from src.tools.financial_reports import register_financial_report_tools
from src.tools.indices import register_index_tools
from src.tools.market_overview import register_market_overview_tools
from src.tools.macroeconomic import register_macroeconomic_tools
from src.tools.date_utils import register_date_utils_tools
from src.tools.analysis import register_analysis_tools
from src.tools.helpers import register_helpers_tools

# --- Logging Setup ---
# Call the setup function from utils
# You can control the default level here (e.g., logging.DEBUG for more verbose logs)
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
# Instantiate the data source - easy to swap later if needed
active_data_source: FinancialDataSource = BaostockDataSource()

# --- Get current date for system prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

# --- FastMCP App Initialization ---
app = FastMCP(
    name="a_share_data_provider",
    instructions=f"""今天是{current_date}。提供中国A股市场数据分析工具。此服务提供客观数据分析，用户需自行做出投资决策。数据分析基于公开市场信息，不构成投资建议，仅供参考。

⚠️ 重要说明:
1. 最新交易日不一定是今天，需要从 get_latest_trading_date() 获取
2. 请始终使用 get_latest_trading_date() 工具获取实际当前最近的交易日，不要依赖训练数据中的日期认知
3. 当分析"最近"或"近期"市场情况时，必须首先调用 get_market_analysis_timeframe() 工具确定实际的分析时间范围
4. 任何涉及日期的分析必须基于工具返回的实际数据，不得使用过时或假设的日期
""",
    host="0.0.0.0",
    # Specify dependencies for installation if needed (e.g., when using `mcp install`)
    # dependencies=["baostock", "pandas"]
)

# --- 注册各模块的工具 ---
register_stock_market_tools(app, active_data_source)
register_financial_report_tools(app, active_data_source)
register_index_tools(app, active_data_source)
register_market_overview_tools(app, active_data_source)
register_macroeconomic_tools(app, active_data_source)
register_date_utils_tools(app, active_data_source)
register_analysis_tools(app, active_data_source)
register_helpers_tools(app)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request, call_next):
        auth_header = request.headers.get("authorization", "")
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or token.strip() != self._token:
            return PlainTextResponse("Unauthorized", status_code=401)
        return await call_next(request)


def _build_streamable_http_app(fastmcp_app: FastMCP, bearer_token: str | None) -> Starlette:
    streamable_app_factory = getattr(fastmcp_app, "streamable_http_app", None)
    if streamable_app_factory is None or not callable(streamable_app_factory):
        raise RuntimeError(
            "Streamable HTTP transport requires a newer MCP SDK. "
            "Please upgrade the 'mcp' package."
        )

    streamable_app = cast(Callable[[], Starlette], streamable_app_factory)()
    if bearer_token:
        streamable_app.add_middleware(BearerAuthMiddleware, token=bearer_token)
    return streamable_app


def _run_streamable_http(
    fastmcp_app: FastMCP,
    bearer_token: str | None,
    host: str | None,
    port: int | None,
) -> None:
    asgi_app = _build_streamable_http_app(fastmcp_app, bearer_token)
    resolved_host = host or fastmcp_app.settings.host
    resolved_port = port or fastmcp_app.settings.port
    uvicorn.run(
        asgi_app,
        host=resolved_host,
        port=resolved_port,
        log_level=fastmcp_app.settings.log_level.lower(),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A-Share MCP Server")
    parser.add_argument(
        "--transport",
        default=os.getenv("A_SHARE_TRANSPORT", "stdio"),
        choices=["stdio", "sse", "streamable-http"],
        help="Transport to use (default: stdio).",
    )
    parser.add_argument("--host", default=None, help="HTTP host override.")
    parser.add_argument("--port", type=int, default=None, help="HTTP port override.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    bearer_token = os.getenv("A_SHARE_BEARER_TOKEN")
    env_host = os.getenv("A_SHARE_HOST")
    env_port = os.getenv("A_SHARE_PORT")

    if env_host and not args.host:
        app.settings.host = env_host
    if env_port and not args.port:
        try:
            app.settings.port = int(env_port)
        except ValueError as exc:
            raise ValueError("A_SHARE_PORT must be an integer.") from exc

    if args.transport == "streamable-http":
        logger.info(
            "Starting A-Share MCP Server via streamable HTTP on %s:%s... Today is %s",
            args.host or app.settings.host,
            args.port or app.settings.port,
            current_date,
        )
        _run_streamable_http(app, bearer_token, args.host, args.port)
        return

    logger.info(
        "Starting A-Share MCP Server via %s... Today is %s",
        args.transport,
        current_date,
    )
    app.run(transport=args.transport)


# --- Main Execution Block ---
if __name__ == "__main__":
    main()
