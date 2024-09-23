import streamlit as st
from openai import OpenAI
import random
import io
from audiorecorder import audiorecorder

# OpenAI API 키 설정
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])

# 단어 목록
words = {
    'big': '큰', 'bird': '새', 'cute': '귀여운', 'elephant': '코끼리',
    'giraffe': '기린', 'lion': '사자', 'small': '작은', 'tall': '키 큰',
    'tiger': '호랑이', 'zebra': '얼룩말'
}

# 시스템 메시지 정의
SYSTEM_MESSAGE = {
    "role": "system", 
    "content": '''
    You are an English teacher for elementary school students. Your task is to create and grade English word quizzes.
    When the user asks for a quiz, provide a random English word from the given list and ask for its meaning.
    When the user provides an answer, evaluate if it's correct and provide feedback.
    Always respond in Korean, as you're teaching Korean students.
    '''
}

# 초기화 함수
def initialize_session():
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
        st.write("내가 한 말 듣기")
        st.audio(audio.export().read())
        
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
st.title("영어 단어 학습 앱")

# 퀴즈 시작 버튼
if st.button("새로운 단어 퀴즈 시작"):
    st.session_state['current_word'] = random.choice(list(words.keys()))
    response = get_chatgpt_response(f"다음 영단어의 뜻을 물어보세요: {st.session_state['current_word']}")
    st.write(response)
    text_to_speech_openai(response)

# 음성 입력
st.write("답변을 음성으로 입력하세요:")
user_input_text = record_and_transcribe()

if user_input_text:
    st.write(f"입력된 텍스트: {user_input_text}")
    response = get_chatgpt_response(f"사용자의 답변: {user_input_text}. 정답은 {words[st.session_state['current_word']]}입니다. 정답 여부를 판단하고 피드백을 제공해주세요.")
    st.write(response)
    text_to_speech_openai(response)

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
