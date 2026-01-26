import yfinance as yf
from langchain.tools import tool

@tool
def get_etf_market_data(ticker: str):
    """
    특정 ETF의 실시간 금융 수치 데이터를 가져옵니다.
    반드시 '069500.KS'와 같은 정확한 티커 형식을 입력해야 합니다.
    한국 종목은 숫지 뒤에 '.KS'를 붙이고, 미국 종목은 'SPY'처럼 입력하세요.
    """
    try:
        etf = yf.Ticker(ticker)
        info = etf.fast_info

        # [수정] 통화 단위(Currency)를 동적으로 처리합니다.
        currency_map = {"KRW": "원", "USD": "$", "JPY": "¥"}
        unit = currency_map.get(info.currency, info.currency)

        # [수정] 가격이 소수점일 수 있으므로 포맷팅을 정교화합니다.
        price = f"{info.last_price:,.2f}" if info.currency == "USD" else f"{info.last_price:,.0f}"

        return {
            "종목명": ticker,
            "현재가": f"{price}{unit}",
            "전일대비변동": f"{((info.last_price - info.previous_close) / info.previous_close * 100):.2f}%",
            "거래량": f"{info.last_volume:,.0f}주",
            "통화": info.currency
        }
    except Exception as e:
        return f"티커 '{ticker}'에 대한 데이터를 찾을 수 없습니다. 정확한 티커인지 확인하세요: {e}"