import streamlit as st
from ..utils.data_loader import ERPDataLoader
from ..utils.plot_utils import create_time_series_plot, create_market_erp_comparison

def show():
    """显示时间序列分析页面"""
    st.title("市场ERP时间序列分析")
    
    # 加载数据
    if "data" not in st.session_state:
        data_loader = ERPDataLoader()
        st.session_state.data = data_loader.load_latest_data()
    
    data = st.session_state.data
    if data is None:
        st.error("数据加载失败")
        return
    
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
    
    # 1. 显示各市场ERP走势对比
    st.header("1. 各市场ERP走势对比")
    if selected_markets:
        fig1 = create_time_series_plot(data, selected_markets)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("请在侧边栏选择至少一个市场")
    
    # 2. 显示各市场指数与ERP对比
    st.header("2. 市场指数与ERP走势对比")
    
    # 市场选择
    market = st.selectbox(
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
    
    if market:
        fig2 = create_market_erp_comparison(data, market)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 添加说明
    st.markdown("""
    ### 说明
    
    1. 各市场ERP走势对比：
       - 展示不同市场ERP的相对水平
       - 反映风险溢价的跨市场比较
       
    2. 市场指数与ERP对比：
       - 展示指数与风险溢价的关系
       - 帮助理解市场估值与风险定价
    """) 