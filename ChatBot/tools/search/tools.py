from tools.search.repo import *

@tool
def get_search_data(query : str):
    """
    실시간 금융 시장 트렌드, 뉴스, 특정 산업 테마(예: AI, 반도체, 금리, 대선 등)에 대한 최신 정보를 검색합니다.
    사용자가 '요즘 뜨는 테마', '시장 상황', '최신 뉴스' 등을 물어볼 때 가장 먼저 호출해야 하는 도구입니다.
    검색된 트렌드 키워드는 나중에 PDF에서 구체적인 ETF 상품을 찾을 때 핵심 근거로 사용됩니다.
    """
    search = get_web_search_tool()
    results = search.run(f"{query}")
    return results