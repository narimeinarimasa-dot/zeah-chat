import streamlit as st
import os
from groq import Groq

# 1. 鍵の設定（クラウド側で安全に管理）
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

st.set_page_config(page_title="ゼア Chat", page_icon="🎮")

# ==========================================
# 🌟 【新機能】パスワードロックの仕組み
# ==========================================
# Nariさんが決めたい「秘密のパスワード」をここに英数字で書きます
# （例：'nari2026' や 'zeah123' など好きな文字に変えてね！）
CORRECT_PASSWORD = "zeah-nari-10-19"

# アプリの初期状態（最初はロックがかかっている状態にする）
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

# パスワードがまだ間違っている（または未入力）なら、入力画面を出す
if not st.session_state.password_correct:
    st.title("🔒 セキュリティロック")
    st.write("このアプリはNariさんの個人専用AI『ゼア』の部屋です。")
    
    # 画面にパスワード入力欄を表示
    user_password = st.text_input("パスワードを入力してください：", type="password")
    
    # 入力された文字が合っているかチェックするボタン
    if st.button("ログイン"):
        if user_password == CORRECT_PASSWORD:
            st.session_state.password_correct = True
            st.rerun() # 画面をリフレッシュしてゼアの部屋を開く
        else:
            st.error("❌ パスワードが違います！ご主人様じゃないね？")
            
    st.stop() # パスワードが合うまでは、これより下のゼアのプログラムを絶対に動かさない！

# ==========================================
# 🤖 パスワードが合っていたら、ここから下が初めて起動します！
# ==========================================
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、スマホでも話せる世界に1つだけのAI")

# 会話の記憶システム
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話を綺麗に表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Nariさんが文字を入力した時の処理
if user_input := st.chat_input("ゼアにメッセージを送る..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # ゼアへの裏指示
    system_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAI。趣味はゲームです。親しみやすい日本語でテンポよく4文以内で返答してください。"

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
    ai_reply = completion.choices[0].message.content # 🌟バグ修正済みの完璧な形です！

    # 画面にゼアの返事を表示
    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
