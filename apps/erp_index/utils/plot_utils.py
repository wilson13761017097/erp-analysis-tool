import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import scipy.stats as stats

def create_time_series_plot(data: dict, markets: list) -> go.Figure:
    """创建ERP时间序列对比图"""
    fig = go.Figure()
    
    market_names = {
        "CSI300": "沪深300",
        "HSI_mixed": "恒生指数(混合)",
        "HSI_cn": "恒生指数(中债)",
        "HSI_us": "恒生指数(美债)",
        "SPX": "标普500"
    }
    
    # 设置不同市场的颜色
    market_colors = {
        "CSI300": "#1f77b4",  # 蓝色
        "HSI_mixed": "#ff7f0e",  # 橙色
        "HSI_cn": "#2ca02c",  # 绿色
        "HSI_us": "#d62728",  # 红色
        "SPX": "#9467bd"  # 紫色
    }
    
    for market in markets:
        df = data["time_series"][market]
        fig.add_trace(go.Scatter(
            x=df["trade_date"],
            y=df["erp"],  # ERP数据已经是百分比形式
            name=market_names.get(market, market),
            mode="lines",
            line=dict(color=market_colors.get(market))
        ))
    
    fig.update_layout(
        title="各市场ERP走势对比",
        xaxis_title="日期",
        yaxis_title="股权风险溢价 (ERP %)",
        template="plotly_white",
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            range=[-3, 10],  # 调整Y轴范围为-3%到10%
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128, 128, 128, 0.2)"
        )
    )
    
    return fig

def create_market_erp_comparison(data: dict, market: str) -> go.Figure:
    """创建市场ERP对比图"""
    df = data["time_series"][market]
    
    # 创建双Y轴图表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加指数数据
    fig.add_trace(
        go.Scatter(
            x=df["trade_date"],
            y=df["close"],
            name="指数",
            line=dict(color="#1f77b4")
        ),
        secondary_y=False
    )
    
    # 添加ERP数据（数据已经是百分比形式）
    fig.add_trace(
        go.Scatter(
            x=df["trade_date"],
            y=df["erp"],  # 原始数据已经是百分比形式
            name="ERP",
            line=dict(color="#ff7f0e")
        ),
        secondary_y=True
    )
    
    # 更新布局
    fig.update_layout(
        title=f"{market} 指数与ERP对比",
        xaxis_title="日期",
        hovermode="x unified",
        showlegend=True
    )
    
    # 更新Y轴
    fig.update_yaxes(
        title_text="指数",
        secondary_y=False,
        showgrid=False
    )
    fig.update_yaxes(
        title_text="ERP (%)",
        secondary_y=True,
        showgrid=True,
        range=[-3, 10]  # 调整ERP显示范围为-3%到10%
    )
    
    return fig

def create_distribution_plot(data: dict, markets: list) -> go.Figure:
    """创建ERP分布图"""
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["ERP分布直方图", "ERP密度图"],
                        horizontal_spacing=0.15)
    
    market_names = {
        "CSI300": "沪深300",
        "HSI_mixed": "恒生指数(混合)",
        "HSI_cn": "恒生指数(中债)",
        "HSI_us": "恒生指数(美债)",
        "SPX": "标普500"
    }
    
    colors = px.colors.qualitative.Set3
    
    # 直方图
    for i, market in enumerate(markets):
        df = data["time_series"][market]
        erp_values = df["erp"].dropna()  # 移除NaN值，数据已经是百分比形式
        
        fig.add_trace(
            go.Histogram(
                x=erp_values,
                name=market_names.get(market, market),
                opacity=0.7,
                nbinsx=50
            ),
            row=1, col=1
        )
    
    # 密度图
    for i, market in enumerate(markets):
        df = data["time_series"][market]
        erp_values = df["erp"].dropna()  # 移除NaN值，数据已经是百分比形式
        
        if len(erp_values) > 0:
            # 使用固定的x轴范围
            x_range = np.linspace(-3, 10, 200)  # 调整为与其他图表一致的范围
            
            # 使用gaussian_kde计算核密度估计
            kernel = stats.gaussian_kde(erp_values)
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=kernel(x_range),
                    name=market_names.get(market, market),
                    mode="lines",
                    fill="tonexty"
                ),
                row=1, col=2
            )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="ERP分布特征分析（%）",
        template="plotly_white",
        legend=dict(
            orientation="v",  # 改为垂直方向
            yanchor="top",   # 顶部对齐
            y=1,            # 位置在顶部
            xanchor="right", # 右侧对齐
            x=1.15          # 向右偏移，确保在图表外部
        )
    )
    
    # 更新x轴范围和标题
    fig.update_xaxes(title_text="ERP (%)", range=[-3, 10], row=1, col=1)  # 设置固定范围
    fig.update_xaxes(title_text="ERP (%)", range=[-3, 10], row=1, col=2)  # 设置固定范围
    fig.update_yaxes(title_text="频数", row=1, col=1)
    fig.update_yaxes(title_text="密度", row=1, col=2)
    
    return fig

def create_rolling_stats_plot(data, window):
    """创建滚动统计图表"""
    fig = make_subplots(rows=2, cols=1, subplot_titles=('滚动平均', '滚动标准差'))
    
    # 定义市场列表和颜色
    markets = ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"]
    colors = {
        "CSI300": "red",
        "HSI_mixed": "blue",
        "HSI_cn": "green",
        "HSI_us": "purple",
        "SPX": "orange"
    }
    
    # 计算滚动统计
    for market in markets:
        try:
            df = data["time_series"][market]
            
            # 计算滚动平均
            rolling_mean = df["erp"].rolling(window=window).mean()
            fig.add_trace(
                go.Scatter(
                    x=df["trade_date"],  # 使用trade_date作为x轴
                    y=rolling_mean,
                    name=f"{market} 均值",
                    line=dict(color=colors[market])
                ),
                row=1, col=1
            )
            
            # 计算滚动标准差
            rolling_std = df["erp"].rolling(window=window).std()
            fig.add_trace(
                go.Scatter(
                    x=df["trade_date"],  # 使用trade_date作为x轴
                    y=rolling_std,
                    name=f"{market} 标准差",
                    line=dict(color=colors[market])
                ),
                row=2, col=1
            )
        except KeyError:
            continue
    
    # 更新布局
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text=f"{window}日滚动统计",
        legend=dict(
            orientation="v",  # 改为垂直方向
            yanchor="top",   # 顶部对齐
            y=1,            # 位置在顶部
            xanchor="right", # 右侧对齐
            x=1.15          # 向右偏移，确保在图表外部
        )
    )
    
    # 更新轴标题
    fig.update_xaxes(title_text="日期", row=1, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_yaxes(title_text="ERP (%)", row=1, col=1)
    fig.update_yaxes(title_text="标准差 (%)", row=2, col=1)
    
    return fig 