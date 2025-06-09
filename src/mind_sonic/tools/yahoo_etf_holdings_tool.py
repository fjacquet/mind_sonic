"""
Tool for getting ETF holdings information from Yahoo Finance.

This module provides a CrewAI-compatible tool to access ETF holdings data
through the Yahoo Finance API using the yfinance library.
"""

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetETFHoldingsInput(BaseModel):
    """Input schema for getting ETF holdings."""

    ticker: str = Field(..., description="The ETF ticker symbol (e.g., 'VTI', 'SPY').")


class YahooFinanceETFHoldingsTool(BaseTool):
    """
    Get holdings information for an ETF from Yahoo Finance.

    This tool retrieves detailed holdings data for ETFs including
    top holdings, sector allocations, and geographical exposure.
    """

    name: str = "Yahoo Finance ETF Holdings Tool"
    description: str = (
        "Get detailed holdings information for ETFs, including top holdings, "
        "sector allocations, and asset breakdown."
    )
    args_schema: type[BaseModel] = GetETFHoldingsInput

    def _run(self, ticker: str) -> dict:
        """Execute the Yahoo Finance ETF holdings lookup."""
        try:
            ticker_data = yf.Ticker(ticker)
            info = ticker_data.info

            # Basic ETF info
            etf_info = {
                "symbol": ticker,
                "name": info.get("shortName", "N/A"),
                "category": info.get("category", "N/A"),
                "total_assets": info.get("totalAssets", "N/A"),
                "yield": info.get("yield", "N/A"),
                "ytd_return": info.get("ytdReturn", "N/A"),
                "three_year_return": info.get("threeYearAverageReturn", "N/A"),
                "five_year_return": info.get("fiveYearAverageReturn", "N/A"),
                "expense_ratio": info.get("annualReportExpenseRatio", "N/A"),
                "inception_date": info.get("fundInceptionDate", "N/A"),
            }

            # Get holdings data
            try:
                holdings = ticker_data.get_holdings()
                top_holdings = []

                if not holdings.empty:
                    # Format top 10 holdings
                    for _, row in holdings.head(10).iterrows():
                        holding = {
                            "symbol": row.get("symbol", "N/A"),
                            "name": row.get("name", "N/A"),
                            "weight": row.get("weight", "N/A"),
                        }
                        top_holdings.append(holding)
            except:
                top_holdings = []

            # Get sector data
            try:
                sector_data = ticker_data.get_sector_data()
                sectors = {}

                if not sector_data.empty:
                    for sector, weight in sector_data.items():
                        sectors[sector] = weight
            except:
                sectors = {}

            # Clean up N/A values
            etf_info = {k: v for k, v in etf_info.items() if v != "N/A"}

            return {
                "etf_info": etf_info,
                "top_holdings": top_holdings,
                "sector_allocation": sectors,
            }
        except Exception as e:
            return {"error": f"Failed to get ETF holdings for {ticker}: {str(e)}"}
