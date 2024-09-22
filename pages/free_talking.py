import streamlit as st
from openai import OpenAI
import io
from audiorecorder import audiorecorder

# OpenAI API 키 설정
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])

# 시스템 메시지 정의
SYSTEM_MESSAGE = {
    "role": "system", 
    "content": '''
   You are an elementary school English teacher and your name is Engling. I am an elementary school student. 
   Please practice speaking English with me. My English level is CEFR A1. When you speak English, please speak at a level that suits me.
   Only speak in English!! 
    '''
}

# 초기화 함수
def initialize_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])
    st.session_state['chat_history'] = [SYSTEM_MESSAGE]
    st.session_state['audio_data'] = []
    st.session_state['tts_data'] = []
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
        st.write("인공지능 선생님의 대답 듣기")    
        st.audio(response.content)
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# Streamlit UI
st.header("✨인공지능 영어대화 선생님 잉글링👩‍🏫")
st.markdown("**😃자유롭게 대화하기.**")
st.divider()

# 처음부터 다시하기 버튼
if st.button("처음부터 다시하기"):
    initialize_session()
    st.rerun()

# 확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요. 👆✅", expanded=False):
    st.markdown(
    """ 
    1️⃣ [녹음 시작] 버튼을 눌러 잉글링에게 말하기.<br>
    2️⃣ [녹음 완료] 버튼을 누르고 내가 한 말과 잉글링의 대답 들어보기.<br> 
    3️⃣ [녹음 시작] 버튼을 다시 눌러 대답하고 이어서 바로 질문하기.<br>
    4️⃣ 말을 하다 생각이 안나면 [잠깐 멈춤]을 누르고 생각한 후, 다시 [녹음 시작]을 누를 수 있음.
    5️⃣ 1~4번을 반복하기. 말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르기.<br>
    <br>
    🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)
    st.divider()
    st.write("🔸이번 단원과 관련하여 궁금한 점을 물어볼 수 있어요.") 
    st.write("🔸영어에 대해 전반적으로 궁금한 점을 한국어나 영어 중 원하는 말로 질문해도 돼요.")
    st.write("🔸영어로 잉글링과 자유롭게 대화할 수도 있어요.")

# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)

# 사이드바 구성
with st.sidebar:
    st.header("대화 기록")
    for message in st.session_state['chat_history'][1:]:  # 시스템 메시지 제외
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
