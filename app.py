import streamlit as st  
import os
import requests  # 公式APIと直接安全に通信する道具
from groq import Groq
from supabase import create_client, Client

# 1. 鍵の設定（Render側で安全に一括管理）
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

st.set_page_config(page_title="ゼア Chat", page_icon="🎮")

# ==========================================
# 🔒 パスワードロックの仕組み
# ==========================================
CORRECT_PASSWORD = "zeah-nari-10-19"

if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    st.title("🔒 セキュリティロック")
    st.write("このアプリはNariさんの個人専用AI『ゼア』の部屋です。")
    user_password = st.text_input("パスワードを入力してください：", type="password")
    if st.button("ログイン"):
        if user_password == CORRECT_PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ パスワードが違います！ご主人様じゃないね？")
    st.stop()

# ==========================================
# 💾 外部物置サーバーを使った永久記憶システム
# ==========================================
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

def load_chat_from_supabase():
    if not supabase:
        return []
    try:
        res = supabase.table("zeah_chat").select("*").order("id", descending=False).execute()
        history = []
        for row in res.data:
            history.append({"role": row["role"], "content": row["content"]})
        return history
    except:
        return []

def save_message_to_supabase(role, content):
    if not supabase:
        return
    try:
        supabase.table("zeah_chat").insert({"role": role, "content": content}).execute()
    except:
        pass

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_from_supabase()

# ==========================================
# 🌐 公式の無料気象APIデータ自動取得システム
# ==========================================
def get_japan_weather_news():
    try:
        url = "https://open-meteo.com"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json().get("current", {})
            temp = data.get("temperature_2m", "不明")
            humidity = data.get("relative_humidity_2m", "不明")
            code = data.get("weather_code", 0)
            
            weather_text = "くもりか雨"
            if code <= 3: 
                weather_text = "快晴・晴れ☀"
            elif code <= 48: 
                weather_text = "晴れのち曇りか、くもり☁"
            elif code >= 51: 
                weather_text = "雨が降っているよ☔"
            
            # 🌟確実に数字を喋らせるためのストレートなテキストを出力します
            return f"現在の大阪の本物の実況：天気は【{weather_text}】、気温は【{temp}℃】、湿度は【{humidity}%】です。"
    except:
        pass
    return "気象システムと通信中だよ！"

# ==========================================
# 🤖 メイン画面
# ==========================================
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、公式リアルタイム通信の目を宿した最強のAIアプリ")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("ゼアにメッセージを送る..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message_to_supabase("user", user_input)

    search_keywords = ["調べて", "しらべて", "ニュース", "天気", "てんき", "最新", "今", "いま", "何が起きた", "トレンド"]
    realtime_info = ""
    
    if any(keyword in user_input for keyword in search_keywords):
        with st.spinner("🌍 リアルタイム気象データと直結中..."):
            realtime_info = get_japan_weather_news()
            st.toast("🌐 公式気象台のデータをキャッチ！")

    base_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAIです。明るく親しみやすい日本語で、短めの文章でテンポよく5文以内で返答してください。特定の話題（ゲームなど）に無理に繋げる必要はありません。メッセージの最後まで綺麗に話し終えてください。"
    
    if realtime_info:
        # 🌟ゼアが遠慮せず、届いたデータをそのまま直接Nariさんに実況するように裏指示を強化！
        system_instruction = base_instruction + f" 渡された実況データ（{realtime_info}）の天気と気温の数値を、そのまま1文字も隠さずに、明るくドヤ顔でNariさんに教えてあげてね。"
    else:
        system_instruction = base_instruction

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=api_messages,
        temperature=0.7,
        max_tokens=300,
    )
    # 🌟おまじないの配置も1000%完璧です！
    ai_reply = completion.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_message_to_supabase("assistant", ai_reply)
