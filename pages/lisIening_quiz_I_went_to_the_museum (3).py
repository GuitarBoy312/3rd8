import streamlit as st
from openai import OpenAI
import random
import base64

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    answer1 = random.choice([" I went to the history museum.", "I played badminton.", " I watched a movie."," I went to the space center."," I made a car.","I went fishing.","I went shopping","I went to the park.","I went to the library.","I went to the museum.","I played soccer","I played basketball", "I played baseball","I played tennis"])       
    question_format = (                          
 f'''
대화를 듣고 어제 뭘했는지 또는 거기서 뭘 했는지에 관해 묻는 질문,
예시:
 ''')
    
    key_expression = (f'''
A:What did you do yesterday?
B:{answer1}
A:What did you do there?
B:.......
''')
    prompt = f"""{key_expression}과 같은 구문을 사용 하는 CEFR A1 수준의 간단한 영어 대화를 생성해주세요. 
    영어 대화를 생성할 때, 마지막 대화 내용은 알려주지 말고대화 내용에 관한 객관식 질문으로 만들어야 합니다. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개 입니다. 
    A와 B가 대화할 때 상대방의 이름을 부르면서 대화를 합니다. 
    영어 대화는 A와 B가 각각 1번 또는 2번 말하고 끝납니다.
    형식:
    [영어 대화]
    A: ...
    B: ...
    A: ...
    B: ...

    [한국어 질문]
    조건: {question_format}을 만들어야 합니다. 영어 대화에서 생성된 A와 B의 이름 중 필요한 것을 골라서 질문에 사용해야 합니다.
    질문: (한국어로 된 질문) 이 때, 선택지는 한국어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    audio_bytes = response.content
    
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    
    return audio_tag

def generate_explanation(question, correct_answer, user_answer, dialogue):
    prompt = f"""
    다음 영어 대화와 관련된 질문에 대해 학생이 오답을 선택했습니다. 
    대화: {dialogue}
    질문: {question}
    정답: {correct_answer}
    학생의 답변: {user_answer}
    
    이 학생에게 왜 그들의 답변이 틀렸는지, 그리고 정답이 무엇인지 설명해주세요. 
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♂️")
st.markdown("**❓어제 한 일에 대한 듣기 퀴즈**")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 재생 막대의 ▶ 버튼을 누르고 대화를 들어보기.<br>
    재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답과 대화 스크립트 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    full_content = generate_question()
    
    dialogue, question_part = full_content.split("[한국어 질문]")
    
    question_lines = question_part.strip().split("\n")
    question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
    options = question_lines[1:5] if len(question_lines) > 1 else []
    correct_answer = ""
    
    for line in question_lines:
        if line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()
            break
    
    st.session_state.question = question
    st.session_state.dialogue = dialogue.strip()
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.question_generated = True
    
    # 새 대화에 대한 음성 생성
    st.session_state.audio_tag = text_to_speech(st.session_state.dialogue)
    
    # 페이지 새로고침
    st.rerun()

if 'question_generated' in st.session_state and st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    # 저장된 음성 태그 사용
    st.markdown("### 대화 듣기")
    st.markdown(st.session_state.audio_tag, unsafe_allow_html=True)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                    st.text(st.session_state.dialogue)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                    st.text(st.session_state.dialogue)
                    
                    # 오답 설명 생성
                    explanation = generate_explanation(
                        st.session_state.question,
                        st.session_state.correct_answer,
                        selected_option,
                        st.session_state.dialogue
                    )
                    st.markdown("### 오답 설명")
                    st.write(explanation)
            else:
                st.warning("답을 선택해주세요.")
