import streamlit as st
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import requests
import json
import torch

def chatbot_page():
    st.title("🤖 ỨNG DỤNG CHAT BOT")
    st.markdown("💬 Hỏi đáp các thông tin về công ty/cổ phiếu của CMG và FPT.")

    # Sử dụng GPU nếu có, nếu không thì sử dụng CPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

    # Đọc FAISS index và các dữ liệu đã lưu trữ
    index = faiss.read_index("vector.index")

    with open("chunks.pkl", "rb") as f:
        chunk_texts = pickle.load(f)

    # Lưu trữ lịch sử các cuộc hội thoại trong session
    if "history" not in st.session_state:
        st.session_state.history = []

    # Nhận câu hỏi của người dùng
    query = st.chat_input("💬 Nhập câu hỏi của bạn:")

    if query:
        st.session_state.history.append({"question": query, "answer": "Đang xử lý..."})

        # Mã hóa câu hỏi của người dùng để tìm kiếm trong FAISS index
        query_embedding = embed_model.encode([query], convert_to_numpy=True)
        D, I = index.search(query_embedding, 3)

        # Nối các văn bản tìm được từ FAISS index thành một ngữ cảnh
        # Kiểm tra nếu chunk_texts[i] là chuỗi, nếu không thì xử lý như Document
        try:
            context = "\n".join([chunk_texts[i] if isinstance(chunk_texts[i], str) else chunk_texts[i].page_content for i in I[0]])
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi xử lý dữ liệu: {e}")
            return

        # Gửi dữ liệu tới API để lấy câu trả lời từ AI
        url = 'http://localhost:1234/v1/chat/completions'
        data = {
            'temperature': 0.3,
            'max_tokens': 1024,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        "Bạn là một trợ lý AI có nhiệm vụ phân tích nội dung tài liệu và đưa ra câu trả lời rõ ràng, chi tiết"
                        "Chỉ trả lời dựa trên nội dung tài liệu được cung cấp. "
                        "Nêu lên điểm chính trong văn bản."
                        "Không bỏ sót thông tin quan trọng."
                    )
                },
                {
                    'role': 'user',
                    'content': f"Đây là nội dung tài liệu tham khảo:\n\n{context}"
                },
                {
                    'role': 'user',
                    'content': (
                        f"Câu hỏi: {query}\n\n"
                        "Yêu cầu: Hãy trình bày rõ ràng tình hình tài chính, hoạt động đầu tư và cấu trúc vốn, cổ tức của công ty nếu có. "
                        "Gồm cả các số liệu về doanh thu, lợi nhuận, đầu tư, cổ tức nếu văn bản cung cấp. "
                        "Tránh trả lời chung chung hoặc bỏ sót thông tin."
                    )
                }
            ]
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.history[-1]["answer"] = answer
        else:
            st.session_state.history[-1]["answer"] = f"Lỗi từ API: {response.text}"

    # Hiển thị lịch sử hội thoại
    for item in reversed(st.session_state.history):
        st.markdown(f"**🧑 Bạn:** {item['question']}")
        st.markdown(f"**🤖 Trả lời:** {item['answer']}")
        st.markdown("---")