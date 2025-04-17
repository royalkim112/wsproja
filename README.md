# AI 변호사

## Korean law based RAG

### 개발환경

- Vector DB : ChromaDB, Docker
- LLM : LLAMA2, OLLAMA

#### 개발 Diagram 예시

┌──────────────────────────────────────────┐
│ Legal Docs │
└──────────────────────────────────────────┘
| Preprocess
v
┌────────────────────────────────────────────────────────┐
│ Document Chunking & Embedding (Python Scripts) │
│ • Splits text into chunks │
│ • Uses local embedding model to produce vectors │
└────────────────────────────────────────────────────────┘
|
| Insert
v
┌────────────────────────────────────────────────────────┐
│ Chroma Vector Database │
│ • Stores embeddings & metadata │
│ • Handles similarity search │
└────────────────────────────────────────────────────────┘
^
| Query embedding
┌────────────────────────────────────────────────────────┐
│ Query Handling (Python + Ollama + Chroma) │
│ 1) Receive user query │
│ 2) Embed query │
│ 3) Retrieve top chunks from Chroma │
│ 4) Build prompt with context │
│ 5) Send to Ollama LLM │
│ 6) Return LLM answer to the user │
└────────────────────────────────────────────────────────┘

#### 사용방법

1. ChromaDB 구축
2. Vector Embedding -> embed_store.py 실행
3. query.py 실행 전, shell ollama 경로 설정 set PATH=%PATH%;C:\Users\사용자\AppData\Local\Programs\Ollama\
4.

#### 개발일지

2025-03-11: Vector Storage 환경 설정

2025-03-15: 환경 구상 설계 - Vector Storage : ChromaDB - LLM Hosting : OLLAMA

2025-03-16: python 3.11 rolldown, Prototype구축, OLLAMA 구축

##### 데이터 출처

- https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=99
- https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71723
- https://huggingface.co/datasets/joonhok-exo-ai/korean_law_open_data_precedents
- https://github.com/lbox-kr/lbox-open
