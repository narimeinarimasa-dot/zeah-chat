import streamlit as st
import os
import json
from groq import Groq

# 1. 鍵の設定（クラウド側で安全に管理）
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

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
# 💾 🌟【新機能】永久記憶システム（日記帳の読み書き）
# ==========================================
MEMORY_FILE = "zeah_memory.json"

# クラウドのお家に日記帳ファイルがあるかチェックして、あれば読み込む
def load_chat_history():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 会話が終わるたびに、日記帳ファイルに上書き保存する
def save_chat_history(messages_list):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages_list, f, ensure_ascii=False, indent=4)

# アプリ起動時に、過去の日記帳（永久記憶）を読み込んでセットする
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# ==========================================
# 🤖 パスワードクリア後のメイン画面
# ==========================================
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、スマホでも話せる世界に1つだけのAI")

# 過去のすべての会話履歴を画面に綺麗に再現して表示（リロードしても消えません！）
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("ゼアにメッセージを送る..."):
    # 画面に入力文字を表示
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 裏指示（途切れ対策もバッチリ！）
    system_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAIです。趣味はゲームです。親しみやすい日本語で、短めの文章でテンポよく5文以内で返答してください。文章が途中で切れないように最後まで綺麗に話し終えてください。"

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # 最強の脳（Qwen）でおしゃべり生成
    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=api_messages,
        temperature=0.7,
        max_tokens=300,
    )
    ai_reply = completion.choices[0].message.content

    # 画面にゼアの返事を表示
    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # 🌟【最重要】会話が成立した瞬間に、日記帳（ファイル）へ永久保存する！
    save_chat_history(st.session_state.messages)
