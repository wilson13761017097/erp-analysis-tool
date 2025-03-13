import streamlit as st
from ..utils.data_loader import ERPDataLoader
from ..utils.plot_utils import create_rolling_stats_plot

def show():
    """显示滚动统计分析页面"""
    st.title("ERP滚动统计分析")
    
    # 加载数据
    data_loader = ERPDataLoader()
    data = data_loader.load_latest_data()
    
    if data is None:
        st.error("无法加载数据")
        return
    
    # 选择滚动窗口期
    window = st.selectbox(
        "选择滚动窗口期",
        [252, 126, 63],
        format_func=lambda x: f"{x}天 ({x//21}个月)" if x != 252 else "252天 (1年)",
        index=0
    )
    
    # 创建滚动统计图
    fig = create_rolling_stats_plot(data, window)
    st.plotly_chart(fig, use_container_width=True)
    
    # 添加说明
    st.markdown("""
    ### 说明
    
    1. 滚动平均ERP：
       - 反映各市场ERP的中期趋势
       - 帮助识别风险溢价的结构性变化
       
    2. ERP波动率：
       - 衡量风险溢价的波动程度
       - 反映市场风险定价的稳定性
       
    3. 滚动窗口：
       - 252天：对应一个交易年度
       - 126天：对应半年度
       - 63天：对应一个季度
    """) 