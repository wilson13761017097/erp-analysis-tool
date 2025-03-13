import pandas as pd
import os
import streamlit as st
import numpy as np
import shutil
from datetime import datetime

class ERPDataLoader:
    def __init__(self):
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)
        # 获取Streamlit_Projects目录路径
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        self.data_path = os.path.join(self.base_path, "data", "erp_index")
        self.erp_project_path = os.path.join(os.path.dirname(self.base_path), "ERP Index")
        
        self._market_names = {
            "CSI300": "沪深300",
            "HSI_mixed": "恒生指数(混合)",
            "HSI_cn": "恒生指数(中债)",
            "HSI_us": "恒生指数(美债)",
            "SPX": "标普500"
        }
        
        # 确保数据目录存在
        os.makedirs(self.data_path, exist_ok=True)
        
        # 检查ERP Index项目路径是否存在
        if not os.path.exists(self.erp_project_path):
            st.error(f"无法找到ERP Index项目路径: {self.erp_project_path}")
            return
        
        # 检查并同步数据
        self._sync_data_if_needed()
    
    def _check_source_paths(self):
        """检查源数据路径是否存在"""
        paths = {
            "ERP项目路径": self.erp_project_path,
            "数据输出目录": os.path.join(self.erp_project_path, "data", "output"),
            "处理数据目录": os.path.join(self.erp_project_path, "data", "processed"),
            "分析结果目录": os.path.join(self.erp_project_path, "analysis")
        }
        
        all_exist = True
        for name, path in paths.items():
            if not os.path.exists(path):
                all_exist = False
                break
        
        return all_exist
    
    def _sync_data_if_needed(self):
        """检查并同步数据（如果需要）"""
        try:
            # 检查源数据路径
            if not self._check_source_paths():
                return
            
            # 清理旧数据
            self._clean_old_data()
            
            # 强制更新数据
            self._sync_data()
            
            # 更新时间戳
            last_update_file = os.path.join(self.data_path, "last_update.txt")
            with open(last_update_file, "w") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        except Exception as e:
            pass
    
    def _clean_old_data(self):
        """清理旧的数据文件"""
        try:
            # 获取所有csv文件
            files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
            
            # 删除所有csv文件
            for file in files:
                file_path = os.path.join(self.data_path, file)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        
        except Exception:
            pass
    
    def _sync_data(self):
        """从ERP Index项目同步最新数据"""
        try:
            # 同步基础统计数据
            src_stats = os.path.join(self.erp_project_path, "analysis", "basic_statistics.csv")
            dst_stats = os.path.join(self.data_path, "basic_statistics.csv")
            if os.path.exists(src_stats):
                shutil.copy2(src_stats, dst_stats)
            
            # 同步时间序列数据
            markets = {
                "CSI300": "CSI300_erp.csv",
                "HSI_mixed": "HSI_erp_mixed.csv",
                "HSI_cn": "HSI_erp_cn.csv",
                "HSI_us": "HSI_erp_us.csv",
                "SPX": "SPX_erp.csv"
            }
            
            for market_key, erp_filename in markets.items():
                try:
                    # 1. 获取ERP数据
                    erp_file = os.path.join(self.erp_project_path, "data", "output", erp_filename)
                    
                    # 2. 获取市场指数数据
                    base_market = market_key.split("_")[0]  # 获取基础市场名称（去掉后缀）
                    market_file = os.path.join(self.erp_project_path, "data", "processed", f"{base_market}_processed.csv")
                    
                    if not os.path.exists(erp_file) or not os.path.exists(market_file):
                        continue
                    
                    # 3. 读取数据
                    erp_df = pd.read_csv(erp_file)
                    market_df = pd.read_csv(market_file)
                    
                    # 4. 数据预处理
                    # 统一日期格式
                    erp_df['trade_date'] = pd.to_datetime(erp_df['trade_date'])
                    market_df['trade_date'] = pd.to_datetime(market_df['trade_date'])
                    
                    # 重新计算ERP
                    erp_df['ep'] = (1 / erp_df['pe']) * 100  # EP已经是百分比
                    erp_df['rf_pct'] = erp_df['rf'] * 100    # 转换RF为百分比
                    erp_df['erp'] = erp_df['ep'] - erp_df['rf_pct']  # 正确计算ERP
                    
                    # 5. 合并数据
                    # 确保market_df中有close列
                    if 'close' not in market_df.columns:
                        continue
                    
                    # 合并数据，保留所需列
                    merged_df = pd.merge(
                        erp_df[['trade_date', 'erp', 'pe', 'rf']], 
                        market_df[['trade_date', 'close']], 
                        on='trade_date',
                        how='inner'  # 只保留两个数据集都有的日期
                    )
                    
                    # 6. 数据验证
                    required_columns = ['trade_date', 'erp', 'pe', 'rf', 'close']
                    if not all(col in merged_df.columns for col in required_columns):
                        continue
                    
                    # 7. 数据清理
                    # 处理无效值
                    merged_df = merged_df.replace([np.inf, -np.inf], np.nan)
                    merged_df = merged_df.dropna(subset=['erp', 'close'])
                    
                    # 8. 保存处理后的数据
                    dst_file = os.path.join(self.data_path, f"{market_key}_erp.csv")
                    merged_df.to_csv(dst_file, index=False)
                    
                except Exception:
                    continue
        
        except Exception:
            pass
    
    def load_latest_data(self):
        """加载最新的ERP分析数据"""
        try:
            # 加载基础统计数据
            stats_df = pd.read_csv(
                os.path.join(self.data_path, "basic_statistics.csv")
            )
            
            # 加载时间序列数据
            time_series = {}
            for market in ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"]:
                df = pd.read_csv(
                    os.path.join(self.data_path, f"{market}_erp.csv")
                )
                
                # 确保日期列正确
                df["trade_date"] = pd.to_datetime(df["trade_date"])
                
                # 确保必要的列存在
                required_columns = ["trade_date", "erp", "pe", "rf", "close"]
                if not all(col in df.columns for col in required_columns):
                    raise ValueError(f"数据文件缺少必要的列: {required_columns}")
                
                # 处理无效值
                df = df.replace([np.inf, -np.inf], np.nan)
                df = df.dropna(subset=["erp", "close"])
                
                time_series[market] = df
            
            # 计算相关性矩阵
            correlation_data = pd.DataFrame()
            for market in ["CSI300", "HSI_mixed", "HSI_cn", "HSI_us", "SPX"]:
                correlation_data[self._market_names[market]] = time_series[market]["erp"]
            
            correlation = correlation_data.corr()
            
            return {
                "stats": stats_df,
                "time_series": time_series,
                "correlation": correlation
            }
        except Exception as e:
            st.error(f"数据加载失败：{str(e)}")
            return None
    
    def get_market_name(self, market_code: str) -> str:
        """获取市场的中文名称"""
        return self._market_names.get(market_code, market_code) 