"""
MCP 服务器的分析工具。
包含用于生成股票分析报告的工具。
"""
import logging
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_df_to_markdown

logger = logging.getLogger(__name__)


def register_analysis_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册分析工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_stock_analysis(code: str, analysis_type: str = "fundamental") -> str:
        """
        提供基于数据的股票分析报告，而非投资建议。

        Args:
            code (str): 股票代码，如'sh.600000'。
            analysis_type (str, optional): 分析类型，可选'fundamental'(基本面)、'technical'(技术面)或'comprehensive'(综合)。

        Returns:
            str: 数据驱动的分析报告，包含关键财务指标、历史表现和同行业比较。
        """
        logger.info(
            f"工具 'get_stock_analysis' 已为 {code} 调用，类型={analysis_type}")

        try:
            basic_info = active_data_source.get_stock_basic_info(code=code)

            if analysis_type in ["fundamental", "comprehensive"]:
                recent_year = datetime.now().strftime("%Y")
                recent_quarter = (datetime.now().month - 1) // 3 + 1
                if recent_quarter < 1:
                    recent_year = str(int(recent_year) - 1)
                    recent_quarter = 4

                profit_data = active_data_source.get_profit_data(
                    code=code, year=recent_year, quarter=recent_quarter)
                growth_data = active_data_source.get_growth_data(
                    code=code, year=recent_year, quarter=recent_quarter)
                balance_data = active_data_source.get_balance_data(
                    code=code, year=recent_year, quarter=recent_quarter)
                dupont_data = active_data_source.get_dupont_data(
                    code=code, year=recent_year, quarter=recent_quarter)

            if analysis_type in ["technical", "comprehensive"]:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=180)
                              ).strftime("%Y-%m-%d")
                price_data = active_data_source.get_historical_k_data(
                    code=code, start_date=start_date, end_date=end_date
                )

            report = f"# {basic_info['code_name'].values[0] if not basic_info.empty else code} 数据分析报告\n\n"
            report += "## 免责声明\n本报告基于公开数据生成，仅供参考，不构成投资建议。投资决策需基于个人风险承受能力和研究。\n\n"

            if not basic_info.empty:
                report += f"## 公司基本信息\n"
                report += f"- 股票代码: {code}\n"
                report += f"- 股票名称: {basic_info['code_name'].values[0]}\n"
                report += f"- 所属行业: {basic_info['industry'].values[0] if 'industry' in basic_info.columns else '未知'}\n"
                report += f"- 上市日期: {basic_info['ipoDate'].values[0] if 'ipoDate' in basic_info.columns else '未知'}\n\n"

            if analysis_type in ["fundamental", "comprehensive"] and not profit_data.empty:
                report += f"## 基本面指标分析 ({recent_year}年第{recent_quarter}季度)\n\n"

                report += "### 盈利能力指标\n"
                if not profit_data.empty and 'roeAvg' in profit_data.columns:
                    roe = profit_data['roeAvg'].values[0]
                    report += f"- ROE(净资产收益率): {roe}%\n"
                if not profit_data.empty and 'npMargin' in profit_data.columns:
                    npm = profit_data['npMargin'].values[0]
                    report += f"- 销售净利率: {npm}%\n"

                if not growth_data.empty:
                    report += "\n### 成长能力指标\n"
                    if 'YOYEquity' in growth_data.columns:
                        equity_growth = growth_data['YOYEquity'].values[0]
                        report += f"- 净资产同比增长: {equity_growth}%\n"
                    if 'YOYAsset' in growth_data.columns:
                        asset_growth = growth_data['YOYAsset'].values[0]
                        report += f"- 总资产同比增长: {asset_growth}%\n"
                    if 'YOYNI' in growth_data.columns:
                        ni_growth = growth_data['YOYNI'].values[0]
                        report += f"- 净利润同比增长: {ni_growth}%\n"

                if not balance_data.empty:
                    report += "\n### 偿债能力指标\n"
                    if 'currentRatio' in balance_data.columns:
                        current_ratio = balance_data['currentRatio'].values[0]
                        report += f"- 流动比率: {current_ratio}\n"
                    if 'assetLiabRatio' in balance_data.columns:
                        debt_ratio = balance_data['assetLiabRatio'].values[0]
                        report += f"- 资产负债率: {debt_ratio}%\n"

            if analysis_type in ["technical", "comprehensive"] and not price_data.empty:
                report += "## 技术面分析\n\n"

                if 'close' in price_data.columns and len(price_data) > 1:
                    latest_price = price_data['close'].iloc[-1]
                    start_price = price_data['close'].iloc[0]
                    price_change = (
                        (float(latest_price) / float(start_price)) - 1) * 100

                    report += f"- 最新收盘价: {latest_price}\n"
                    report += f"- 6个月价格变动: {price_change:.2f}%\n"

                    if len(price_data) >= 20:
                        ma20 = price_data['close'].astype(
                            float).tail(20).mean()
                        report += f"- 20日均价: {ma20:.2f}\n"
                        if float(latest_price) > ma20:
                            report += f"  (当前价格高于20日均线 {((float(latest_price)/ma20)-1)*100:.2f}%)\n"
                        else:
                            report += f"  (当前价格低于20日均线 {((ma20/float(latest_price))-1)*100:.2f}%)\n"

            try:
                if not basic_info.empty and 'industry' in basic_info.columns:
                    industry = basic_info['industry'].values[0]
                    industry_stocks = active_data_source.get_stock_industry(
                        date=None)
                    if not industry_stocks.empty:
                        same_industry = industry_stocks[industry_stocks['industry'] == industry]
                        report += f"\n## 行业比较 ({industry})\n"
                        report += f"- 同行业股票数量: {len(same_industry)}\n"

            except Exception as e:
                logger.warning(f"获取行业比较数据失败: {e}")

            report += "\n## 数据解读建议\n"
            report += "- 以上数据仅供参考，建议结合公司公告、行业趋势和宏观环境进行综合分析\n"
            report += "- 个股表现受多种因素影响，历史数据不代表未来表现\n"
            report += "- 投资决策应基于个人风险承受能力和投资目标\n"

            logger.info(f"成功生成{code}的分析报告")
            return report

        except Exception as e:
            logger.exception(f"分析生成失败 for {code}: {e}")
            return f"分析生成失败: {e}"
