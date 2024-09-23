import streamlit as st
from openai import OpenAI
import random
import io
from audiorecorder import audiorecorder

# OpenAI API 키 설정
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])

# 단어 목록
words = ['big', 'bird', 'cute', 'elephant', 'giraffe', 'lion', 'small', 'tall', 'tiger', 'zebra']

# 시스템 메시지 정의
SYSTEM_MESSAGE = {
    "role": "system", 
    "content": '''
    당신은 초등학생을 위한 영어 발음 교사입니다. 다음과 같은 작업을 수행하세요:
    1. 주어진 영단어 목록에서 무작위로 단어를 선택하여 학생에게 제시합니다.
    2. 학생이 그 단어를 읽은 후, 음성을 텍스트로 변환한 결과를 받게 됩니다.
    3. 학생의 발음이 정확한지 평가하고, 친절하고 격려하는 방식으로 피드백을 제공합니다.
    4. 발음이 정확하지 않은 경우, 어떤 부분을 개선해야 하는지 조언을 줍니다.
    예시 질문: 'zebra'를 읽어보세요.
    '''
}

# 초기화 함수
def initialize_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])
    st.session_state['chat_history'] = [SYSTEM_MESSAGE]
    st.session_state['current_word'] = None
    st.session_state['initialized'] = True

# 세션 상태 초기화
if 'initialized' not in st.session_state or not st.session_state['initialized']:
    initialize_session()

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    response = st.session_state['openai_client'].chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['chat_history']
    )
    assistant_response = response.choices[0].message.content
    st.session_state['chat_history'].append({"role": "assistant", "content": assistant_response})
    return assistant_response

# 음성을 녹음하고 텍스트로 변환하는 함수
def record_and_transcribe():
    audio = audiorecorder("녹음 시작", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.session_state['recorded_audio'] = audio.export().read()  # 녹음된 오디오를 세션 상태에 저장
        st.write("내가 한 말 듣기")
        st.audio(st.session_state['recorded_audio'])  # 세션 상태에서 오디오 재생
        
        audio_bytes = io.BytesIO()
        audio.export(audio_bytes, format="wav")
        audio_file = io.BytesIO(audio_bytes.getvalue())
        audio_file.name = "audio.wav"
        transcription = st.session_state['openai_client'].audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text
    
    return None

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    try:
        response = st.session_state['openai_client'].audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )
        st.write("선생님의 대답 듣기")    
        st.audio(response.content)
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# Streamlit UI
st.title("영어 발음 학습 앱")

# 새로운 단어 제시 버튼
if st.button("새로운 단어 받기"):
    st.session_state['current_word'] = random.choice(words)
    st.session_state['recording_started'] = False  # 녹음 버튼 상태 초기화
    st.session_state['recorded_audio'] = None  # 녹음된 오디오 초기화
    response = get_chatgpt_response(f"다음 영단어를 학생에게 읽어보라고 요청하세요: {st.session_state['current_word']}")
    st.write(response)
    text_to_speech_openai(response)

# 현재 단어 표시
if st.session_state['current_word']:
    st.write(f"현재 단어: **{st.session_state['current_word']}**")

# 음성 입력
if st.session_state['current_word'] and not st.session_state.get('recording_started', False):
    st.write("단어를 읽고 녹음해주세요:")
    user_input_text = record_and_transcribe()
    st.session_state['recording_started'] = True  # 녹음 버튼 상태 업데이트

    if user_input_text:
        st.write(f"인식된 텍스트: {user_input_text}")
        response = get_chatgpt_response(f"학생이 '{st.session_state['current_word']}'를 읽었고, 인식된 텍스트는 '{user_input_text}'입니다. 발음의 정확성을 평가하고 피드백을 제공해주세요.")
        st.write(response)
        text_to_speech_openai(response)

# 녹음된 오디오가 있으면 재생바 표시
if st.session_state.get('recorded_audio'):
    st.write("내가 한 말 듣기")
    st.audio(st.session_state['recorded_audio'])

# 사이드바 구성
with st.sidebar:
    st.header("대화 기록")
    for message in st.session_state['chat_history'][1:]:  # 시스템 메시지 제외
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])

# 처음부터 다시하기 버튼
if st.button("처음부터 다시하기", type="primary"):
    initialize_session()
    st.rerun()
    
    
 
