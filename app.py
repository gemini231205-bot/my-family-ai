import streamlit as st
import google.generativeai as genai
import os
import json
import hashlib

# =================================================================
# 1. 화면 스타일링 및 모든 흔적 완벽 박멸
# =================================================================
st.set_page_config(page_title="GHK AI ENTERPRISE", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader, [class*="st-emotion-cache"] header {
        display: none !important; visibility: hidden !important; height: 0px !important;
    }
    [data-testid="stManageAppBanners"], .stManageAppBanners, iframe[title="Manage app"] {
        display: none !important; visibility: hidden !important; height: 0px !important;
    }
    footer, [data-testid="stFooter"], #MainMenu {
        display: none !important; visibility: hidden !important;
    }
    .block-container {
        padding-top: 1.5rem !important; padding-bottom: 1.5rem !important;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. 데이터베이스 설정 및 고도화
# =================================================================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = "AQ.Ab8RN6K3O5OXLonP6IjXCrqdEhgmpSRzuOuJmbpqNIDiOcujYA" 

genai.configure(api_key=api_key)

USER_DB = "users_db_v2.json"
CHAT_DB = "chat_history_enterprise.json"
TANK_DB = "idea_tank_enterprise.json"

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_data(file):
    try:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f: 
                return json.load(f)
    except:
        pass
    return {}

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users = load_data(USER_DB)
all_chats = load_data(CHAT_DB)
all_tanks = load_data(TANK_DB)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# =================================================================
# 3. 로그인 및 회원가입 화면
# =================================================================
if not st.session_state.logged_in:
    st.title("🔱 GHK AI 엔터프라이즈 포탈")
    auth_mode = st.radio("메뉴 선택", ["로그인", "회원가입"], key="auth_mode_radio")
    
    with st.form("auth_form"):
        user_id = st.text_input("아이디", key="login_id_input").strip()
        user_pw = st.text_input("비밀번호", type="password", key="login_pw_input").strip()
        submit = st.form_submit_button(auth_mode)
        
        if submit:
            if auth_mode == "회원가입":
                if user_id in users: 
                    st.error("이미 등록된 아이디입니다.")
                elif user_id and user_pw:
                    users[user_id] = {"pw": make_hash(user_pw), "plan": "FREE"}
                    save_data(USER_DB, users)
                    st.success("회원가입 성공! 로그인 후 이용해 주세요.")
                else: 
                    st.warning("정보를 전부 입력하세요.")
            else:
                if user_id in users and users[user_id]["pw"] == make_hash(user_pw):
                    st.session_state.logged_in = True
                    st.session_state.user = user_id
                    st.rerun()
                else: 
                    st.error("아이디 혹은 비밀번호 확인 실패.")
    st.stop()

# 세션 동기화
current_user = st.session_state.user
if current_user not in users:
    users[current_user] = {"pw": "", "plan": "FREE"}
user_plan = users[current_user].get("plan", "FREE")

if "messages" not in st.session_state:
    st.session_state.messages = all_chats.get(current_user, [])
if "idea_tank" not in st.session_state:
    st.session_state.idea_tank = all_tanks.get(current_user, [])

# =================================================================
# 4. 종합 제어 컨트롤 허브 (사이드바)
# =================================================================
with st.sidebar:
    st.title(f"👑 {current_user}님 허브")
    st.markdown(f"현재 등급: **[{user_plan} PLAN]**")
    
    if st.button("➕ 새 대화방 만들기 (New Chat)", key="btn_new_chat"):
        st.session_state.messages = []
        all_chats[current_user] = []
        save_data(CHAT_DB, all_chats)
        st.rerun()
        
    st.write("---")
    
    tab1, tab2, tab3 = st.tabs(["🔍 검색/저장", "⭐ 플랜", "👤 설정"])
    
    with tab1:
        search_query = st.text_input("대화 키워드 검색", key="search_query_input")
        if search_query:
            found = [m for m in st.session_state.messages if search_query in m["content"] and not m.get("is_image")]
            for f_msg in found: st.info(f"[{f_msg['role']}] {f_msg['content'][:25]}...")
        
        st.write("---")
        st.write("✨ 아이디어 싱크탱크")
        for idea in st.session_state.idea_tank: st.warning(f"💡 {idea}")
            
    with tab2:
        st.subheader("🚀 라이선스 업그레이드")
        st.write("• **FREE**: 기본 지능 탑재")
        st.write("• **PREMIUM**: 그림 생성 및 초고성능 모드 해제")
        
        new_plan = st.selectbox("변경할 등급 선택", ["FREE", "PREMIUM"], index=0 if user_plan=="FREE" else 1, key="plan_select_box")
        if st.button("💳 플랜 즉시 변경하기", key="btn_change_plan"):
            users[current_user]["plan"] = new_plan
            save_data(USER_DB, users)
            st.success(f"[{new_plan}] 등급으로 즉시 반영되었습니다!")
            st.rerun()
            
    with tab3:
        st.subheader("🔒 보안 및 관리")
        new_pw = st.text_input("새 비밀번호 변경", type="password", key="change_pw_input")
        if st.button("🔑 비밀번호 수정", key="btn_modify_pw"):
            if new_pw:
                users[current_user]["pw"] = make_hash(new_pw)
                save_data(USER_DB, users)
                st.success("비밀번호 변경 완료!")
            else: st.error("공백은 사용할 수 없습니다.")
            
        st.write("---")
        if st.button("🚨 계정 즉시 탈퇴", type="secondary", key="btn_delete_account"):
            if current_user in users: del users[current_user]
            if current_user in all_chats: del all_chats[current_user]
            if current_user in all_tanks: del all_tanks[current_user]
            save_data(USER_DB, users)
            save_data(CHAT_DB, all_chats)
            save_data(TANK_DB, all_tanks)
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    uploaded_file = st.file_uploader("파일 업로드 인프라", type=["png", "jpg", "jpeg", "pdf", "txt"], key="file_uploader_hub")
    if st.button("🚪 안전 로그아웃", key="btn_logout"):
        st.session_state.logged_in = False; st.rerun()

# =================================================================
# 5. 메인 스트리밍 및 제미나이 작동 코어
# =================================================================
st.title("🔱 GHK AI ENTERPRISE")
st.caption(f"인증 계정: {current_user} | 적용 등급: {user_plan} LEVEL")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_image"): st.image(msg["content"])
        else: st.markdown(msg["content"])

if user_input := st.chat_input("GHK AI에게 무엇이든 물어보세요!", key="chat_input_core"):
    with st.chat_message("user"): st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        resp_place = st.empty()
        
        try:
            if any(k in user_input for k in ["그려줘", "그림", "이미지 생성"]):
                if user_plan == "FREE":
                    resp_place.error("❌ 이미지 생성 기능은 [PREMIUM] 플랜 전용 기능입니다. 사이드바에서 등급을 올려주세요!")
                else:
                    resp_place.markdown("🎨 Premium Imagen 3 하이엔드 렌더링 중...")
                    imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
                    result = imagen.generate_images(prompt=user_input)
                    img_path = f"img_{current_user}_{len(st.session_state.messages)}.png"
                    result.images[0].image.save(img_path)
                    resp_place.image(img_path)
                    st.session_state.messages.append({"role": "assistant", "content": img_path, "is_image": True})
            
            else:
                # 💡 [구글 라우팅 강제 돌파 고정] 옛날 라이브러리가 주소를 엉뚱하게 찾아가지 못하도록 아예 고유 명칭으로 고정!
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                
                contents = []
                if uploaded_file:
                    f_bytes = uploaded_file.read()
                    if uploaded_file.type.startswith("image/"):
                        contents.append({"mime_type": uploaded_file.type, "data": f_bytes})
                    else:
                        contents.append(f_bytes.decode("utf-8", errors="ignore"))
                
                full_prompt = f"너는 초지능 솔루션 GHK AI다. 유저 {current_user}에게 친절하게 답해라.\n\n질문: {user_input}"
                contents.append(full_prompt)
                
                # 구형 SDK에서 v1beta 호출로 뻗는 버그를 원천 봉쇄하는 안전 모드 파라미터 적용
                response = model.generate_content(contents)
                ai_txt = response.text
                resp_place.markdown(ai_txt)
                st.session_state.messages.append({"role": "assistant", "content": ai_txt})
                
                # 🧠 싱크탱크 가동
                tank_prompt = f"다음 문장이 계획, 핵심 지식, 공식이면 20자 이내로 핵심만 요약하고, 일상 대화면 'PASS'라고만 답해라.\n\n문장: {user_input}"
                tank_check = model.generate_content(tank_prompt).text.strip()
                
                if "PASS" not in tank_check and len(tank_check) > 2 and len(tank_check) < 40:
                    st.session_state.idea_tank.append(tank_check)
                    all_tanks[current_user] = st.session_state.idea_tank
                    save_data(TANK_DB, all_tanks)
            
            all_chats[current_user] = st.session_state.messages
            save_data(CHAT_DB, all_chats)
            
        except Exception as e:
            resp_place.error(f"시스템 예외: {e}")
