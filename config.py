"""
配置文件
"""
import os
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "deepinsight.db"

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-reasoner"

# 定价配置（RMB）
PRICING = {
    "input": 0.55 / 1_000_000,      # ¥0.55 per 1M tokens
    "output": 2.19 / 1_000_000,     # ¥2.19 per 1M tokens
}

# 缓存配置
CACHE_CONFIG = {
    "movement_analysis_ttl": 3600,      # 1 小时
    "holdings_analysis_ttl": 14400,     # 4 小时
    "news_summary_ttl": 7200,           # 2 小时
}

# 数据获取配置
DATA_CONFIG = {
    "use_mock_data": True,              # 默认使用模拟数据
    "volatility_threshold": 1.5,        # 波动阈值（%）
    "news_lookback_hours": 12,          # 新闻回溯时间
    "max_holdings_display": 5,          # 最多显示持仓数
}

# Streamlit 配置
STREAMLIT_CONFIG = {
    "page_title": "DeepInsight 基金智投系统",
    "page_icon": "📊",
    "layout": "wide",
    "theme": "dark"
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
