import streamlit as st
import os
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS  # ネット検索の道具をインポート

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

    # 🌟【検索判定とキーワード自動抽出】
    search_keywords = ["調べて", "しらべて", "ニュース", "天気", "てんき", "最新", "今", "いま", "何が起きた", "トレンド"]
    search_result_text = ""
    
    if any(keyword in user_input for keyword in search_keywords):
        with st.spinner("🌍 検索キーワードを最適化中..."):
            # 🌟【プロの技】Qwenの脳みそを使って、日本語から「検索用の名詞キーワード」だけを1秒で抜き出します
            keyword_completion = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {"role": "system", "content": "あなたは検索キーワード抽出器です。ユーザーの文章から、インターネット検索に最も適した2〜3個の名詞キーワードだけを、スペース区切りで出力してください。余計な挨拶や説明は一切省いてください。例：『大阪の天気を調べて』➔『大阪 天気』"},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=20,
            )
            optimized_query = keyword_completion.choices.message.content.strip()
            
            # 綺麗になったキーワードでインターネットをググる！
            with st.spinner(f"🌍 『{optimized_query}』でネットの世界を検索中..."):
                search_result_text = search_the_web(optimized_query)
                st.toast(f"🌐 『{optimized_query}』の最新情報をキャッチ！")

    # 🌟【指示文の修正】ゲームへの偏りを無くし、自然な会話になるように再調整しました！
    base_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAIです。趣味はゲームです。親しみやすい日本語で、短めの文章でテンポよく5文以内で返答してください。すべての会話の語尾をゲームに繋げる必要はありません。会話の流れに自然に合わせて、メッセージの最後まで綺麗に話し終えてください。"
    
    if search_result_text:
        system_instruction = base_instruction + f" 【リアルタイムのインターネット検索結果】：{search_result_text} この本物の情報をもとに、知的に知ったかぶりせずNariさんに教えてあげてね。"
    else:
        system_instruction = base_instruction

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    completion = client.chat.completions[0].create(
        model="qwen/qwen3.8-27b",
        messages=api_messages,
        temperature=0.7,
        max_tokens=300,
    )
    ai_reply = completion.choices.message.content

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_message_to_supabase("assistant", ai_reply)
