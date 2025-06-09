"""
Tool for getting news related to financial instruments from Yahoo Finance.

This module provides a CrewAI-compatible tool to access news articles
through the Yahoo Finance API using the yfinance library.
"""

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetTickerNewsInput(BaseModel):
    """Input schema for getting news for a ticker."""

    ticker: str = Field(..., description="The ticker symbol (e.g., 'AAPL', 'BTC-USD').")
    limit: int = Field(5, description="Maximum number of news items to return.")


class YahooFinanceNewsTool(BaseTool):
    """
    Get recent news for a financial instrument from Yahoo Finance.

    This tool retrieves recent news articles related to a specific stock,
    ETF, or cryptocurrency ticker symbol.
    """

    name: str = "Yahoo Finance News Tool"
    description: str = (
        "Get recent news articles for stocks, ETFs, or cryptocurrencies, "
        "including headlines, publishers, and links to full articles."
    )
    args_schema: type[BaseModel] = GetTickerNewsInput

    def _run(self, ticker: str, limit: int = 5) -> dict:
        """Execute the Yahoo Finance news lookup."""
        try:
            ticker_data = yf.Ticker(ticker)
            
            # Get news data
            news_data = ticker_data.news
            
            if not news_data:
                return {"error": f"No news available for {ticker}"}
                
            # Format news items
            news_items = []
            for item in news_data[:limit]:
                news_item = {
                    "title": item.get("title", "N/A"),
                    "publisher": item.get("publisher", "N/A"),
                    "link": item.get("link", "N/A"),
                    "published": item.get("providerPublishTime", "N/A"),
                    "type": item.get("type", "N/A"),
                    "related_tickers": item.get("relatedTickers", []),
                }
                news_items.append(news_item)
                
            return {
                "symbol": ticker,
                "news_count": len(news_items),
                "news": news_items,
            }
        except Exception as e:
            return {"error": f"Failed to get news for {ticker}: {str(e)}"}
