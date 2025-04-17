# query/query.py

import chromadb
import sys
import os
import subprocess

# Add the project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from embed.embedding_model import model

# Connect to ChromaDB
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_collection(name="legal_docs")

def query_chroma(user_query, top_k=5):
    """ChromaDB에서 관련 판례를 검색하고, LLM으로 요약 설명을 받아 출력"""
    query_embedding = model.encode([user_query])  # 질문을 벡터로 변환

    # 유사 판례 검색
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    if results["documents"]:
        retrieved_texts = []
        for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            case_number = meta.get("caseNumber", "알 수 없음")
            retrieved_texts.append(f"📜 사례 {i+1}: 사건번호 {case_number}\n\"{doc[:500]}...\"")

        # Ollama에게 전달할 프롬프트 구성 (한글로 응답 요청)
        ollama_prompt = f"""SYSTEM: 당신은 한국 법률 전문가 AI입니다. 아래 판례들을 참고하여 사용자 질문에 대해 **한국어로 정확하고 상세하게** 설명해 주세요.

{chr(10).join(retrieved_texts)}

[사용자 질문]  
"{user_query}"

[답변]
"""

        # Ollama 실행
        response = subprocess.run(
            ["ollama", "run", "llama2", ollama_prompt],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        print("\n답변:\n")
        print(response.stdout.strip())
    else:
        print("\n관련 판례를 찾을 수 없습니다.")

# 실행 루프
if __name__ == "__main__":
    print("챗봇 실행 완\n")
    while True:
        user_query = input("질문: ")
        if user_query.lower() in ["exit", "quit"]:
            print("챗봇을 종료합니다.")
            break
        query_chroma(user_query, top_k=3)
