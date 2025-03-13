import streamlit as st
from apps.erp_index.utils.data_loader import ERPDataLoader
from apps.erp_index.utils.plot_utils import (
    create_time_series_plot,
    create_market_erp_comparison,
    create_distribution_plot,
    create_rolling_stats_plot
)

# 设置页面标题
st.set_page_config(page_title="ERP分析工具", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    try:
        loader = ERPDataLoader()
        return loader.load_latest_data()
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

# 确保数据被加载并存储到session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

if data is None:
    st.error("数据加载失败")
    st.stop()

# 创建标题
st.title("ERP分析工具")

# 显示最后更新时间
try:
    # 从time_series数据中获取最新日期
    latest_date = max(data["time_series"][market]["trade_date"].max() for market in ["CSI300", "HSI_mixed", "SPX"])
    st.caption(f"数据最后更新时间：{latest_date.strftime('%Y-%m-%d')}")
except Exception as e:
    st.caption("无法获取最后更新时间")

# 显示时间序列对比图
st.header("各市场ERP走势对比")

# 市场选择（移到图表上方）
selected_markets = st.multiselect(
    "选择要显示的市场",
    ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"],
    default=["CSI300", "HSI_mixed", "SPX"],
    format_func=lambda x: {
        "CSI300": "沪深300",
        "HSI_mixed": "恒生指数(混合)",
        "HSI_cn": "恒生指数(中债)",
        "HSI_us": "恒生指数(美债)",
        "SPX": "标普500"
    }[x]
)

if selected_markets:
    fig = create_time_series_plot(data, selected_markets)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("请选择至少一个市场")

# 显示单个市场的ERP和指数对比
st.header("单个市场ERP与指数对比")
selected_market = st.selectbox(
    "选择市场",
    ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"],
    format_func=lambda x: {
        "CSI300": "沪深300",
        "HSI_mixed": "恒生指数(混合)",
        "HSI_cn": "恒生指数(中债)",
        "HSI_us": "恒生指数(美债)",
        "SPX": "标普500"
    }[x]
)

if selected_market:
    fig = create_market_erp_comparison(data, selected_market)
    st.plotly_chart(fig, use_container_width=True)

# 显示分布特征
st.header("ERP分布特征分析")
fig = create_distribution_plot(data, selected_markets)
st.plotly_chart(fig, use_container_width=True)

# 显示滚动统计
st.header("ERP滚动统计分析")
window = st.slider("选择滚动窗口大小（交易日）", min_value=21, max_value=504, value=252, step=21)
fig = create_rolling_stats_plot(data, window)
st.plotly_chart(fig, use_container_width=True)

# 添加制作人信息
st.markdown("---")
st.markdown("<div style='text-align: right'>By wilson x</div>", unsafe_allow_html=True) 