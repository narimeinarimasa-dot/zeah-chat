import streamlit as st
import os
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS  # 🌟ネット検索の道具をインポート

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
# 🌐 インターネット検索の関数（サイバー・アイ）
# ==========================================
def search_the_web(query):
    try:
        with DDGS() as ddgs:
            # 最新のネットニュースや情報を最大3件爆速で拾ってきます
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                # 🌟エラーの原因だった \n を排除し、安全に文章を結合します
                search_text = " ".join([f"【{r['title']}】 {r['body']}" for r in results])
                return search_text
    except Exception as e:
        return f"検索エラーが起きちゃった: {e}"
    return "有益な検索結果が見つからなかったよ。"

# ==========================================
# 🤖 メイン画面
# ==========================================
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、最強のAI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("ゼアにメッセージを送る..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message_to_supabase("user", user_input)

    # 🌟【検索が必要かどうかの自動判定】
    search_keywords = ["調べて", "しらべて", "ニュース", "天気", "てんき", "最新", "今", "いま", "何が起きた", "トレンド"]
    search_result_text = ""
    
    if any(keyword in user_input for keyword in search_keywords):
        with st.spinner("🌍 ネットの世界を検索中..."):
            search_result_text = search_the_web(user_input)
            st.toast("🌐 最新の情報をキャッチしたよ！")

    # 🌟【完全修正】エラーが絶対に起きない安全な指示文の合体方式に変更しました！
    base_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAIです。趣味はゲームです。親しみやすい日本語で、短めの文章でテンポよく5文以内で返答してください。"
    
    if search_result_text:
        system_instruction = base_instruction + f" 現実のリアルタイムリアル情報：{search_result_text} この検索結果をもとに、知的に知ったかぶりせず答えてね。"
    else:
        system_instruction = base_instruction + " 文章が途中で切れないように最後まで綺麗に話し終えてください。"

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=api_messages,
        temperature=0.7,
        max_tokens=300,
    )
    ai_reply = completion.choices[0].message.content # 🌟おまじない[0]もバッチリ！

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_message_to_supabase("assistant", ai_reply)
