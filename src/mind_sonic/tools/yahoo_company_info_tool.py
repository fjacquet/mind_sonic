"""
Tool for getting detailed company information from Yahoo Finance.

This module provides a CrewAI-compatible tool to access comprehensive company data
through the Yahoo Finance API using the yfinance library.
"""

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetCompanyInfoInput(BaseModel):
    """Input schema for getting company information."""

    ticker: str = Field(..., description="The ticker symbol (e.g., 'AAPL', 'MSFT').")


class YahooFinanceCompanyInfoTool(BaseTool):
    """
    Get detailed company information from Yahoo Finance.

    This tool retrieves comprehensive company data including business description,
    financial metrics, and key performance indicators.
    """

    name: str = "Yahoo Finance Company Info Tool"
    description: str = (
        "Get detailed company information including business description, "
        "key financial metrics, and company profile."
    )
    args_schema: type[BaseModel] = GetCompanyInfoInput

    def _run(self, ticker: str) -> dict:
        """Execute the Yahoo Finance company info lookup."""
        try:
            ticker_data = yf.Ticker(ticker)
            info = ticker_data.info

            # Create a focused company profile
            company_info = {
                "symbol": ticker,
                "name": info.get("longName", "N/A"),
                "industry": info.get("industry", "N/A"),
                "sector": info.get("sector", "N/A"),
                "website": info.get("website", "N/A"),
                "country": info.get("country", "N/A"),
                "employees": info.get("fullTimeEmployees", "N/A"),
                "description": info.get("longBusinessSummary", "N/A"),
                "ceo": info.get("companyOfficers", [{}])[0].get("name", "N/A")
                if info.get("companyOfficers")
                else "N/A",
            }

            # Financial metrics
            financial_metrics = {
                "market_cap": info.get("marketCap", "N/A"),
                "enterprise_value": info.get("enterpriseValue", "N/A"),
                "trailing_pe": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "peg_ratio": info.get("pegRatio", "N/A"),
                "price_to_sales": info.get("priceToSalesTrailing12Months", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),
                "enterprise_to_revenue": info.get("enterpriseToRevenue", "N/A"),
                "enterprise_to_ebitda": info.get("enterpriseToEbitda", "N/A"),
                "profit_margins": info.get("profitMargins", "N/A"),
                "revenue_growth": info.get("revenueGrowth", "N/A"),
                "earnings_growth": info.get("earningsGrowth", "N/A"),
                "return_on_assets": info.get("returnOnAssets", "N/A"),
                "return_on_equity": info.get("returnOnEquity", "N/A"),
                "total_cash": info.get("totalCash", "N/A"),
                "total_debt": info.get("totalDebt", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "current_ratio": info.get("currentRatio", "N/A"),
            }

            # Clean up N/A values
            company_info = {k: v for k, v in company_info.items() if v != "N/A"}
            financial_metrics = {
                k: v for k, v in financial_metrics.items() if v != "N/A"
            }

            return {
                "company_profile": company_info,
                "financial_metrics": financial_metrics,
            }
        except Exception as e:
            return {"error": f"Failed to get company info for {ticker}: {str(e)}"}
