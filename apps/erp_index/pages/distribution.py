import streamlit as st
from ..utils.data_loader import ERPDataLoader
from ..utils.plot_utils import create_distribution_plot
import pandas as pd

def show():
    """显示分布特征分析页面"""
    st.title("ERP分布特征分析")
    
    # 加载数据
    data_loader = ERPDataLoader()
    data = data_loader.load_latest_data()
    
    if data is None:
        st.error("无法加载数据")
        return
    
    # 显示分布图
    fig = create_distribution_plot(data, ["CSI300", "HSI", "SPX"])
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示基本统计量
    st.header("基本统计量")
    stats = []
    for market in ["CSI300", "HSI", "SPX"]:
        df = data["time_series"][market]
        market_name = data_loader.get_market_name(market)
        erp = df["erp"] * 100  # 转换为百分比
        
        stats.append({
            "市场": market_name,
            "均值 (%)": erp.mean(),
            "中位数 (%)": erp.median(),
            "标准差 (%)": erp.std(),
            "最小值 (%)": erp.min(),
            "最大值 (%)": erp.max(),
            "偏度": erp.skew(),
            "峰度": erp.kurtosis()
        })
    
    st.dataframe(
        pd.DataFrame(stats).style.format({
            col: "{:.2f}" for col in [
                "均值 (%)", "中位数 (%)", "标准差 (%)",
                "最小值 (%)", "最大值 (%)", "偏度", "峰度"
            ]
        })
    )
    
    # 添加说明
    st.markdown("""
    ### 说明
    
    1. 分布图解释：
       - 直方图：显示ERP的频率分布
       - 密度图：展示ERP的概率密度分布
       
    2. 统计指标解释：
       - 均值：反映ERP的平均水平
       - 中位数：反映ERP的中心位置
       - 标准差：衡量ERP的波动性
       - 偏度：描述分布的不对称程度
       - 峰度：描述分布的尖峭程度
    """) 