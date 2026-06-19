import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from gtts import gTTS
import base64
import io

# 1. 웹페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="ALL-IN-ONE 초지능 AI 비서", page_icon="🔱", layout="wide")
st.title("🔱 GHK AI")
st.subheader("사용자님 무엇을 도와드릴까요?")

# ⚠️ [중요]여기에 네 API Key를 입력해!
GEMINI_API_KEY = "AQ.Ab8RN6K3O5OXLonP6IjXCrqdEhgmpSRzuOuJmbpqNIDiOcujYA"

# 구글 AI 서버와 연결하는 클라이언트 생성
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=GEMINI_API_KEY)

# 2. AI 인격과 규칙 정의
SYSTEM_INSTRUCTION = """
너는 세계 최고의 천재 인공지능 비서야. 
[규칙]
1. 모든 답변은 아주 자연스럽고 유창하게만 작성해.
2. 문장은 명확하게 지적으로 대답해줘.
3. 기본 언어는 한국어로 답변해줘.
"""

# 3. 사이드바 설정 (이미지 업로드 및 음성 출력 옵션)
with st.sidebar:
    st.header("⚙️ 기능 컨트롤러")
    uploaded_file = st.file_uploader("📸 AI에게 보여줄 사진 업로드", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="로드된 이미지", use_container_width=True)
        st.success("이미지 인식 준비 완료!")
        
    st.markdown("---")
    speak_out = st.checkbox("🔊 AI 답변을 목소리로 읽어주기", value=False)

# 4. 대화 기록 메모리 공간
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 이전 대화 화면에 그리기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 사용자 채팅 입력 및 텍스트 대화 처리
if user_input := st.chat_input("질문, 이미지 분석, 웹 검색, 복잡한 계산 등을 요청하세요!"):
    
    # 사용자 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 답변 생성 프로세스
    with st.chat_message("assistant"):
        with st.spinner("🔱 초지능 마스터 시스템 가동 중..."):
            
            contents_payload = [user_input]
            if uploaded_file:
                contents_payload.append(image)
            
            # 구글 서버 호출 (구글 검색 + 코드 실행 엔진 동시에 탑재!)
            response = st.session_state.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents_payload,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    # 🔥 [치트키 2종 세트] 실시간 검색과 자체 코드 실행기를 모두 활성화!
                    tools=[
                        {"google_search": {}},     # 1. 실시간 구글 웹 검색
                        {"code_execution": {}}     # 2. 고급 수학/데이터 분석용 파이썬 코드 실행기
                    ]
                )
            )
            ai_response = response.text
            
            # AI의 답변 표시 및 저장
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # 7. 🔊 음성 읽어주기 기능이 켜져 있다면 목소리 생성
            if speak_out:
                try:
                    tts = gTTS(text=ai_response[:300], lang='ko') # 너무 길면 중간에 끊김 방지용 300자 제한
                    sound_file = io.BytesIO()
                    tts.write_to_fp(sound_file)
                    st.audio(sound_file, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error("음성 생성 중 오류가 발생했습니다.")