import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool

from config import settings

def get_web_search_tool(k=5):
    """
    Tavily 검색 도구를 생성합니다.
    k : 가져올 검색 결과의 개수
    """
    os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY

    search_tool = TavilySearchResults(
        k = k,
        search_depth = "advanced"
    )

    return search_tool