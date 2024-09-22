import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from audiorecorder import audiorecorder
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    # ... (이전 코드와 동일)

# 음성을 녹음하고 텍스트로 변환하는 함수
def record_and_transcribe():
    audio = audiorecorder("녹음 시작", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.session_state['last_recording'] = audio  # 마지막 녹음 저장
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.write("내가 한 말 듣기")
        st.audio(audio.export().read()) 
        
        # 녹음한 오디오를 파일로 저장
        audio_file_path = Path("recorded_audio.wav")
        audio.export(str(audio_file_path), format="wav")

        # Whisper API를 사용해 음성을 텍스트로 변환
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    
    return None

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    # ... (이전 코드와 동일)

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'last_recording' not in st.session_state:
    st.session_state['last_recording'] = None

# 메시지 출력 함수
def display_messages():
    # ... (이전 코드와 동일)

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어대화 선생님 잉글링👩‍🏫")
st.markdown("**💕감정이나 느낌에 대한 대화하기**")
st.divider()

# 확장 설명
# ... (이전 코드와 동일)

# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        st.session_state['chat_history'].append({"role": "user", "content": user_input_text})
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)
            st.session_state['chat_history'].append({"role": "chatbot", "content": response})    

with col2:
    if st.button("처음부터 다시하기", type="primary"):
        st.session_state['chat_history'] = []
        st.session_state['last_recording'] = None  # 마지막 녹음 초기화
        # 녹음된 음성 파일 삭제
        if os.path.exists("recorded_audio.wav"):
            os.remove("recorded_audio.wav")
        if os.path.exists("speech.mp3"):
            os.remove("speech.mp3")
        st.rerun()

# 사이드바 구성
with st.sidebar:
    # 메시지 표시
    display_messages()

# 마지막 녹음 재생 (필요한 경우)
if st.session_state['last_recording'] is not None:
    st.audio(st.session_state['last_recording'].export().read())
