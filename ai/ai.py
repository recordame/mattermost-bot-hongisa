# Llama 3 모델 다운로드
# ollama pull llama3

# GGUF 사용 및 모델 생성
# - GGUF 및 GGML : GPT(Generative Pre-trained Transformer)와 같은 언어 모델의 맥락에서 추론을 위한 모델을 저장하는 데 사용되는 파일 형식
# - GGUF 다운로드
#   https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/tree/main
# - Ollama LLM 모델 생성
#   Modelfile 파일 작성 (Modelfile.md)
#### FROM Meta-Llama-3-8B-Instruct.Q8_0.gguf
####
#### TEMPLATE """{{- if .System }}
#### <s>{{ .System }}</s>
#### {{- end }}
#### <s>Human:
#### {{ .Prompt }}</s>
#### <s>Assistant:
#### """
####
#### SYSTEM """A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."""
####
#### PARAMETER temperature 0
#### PARAMETER stop <s>
#### PARAMETER stop </s>
# - 모델 생성
#   ollama create Meta-Llama-3-8B-Instruct.Q8_0 -f Modelfile

# LLM 모델 리스트 조회
# - ollama list
# LLM 모델 실행
# - ollama run {모델명}
# 	Ex) ollama run Meta-Llama-3-8B-Instruct.Q8_0:latest

# LangChain 설치
# pip install langchain

from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3:latest")
llm.invoke("What is stock?")