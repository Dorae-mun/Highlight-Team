import streamlit as st
import pandas as pd
import plotly.graph_objs as go

def sales_dashboard_page():

    st.markdown(
        """
        <h1 style='text-align: center;'>📈 Dashboard Giá Cổ Phiếu</h1>
        """,
        unsafe_allow_html=True
    )

    @st.cache_data
    def load_and_prepare_data():
        cmg_df = pd.read_csv(
            "Xây dựng mô hình dự báo giá cổ phiếu/4.2.3 (TARGET) (live & his) CMG_detail_transactions_processed.csv",
            parse_dates=['Date']
        )
        fpt_df = pd.read_csv(
            "Xây dựng mô hình dự báo giá cổ phiếu/4.2.3 (TARGET) (live & his) FPT_detail_transactions_processed.csv",
            parse_dates=['Date']
        )
        full_df = pd.concat([cmg_df, fpt_df], ignore_index=True)

        cols_to_convert = ['Total Volume', 'Total Value', 'Market Cap',
                           'Closing Price', 'Price Change', 'Matched Volume', 'Matched Value']
        for col in cols_to_convert:
            full_df[col] = (full_df[col].astype(str)
                            .str.replace(',', '')
                            .astype(float)
                            .round()
                            .astype(int))
        return full_df

    full_df = load_and_prepare_data()

    # Đảm bảo cột 'Date' là kiểu datetime
    full_df['Date'] = pd.to_datetime(full_df['Date'], format='%d/%m/%Y')

    # Sidebar
    st.sidebar.title("📊 Bộ lọc")
    stock_options = full_df['StockID'].unique()
    selected_stock = st.sidebar.selectbox("Chọn mã cổ phiếu", stock_options)

    df = full_df[full_df['StockID'] == selected_stock].sort_values(by='Date', ascending=False)

    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Chọn khoảng thời gian", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    latest_row = full_df.sort_values('Date').iloc[-1]
    prev_row = full_df.sort_values('Date').iloc[-2]
        
    # Tạo 4 cột cho 4 card
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Mỗi cột chiếm 25% không gian

    # Card cho "Giá đóng cửa"
    with col1:
        st.markdown(f"""
            <div style="border: 1px solid black; border-left: 10px solid gray; 
                        border-radius: 10px; padding: 1rem; background-color: white; 
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                <h4 style="font-size: 23px">💰 Giá đóng cửa</h4>
                <p>{latest_row['Closing Price']:,} VND</p>
            </div>
        """, unsafe_allow_html=True)

    # Card cho "Khối lượng khớp lệnh"
    with col2:
        st.markdown(f"""
            <div style="border: 1px solid black; border-left: 10px solid gray; 
                        border-radius: 10px; padding: 1rem; background-color: white; 
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                <h4 style="font-size: 23px">📦 KL khớp lệnh</h4>
                <p>{latest_row['Matched Volume']:,} CP</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Mở rộng để xem bảng dữ liệu
    with st.expander("📄 Xem bảng dữ liệu chi tiết"):
        st.markdown("""
            <style>
            .stDataFrame div[data-testid="stDataFrame"] div[role="table"] {
                font-weight: bold !important;
                font-size: 16px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)


    # Card cho "Vốn hóa"
    with col3:
        st.markdown(f"""
            <div style="border: 1px solid black; border-left: 10px solid gray; 
                        border-radius: 10px; padding: 1rem; background-color: white; 
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                <h4 style="font-size: 23px">🏦 Vốn hóa</h4>
                <p>{latest_row['Market Cap'] / 1e6:.2f} Tỷ VND</p>
            </div>
        """, unsafe_allow_html=True)

    # Card cho "Giá thay đổi"
    with col4:
        # Kiểm tra nếu giá thay đổi âm thì màu đỏ, nếu dương thì màu xanh
        price_change_color = "red" if latest_row['Price Change'] < 0 else "green"
        
        st.markdown(f"""
            <div style="border: 1px solid black; border-left: 10px solid gray; 
                        border-radius: 10px; padding: 1rem; background-color: white; 
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                <h4 style="font-size: 20px">🔺 Giá Thay Đổi</h4>
                <p style="color: {price_change_color}; font-size: 18px;">
                    {latest_row['Price Change']:+,} VND
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Main dashboard: Tạo các cột với tỉ lệ chia không gian cho các biểu đồ
    col1, col2 = st.columns([4, 4])  # Mỗi cột chiếm 50% không gian

    with col1:
        # Biểu đồ giá thay đổi %
        fig_price_change = go.Figure()
        fig_price_change.add_trace(go.Bar(
            x=df['Date'],
            y=df['Price Change %'],
            marker_color=['green' if val > 0 else 'red' for val in df['Price Change %']],
            name='Giá thay đổi (%)'
        ))
        fig_price_change.update_layout(
            title="📉 Biểu đồ Giá Thay Đổi (%)",
            xaxis_title="Ngày",
            yaxis_title="Tỷ lệ thay đổi (%)",
            hovermode="x unified",
            width=800,
            height=400,
            plot_bgcolor="#e5edf4",
            paper_bgcolor="#c9d7e5",
        )
        st.plotly_chart(fig_price_change, use_container_width=True)

    with col2:
        # Biểu đồ khối lượng khớp lệnh
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(
            x=df['Date'],
            y=df['Matched Volume'],
            name='Khối lượng khớp lệnh',
            marker=dict(color='orange')
        ))
        fig_volume.update_layout(
            title="🔁 Khối Lượng Khớp Lệnh",
            xaxis_title="Ngày",
            yaxis_title="Khối lượng",
            hovermode="x",
            width=800,
            height=400,
            plot_bgcolor="#e5edf4",
            paper_bgcolor="#c9d7e5",
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    @st.cache_data
    def load_forecast_data():
        forecast_fpt = pd.read_csv('Xây dựng mô hình dự báo giá cổ phiếu/Du_bao_FPT.csv',
                                   names=['Date', 'Closing Price', 'Predicted Closing Price'],
                                   header=0)
        forecast_cmg = pd.read_csv('Xây dựng mô hình dự báo giá cổ phiếu/Du_bao_CMG.csv',
                                   names=['Date', 'Closing Price', 'Predicted Closing Price'],
                                   header=0)
        forecast_fpt['StockID'] = 'FPT'
        forecast_cmg['StockID'] = 'CMG'
        return pd.concat([forecast_fpt, forecast_cmg], ignore_index=True)
    
    forecast_df = load_forecast_data()

    #Lọc theo cổ phiếu
    forecast_filtered = forecast_df[forecast_df['StockID'] == selected_stock]

    # Vẽ biểu đồ
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=forecast_filtered['Date'],
        y=forecast_filtered['Closing Price'],
        mode='lines+markers',
        name='Giá thực tế',
        line=dict(color='blue')
    ))
    fig_forecast.add_trace(go.Scatter(
        x=forecast_filtered['Date'],
        y=forecast_filtered['Predicted Closing Price'],
        mode='lines+markers',
        name='Giá dự báo',
        line=dict(color='red'),
        connectgaps=True
    ))
    fig_forecast.update_layout(
        title=f"🔮 Dự Báo Giá Đóng Cửa - {selected_stock}",
        xaxis_title="Ngày",
        yaxis_title="Giá",
        hovermode="x unified",
        height=400,
        plot_bgcolor="#e5edf4",
        paper_bgcolor="#c9d7e5",
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

# Gọi hàm trang dashboard của bạn
sales_dashboard_page()