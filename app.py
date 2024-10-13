import streamlit as st

from llama_index.core.llms import ChatMessage


import logging
import time
from llama_index.llms.ollama import Ollama

logging.basicConfig(level = logging.INFO)

if 'message' not in st.session_state:
    st.session_state.messages = [] # message가 없으면 리스트 비워주기

def stream_chat(model, message):
    try:
        llm = Ollama(model=model, request_timeout=120)
        resp = llm.stream_chat(message)
        response = ""
        response_placeholder = st.empty()
        
        for r in resp:
            response += r.delta
            response_placeholder.write(response)
        logging.info(f"Model : {model}, Message: {message}, Response : {response}")
        return response

    except Exception as e:
        logging.error(f"streaming error occur {str(e)}")
        raise e


def main():
    st.title("Joker와 함께하는 LLM 모델 하하")
    logging.info("앱 시작")
    
    model = st.sidebar.selectbox("모델을 선택해주세요", ["llama3.2", "ddas"])
    logging.info(f"선택한 모델 : {model}")
    
    if prompt := st.chat_input("질문해 주세요"):
        st.session_state.messages.append({"role":"user", "content": prompt})
        logging.info(f"유저 인풋 : {prompt}")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                start_time = time.time()
                logging.info("응답 생성중")
        
        with st.spinner("응답 생성하는 중..."):
            try:
                messages = [ChatMessage(role=msg["role"], content = msg["content"]) for msg in st.session_state.messages]
                response_message = stream_chat(model, messages)
                duration = time.time() - start_time
                response_message_with_duration = f"{response_message}\n\nDuration: {duration:0.2f} seconds"
                st.session_state.messages.append({"role" : "assistant", "content" : response_message_with_duration})
                st.write(f"Duration : {duration:.2f} seconds")
            except Exception as e:
                st.session_state.messages.append({"role" : "assistant", "content": str(e)})
                logging.error(f"streaming error occur {str(e)}")
                raise e
        

if __name__ == "__main__":
    main()