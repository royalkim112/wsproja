docker pull chromadb/chroma                 # pull official docker image
docker run -p 8000:8000 chromadb/chroma     # run container on 8000 port

uvicorn scripts.query.query_api:app --host 0.0.0.0 --port 8001

cd ai-lawyer-ui
npx expo start --web