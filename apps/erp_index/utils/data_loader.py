import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ERPDataLoader:
    def __init__(self):
        self._market_names = {
            "CSI300": "沪深300",
            "HSI_mixed": "恒生指数(混合)",
            "HSI_cn": "恒生指数(中债)",
            "HSI_us": "恒生指数(美债)",
            "SPX": "标普500"
        }
    
    def _generate_sample_data(self):
        """生成示例数据用于展示"""
        # 生成日期序列
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*5)  # 5年数据
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        time_series = {}
        for market in ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"]:
            # 生成ERP数据
            np.random.seed(42)  # 确保可重复性
            n = len(dates)
            
            # 生成基础趋势
            trend = np.linspace(0, 2, n) + np.random.normal(0, 0.5, n)
            
            # 添加季节性
            seasonal = 0.5 * np.sin(np.linspace(0, 10*np.pi, n))
            
            # 生成ERP数据（确保在合理范围内）
            erp = trend + seasonal + np.random.normal(0, 0.3, n)
            erp = erp + 4  # 将均值调整到合理水平
            
            # 生成指数数据
            if market == "CSI300":
                base = 3000
            elif market.startswith("HSI"):
                base = 20000
            else:
                base = 4000
                
            close = base * (1 + np.cumsum(np.random.normal(0.0002, 0.01, n)))
            
            # 创建DataFrame
            df = pd.DataFrame({
                'trade_date': dates,
                'erp': erp,
                'close': close,
                'pe': 15 + np.random.normal(0, 2, n),
                'rf': 0.03 + np.random.normal(0, 0.005, n)
            })
            
            time_series[market] = df
        
        # 生成相关性矩阵
        correlation_data = pd.DataFrame()
        for market in ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"]:
            correlation_data[self._market_names[market]] = time_series[market]["erp"]
        correlation = correlation_data.corr()
        
        return {
            "time_series": time_series,
            "correlation": correlation
        }
    
    def load_latest_data(self):
        """加载最新的ERP分析数据"""
        return self._generate_sample_data()
    
    def get_market_name(self, market_code: str) -> str:
        """获取市场的中文名称"""
        return self._market_names.get(market_code, market_code) 