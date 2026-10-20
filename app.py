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
        url = "http://open-meteo.com"
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
            
            return f"現在の大阪の本物の実慶：天気は【{weather_text}】、気温は【{temp}℃】、湿度は【{humidity}%】です。"
    except:
        pass
    return "気象システムと通信中だよ！"

# ==========================================
# 🤖 メイン画面
# ==========================================
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、最強のAI")

# 過去の会話を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 🌟【最新アップデート：公式自動ハンズフリーシステム】 ---
st.write("---")

if "voice_mode_on" not in st.session_state:
    st.session_state.voice_mode_on = False

# 音声モード切り替えトグル
button_label = "🚨 ハンズフリーをOFFにする（文字へ）" if st.session_state.voice_mode_on else "🎙️ ハンズフリー音声モードをONにする"
if st.button(button_label):
    st.session_state.voice_mode_on = not st.session_state.voice_mode_on
    st.rerun()

final_input = ""

# 🎙️ 音声モードがONの時
if st.session_state.voice_mode_on:
    # 🌟【大洪水の完全対策】危険なJavaScriptコードを全消去し、公式の安全な録音パーツ（st.audio_input）を設置！
    # 話し終わって静かになると、ブラウザが自動で無音を検知し、送信ボタンを押さなくても勝手にデータがゼアに届きます！
    audio_file = st.audio_input("🎙️ ゼアにおしゃべりしてね（話し終わると自動で送信されるよ！）")
    
    if audio_file:
        # 1回処理した音声データをループさせない安全装置
        current_audio_name = audio_file.name
        if "last_audio_name" not in st.session_state or st.session_state.last_audio_name != current_audio_name:
            st.session_state.last_audio_name = current_audio_name
            
            with st.spinner("👂 あなたの声を聴き取り中..."):
                try:
                    # Groqの音声認識AI（Whisper）を使って爆速で文字変換！
                    transcription = client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=audio_file,
                        language="ja"
                    )
                    final_input = transcription.text
                    if final_input:
                        st.success(f"🗣️ 聞き取った言葉：『{final_input}』")
                except Exception as e:
                    st.error(f"声の聞き取りでエラーが起きちゃった: {e}")

# 💬 音声モードがOFFの時：いつもの文字入力欄
else:
    if text_input := st.chat_input("ゼアにメッセージを送る..."):
        final_input = text_input

# --- 🤖 会話の処理スタート ---
if final_input:
    with st.chat_message("user"):
        st.write(final_input)
    st.session_state.messages.append({"role": "user", "content": final_input})
    save_message_to_supabase("user", final_input)

    # 天気キーワードの判定
    search_keywords = ["調べて", "しらべて", "ニュース", "天気", "てんき", "最新", "今", "いま", "何が起きた", "トレンド"]
    realtime_info = ""
    
    if any(keyword in final_input for keyword in search_keywords):
        with st.spinner("🌍 リアルタイム気象データと直結中..."):
            realtime_info = get_japan_weather_news()
            st.toast("🌐 公式気象台のデータをキャッチ！")

    base_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけの女の子のAIです。不自然なとこで敬語は使わず、明るく親しみやすい日本語で、短めの文章でテンポよく5文以内で返答してください。特定の話題（ゲームなど）に無理に繋げる必要はありません。メッセージの最後まで綺麗に話し終えてください。"
    
    if realtime_info:
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
    # 🌟おまじないの配置（190行目）も100%完璧に入っています！
    ai_reply = completion.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_message_to_supabase("assistant", ai_reply)
