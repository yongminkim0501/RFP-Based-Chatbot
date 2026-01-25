import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import settings

load_dotenv()

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY

def create_rag_chain(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,         # 청크 사이즈 조절
        chunk_overlap=100,      # 오버랩 조절
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    split_documents = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    
    # [디버깅 메모] 아래 for문은 테스트 용도이므로 실제 함수 흐름에서는 생략하거나 pass 처리해야 함
    # for doc in vectorstore.similarity_search("투자"):
    #     print(doc.page_content) 

    # [5단계] 검색기(Retriever) 생성
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import tool
    from tools.using_tool import tools
    @tool
    def get_etf_details(query: str):
        """ACE ETF 상품 설명서(PDF)에서 구체적인 투자 전략, 종목, 보수 정보를 찾습니다."""
        return retriever.invoke(query)

    using_tools = tools + [get_etf_details]

    # [6~7단계] 프롬프트 및 LLM 설정 (Prompt & LLM)
    template = """당신은 한국투자증권 ACE ETF 추천 전문가입니다.
    사용자의 질문에 답하기 위해 아래 지침과 도구 활용 우선순위를 반드시 지키세요.

    [도구 활용 지약 조건]
    - **중요**: 한 번의 질의응답 과정에서 `get_search_data` 도구 호출은 **최대 3회**로 제한합니다.
    - 3회 호출 이내에 원하는 정보를 찾지 못했다면, 더 이상 검색하지 말고 그때까지 수집된 정보를 바탕으로 가장 적절한 답변을 제공하세요.

    [도구 활용 우선순위]
    1. **트렌드 파악**: 최신 유행이나 산업 동향 질문 시 `get_search_data`를 먼저 사용하세요.
    2. **상품 매칭**: `get_etf_details`(PDF)에서 정보를 찾되, 정보가 부족하면 `get_search_data`를 통해 실제 ACE ETF 상품명을 끝까지 찾아내세요.
    3. **실시간 데이터**: 최종 선정된 상품의 수치는 `get_etf_market_data`로 확인하세요.

    [답변 가이드라인]
    - "PDF에 정보가 없다"는 식의 답변은 지양하고, 검색 도구를 활용해 사용자에게 실질적인 도움을 주는 상품 정보를 제공하세요.
    - 모든 답변은 한국어로 전문적이고 친절하게 작성하세요."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    '''# [8단계] 체인 생성 (Chain)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )'''
    agent = create_openai_functions_agent(llm, using_tools, prompt)
    
    '''return rag_chain'''
    return AgentExecutor(agent=agent, tools=using_tools, verbose=True)