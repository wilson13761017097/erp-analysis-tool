import streamlit as st
import pandas as pd
from ..utils.data_loader import ERPDataLoader

def show():
    """显示ERP分析概览页面"""
    st.title("ERP指数分析概览")
    
    # 加载数据
    data_loader = ERPDataLoader()
    data = data_loader.load_latest_data()
    
    if data is None:
        st.error("无法加载数据")
        return
    
    # 显示基础统计信息
    st.header("基础统计指标")
    st.dataframe(
        data["stats"].style.format({
            col: "{:.2f}" for col in data["stats"].columns 
            if col != "市场"
        })
    )
    
    # 显示最新ERP值
    st.header("最新ERP值")
    latest_erp = pd.DataFrame([
        {
            "市场": data_loader.get_market_name(market),
            "ERP (%)": df["erp"].iloc[-1] * 100,
            "更新日期": df["trade_date"].iloc[-1].strftime("%Y-%m-%d")
        }
        for market, df in data["time_series"].items()
    ])
    
    st.dataframe(
        latest_erp.style.format({
            "ERP (%)": "{:.2f}"
        })
    )
    
    # 添加说明
    st.markdown("""
    ### 说明
    
    1. ERP（股权风险溢价）计算方法：
       - 使用PE的倒数减去无风险利率
       - 沪深300使用中国10年期国债收益率
       - 恒生指数使用混合国债收益率（中美各50%）
       - 标普500使用美国10年期国债收益率
       
    2. 数据更新频率：
       - 每个交易日收盘后更新
       - PE数据来源：Wind数据库
       - 国债收益率来源：akshare接口
    """) 