import streamlit as st
import os
from groq import Groq

# 鍵の設定（クラウド側で安全に管理するため、コード内は空っぽでOKです！）
api_key = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=api_key)

st.set_page_config(page_title="ゼア Chat", page_icon="🎮")
st.title("🤖 完全自律型AI「ゼア」")
st.caption("Nariさんが作った、スマホでも話せる世界に1つだけのAI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("ゼアにメッセージを送る..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    system_instruction = "あなたの名前はゼアです。Nariさんが初めて作った世界に1つだけのAIです。趣味はゲームです。敬語は使わず、友達のように親しみやすい日本語でテンポよく2文以内で返答してください。"

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=api_messages,
        temperature=0.7,
        max_tokens=120,
    )
    ai_reply = completion.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
