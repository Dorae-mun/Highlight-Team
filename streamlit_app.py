import streamlit as st
from app import chatbot_page
from dashboard import sales_dashboard_page

# Cấu hình trang
st.set_page_config(page_title="Highlight Dashboard", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stApp"] {
        background: linear-gradient(to right, #c9d7e5, #b4c7d4);
    }
    .menu-container {
        margin-bottom: 10px;
    }
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        color: #37474F;
        cursor: pointer;
        transition: background-color 0.3s ease;
        text-decoration: none;
    }
    .menu-item:hover {
        background-color: #aebdc7;
    }
    .menu-item.selected {
        background-color: #607d8b;
        color: white;
    }
    .menu-icon {
        margin-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Khởi tạo trạng thái
if "menu_selection" not in st.session_state:
    st.session_state.menu_selection = "Chat Bot"

# Tạo nút sidebar với HTML click toàn vùng
def sidebar_html_button(name, icon):
    selected = st.session_state.menu_selection == name
    selected_class = "selected" if selected else ""
    button_html = f"""
        <div class="menu-container">
            <a href="?menu={name}" class="menu-item {selected_class}">
                <span class="menu-icon">{icon}</span> {name}
            </a>
        </div>
    """
    st.sidebar.markdown(button_html, unsafe_allow_html=True)

# Sidebar hiển thị
st.sidebar.markdown("### Projects")
sidebar_html_button("Chat Bot", "💬")
sidebar_html_button("Sales Dashboard", "📊")

# Lấy menu từ URL và cập nhật session_state
menu = st.query_params.get("menu", "Chat Bot")  # Default to "Chat Bot"
if menu != st.session_state.menu_selection:
    st.session_state.menu_selection = menu
    st.rerun()  # Làm mới lại trang để cập nhật

# Điều hướng nội dung
if st.session_state.menu_selection == "Chat Bot":
    from app import chatbot_page
    chatbot_page()
else:
    from dashboard import sales_dashboard_page
    sales_dashboard_page()

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Tạo bởi **HIGHLIGHT TEAM** 🚀")