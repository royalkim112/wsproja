from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import requests
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from embed.embedding_model import model  # 너가 만든 임베딩 모델

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChromaDB 연결
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_collection(name="legal_docs")

# 요청 데이터 정의
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

@app.post("/query")
async def query(request: QueryRequest):
    user_query = request.question
    top_k = request.top_k

    try:
        # 사용자 질문 임베딩
        query_embedding = model.encode([user_query])

        # 관련 문서 검색
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        if results["documents"]:
            retrieved_texts = []
            for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
                case_number = meta.get("caseNumber", "알 수 없음")
                retrieved_texts.append(f"📜 사례 {i+1}: 사건번호 {case_number}\n\"{doc[:500]}...\"")

            # Ollama에게 보낼 프롬프트 구성
            ollama_prompt = f"""
                            당신은 한국 법률 전문가 AI입니다. 반드시 **한국어로만 답변**해 주세요.
                            아래 판례들을 참고하여 사용자의 질문에 대해 정확하고 친절하게 설명해 주세요.

{chr(10).join(retrieved_texts)}

[사용자 질문]  
"{user_query}"

[답변]
"""

            # Ollama 서버로 HTTP POST 요청
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": ollama_prompt,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {"answer": data["response"].strip()}
            else:
                return {"error": f"Ollama 응답 실패: {response.status_code}"}

        else:
            return {"answer": "관련 판례를 찾을 수 없습니다."}

    except Exception as e:
        return {"error": str(e)}
