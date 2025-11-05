"""
MCP服务器主入口文件。

该文件负责初始化并运行一个FastMCP应用，专门为中国A股市场提供数据服务。
主要执行以下任务：
1.  **设置日志**: 配置全局日志记录器。
2.  **依赖注入**: 实例化数据源（例如BaostockDataSource），并将其注入到各个工具模块中。
3.  **MCP应用初始化**: 创建FastMCP实例，并设置服务器名称和描述。
4.  **工具注册**: 从`src.tools`目录导入并注册所有可用的数据查询和分析工具。
5.  **服务器启动**: 在`if __name__ == "__main__":`块中，通过标准输入/输出（stdio）启动服务器，使其能与MCP客户端（如IDE插件、CherryStudio等）通信。
"""
import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

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
    server_name="a_share_data_provider",
    description=f"""今天是{current_date}。提供中国A股市场数据分析工具。此服务提供客观数据分析，用户需自行做出投资决策。数据分析基于公开市场信息，不构成投资建议，仅供参考。

⚠️ 重要说明:
1. 最新交易日不一定是今天，需要从 get_latest_trading_date() 获取
2. 请始终使用 get_latest_trading_date() 工具获取实际当前最近的交易日，不要依赖训练数据中的日期认知
3. 当分析"最近"或"近期"市场情况时，必须首先调用 get_market_analysis_timeframe() 工具确定实际的分析时间范围
4. 任何涉及日期的分析必须基于工具返回的实际数据，不得使用过时或假设的日期
""",
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

# --- Main Execution Block ---
if __name__ == "__main__":
    logger.info(
        f"Starting A-Share MCP Server via stdio... Today is {current_date}")
    # Run the server using stdio transport, suitable for MCP Hosts like Claude Desktop
    app.run(transport='stdio')
