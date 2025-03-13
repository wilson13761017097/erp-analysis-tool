import streamlit as st
from utils.data_loader import ERPDataLoader
from utils.plot_utils import (
    create_time_series_plot,
    create_market_erp_comparison,
    create_correlation_heatmap,
    create_distribution_plot,
    create_rolling_stats_plot
)

# 设置页面标题
st.set_page_config(page_title="ERP分析工具", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    loader = ERPDataLoader()
    return loader.load_latest_data()

data = load_data()

# 创建侧边栏
st.sidebar.title("ERP分析工具")

# 市场选择
st.sidebar.header("市场选择")
selected_markets = st.sidebar.multiselect(
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

# 显示时间序列对比图
st.header("各市场ERP走势对比")
if selected_markets:
    fig = create_time_series_plot(data, selected_markets)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("请在侧边栏选择至少一个市场")

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

# 显示相关性热力图
st.header("市场间ERP相关性分析")
fig = create_correlation_heatmap(data)
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