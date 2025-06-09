"""
Tool for getting historical price data from Yahoo Finance.

This module provides a CrewAI-compatible tool to access historical price data
through the Yahoo Finance API using the yfinance library.
"""

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetTickerHistoryInput(BaseModel):
    """Input schema for getting ticker price history."""

    ticker: str = Field(
        ..., description="The ticker symbol (e.g., 'AAPL', 'VTI', 'BTC-USD')"
    )
    period: str = Field(
        "1y", description="Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"
    )
    interval: str = Field(
        "1d",
        description="Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo",
    )


class YahooFinanceHistoryTool(BaseTool):
    """
    Get historical price data for a financial instrument from Yahoo Finance.

    This tool retrieves historical price data for stocks, ETFs, or cryptocurrencies
    over a specified time period and interval.
    """

    name: str = "Yahoo Finance History Tool"
    description: str = (
        "Get historical price data (open, high, low, close, volume) for stocks, ETFs,"
        " or cryptocurrencies over various time periods and intervals."
    )
    args_schema: type[BaseModel] = GetTickerHistoryInput

    def _run(self, ticker: str, period: str = "1y", interval: str = "1d") -> dict:
        """Execute the Yahoo Finance historical data lookup."""
        try:
            ticker_data = yf.Ticker(ticker)
            history = ticker_data.history(period=period, interval=interval)

            if history.empty:
                return {"error": f"No historical data available for {ticker}"}

            # Format the data for easier consumption
            history_list = []
            for date, row in history.iterrows():
                history_list.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(float(row.get("Open", 0)), 2),
                        "high": round(float(row.get("High", 0)), 2),
                        "low": round(float(row.get("Low", 0)), 2),
                        "close": round(float(row.get("Close", 0)), 2),
                        "volume": int(row.get("Volume", 0)),
                    }
                )

            # Add summary statistics
            latest = history_list[-1] if history_list else {}
            earliest = history_list[0] if history_list else {}

            summary = {
                "symbol": ticker,
                "period": period,
                "interval": interval,
                "start_date": earliest.get("date", "N/A"),
                "end_date": latest.get("date", "N/A"),
                "price_change": round(
                    latest.get("close", 0) - earliest.get("close", 0), 2
                ),
                "price_change_percent": round(
                    (latest.get("close", 0) / earliest.get("close", 1) - 1) * 100, 2
                ),
                "data_points": len(history_list),
            }

            return {
                "summary": summary,
                "history": history_list[
                    -10:
                ],  # Return only last 10 data points to avoid overloading
            }
        except Exception as e:
            return {"error": f"Failed to get history for {ticker}: {str(e)}"}
