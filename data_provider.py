"""
数据提供者模块：从 AkShare 获取基金实时数据
支持模拟数据以应对网络问题
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class FundDataProvider:
    """基金数据提供者"""
    
    # 模拟数据库（用于演示）
    MOCK_DATA = {
        "005827": {
            "name": "易方达蓝筹精选",
            "base_value": 2.8534,
            "daily_change": -0.45,
            "top_holdings": [
                {"stock": "贵州茅台", "code": "600519", "weight": 8.5, "change": -1.2},
                {"stock": "中国平安", "code": "601318", "weight": 7.2, "change": 0.8},
                {"stock": "招商银行", "code": "600036", "weight": 6.1, "change": 1.5},
                {"stock": "美的集团", "code": "000333", "weight": 5.8, "change": -0.3},
                {"stock": "格力电器", "code": "000651", "weight": 5.2, "change": -2.1},
            ]
        },
        "513100": {
            "name": "纳指 ETF",
            "base_value": 3.2156,
            "daily_change": 1.23,
            "top_holdings": [
                {"stock": "微软", "code": "MSFT", "weight": 12.3, "change": 2.1},
                {"stock": "苹果", "code": "AAPL", "weight": 11.8, "change": 1.5},
                {"stock": "英伟达", "code": "NVDA", "weight": 10.2, "change": 3.2},
                {"stock": "亚马逊", "code": "AMZN", "weight": 9.5, "change": 0.8},
                {"stock": "特斯拉", "code": "TSLA", "weight": 8.1, "change": -1.5},
            ]
        }
    }
    
    @staticmethod
    def get_fund_realtime(fund_code: str, use_mock: bool = False) -> Optional[Dict]:
        """获取基金实时数据"""
        try:
            if use_mock or fund_code in FundDataProvider.MOCK_DATA:
                return FundDataProvider._get_mock_data(fund_code)
            
            # 尝试从 AkShare 获取
            try:
                df = ak.fund_basic_info_sina(symbol=fund_code)
                if df.empty:
                    return FundDataProvider._get_mock_data(fund_code)
                
                row = df.iloc[0]
                return {
                    "code": fund_code,
                    "name": row.get("name", ""),
                    "current_value": float(row.get("per_nav", 0)),
                    "daily_change_pct": float(row.get("daily_growth", 0)),
                    "daily_change_amount": 0,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.warning(f"AkShare 获取失败，使用模拟数据: {e}")
                return FundDataProvider._get_mock_data(fund_code)
                
        except Exception as e:
            logger.error(f"获取基金数据失败: {e}")
            return None
    
    @staticmethod
    def _get_mock_data(fund_code: str) -> Dict:
        """获取模拟数据"""
        if fund_code not in FundDataProvider.MOCK_DATA:
            # 生成随机基金数据
            return {
                "code": fund_code,
                "name": f"基金{fund_code}",
                "current_value": round(2.5 + random.random() * 2, 4),
                "daily_change_pct": round((random.random() - 0.5) * 3, 2),
                "daily_change_amount": round((random.random() - 0.5) * 0.1, 4),
                "timestamp": datetime.now().isoformat()
            }
        
        data = FundDataProvider.MOCK_DATA[fund_code]
        # 添加随机波动
        volatility = (random.random() - 0.5) * 0.5
        return {
            "code": fund_code,
            "name": data["name"],
            "current_value": round(data["base_value"] + volatility, 4),
            "daily_change_pct": round(data["daily_change"] + (random.random() - 0.5) * 0.3, 2),
            "daily_change_amount": round((data["daily_change"] / 100) * data["base_value"], 4),
            "timestamp": datetime.now().isoformat(),
            "top_holdings": data["top_holdings"]
        }
    
    @staticmethod
    def get_fund_holdings(fund_code: str, use_mock: bool = False) -> List[Dict]:
        """获取基金持仓"""
        try:
            if use_mock or fund_code in FundDataProvider.MOCK_DATA:
                return FundDataProvider.MOCK_DATA[fund_code].get("top_holdings", [])
            
            # 尝试从 AkShare 获取
            try:
                df = ak.fund_portfolio_hold_sina(symbol=fund_code)
                if df.empty:
                    return FundDataProvider.MOCK_DATA[fund_code].get("top_holdings", [])
                
                holdings = []
                for _, row in df.head(5).iterrows():
                    holdings.append({
                        "stock": row.get("stock_name", ""),
                        "code": row.get("stock_code", ""),
                        "weight": float(row.get("hold_ratio", 0)),
                        "change": 0  # AkShare 可能不提供实时涨跌
                    })
                return holdings
            except Exception as e:
                logger.warning(f"AkShare 获取持仓失败，使用模拟数据: {e}")
                return FundDataProvider.MOCK_DATA[fund_code].get("top_holdings", [])
                
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []
    
    @staticmethod
    def get_industry_news(keywords: str, hours: int = 12) -> List[Dict]:
        """获取行业新闻（模拟）"""
        # 模拟新闻数据
        mock_news = [
            {
                "title": "央行公开市场操作，释放流动性",
                "summary": "央行今日进行公开市场操作，投放流动性以稳定市场预期。",
                "source": "新华社",
                "time": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "title": "科技股集体上涨，AI 概念持续火热",
                "summary": "受全球 AI 发展推动，科技股今日表现强劲，纳斯达克指数创新高。",
                "source": "财经网",
                "time": (datetime.now() - timedelta(hours=4)).isoformat()
            },
            {
                "title": "消费板块承压，社零数据不及预期",
                "summary": "最新社会消费品零售总额数据低于预期，消费股承压下行。",
                "source": "证券时报",
                "time": (datetime.now() - timedelta(hours=6)).isoformat()
            },
            {
                "title": "房地产政策调整，利好板块反弹",
                "summary": "政策面传来利好信号，房地产及相关产业链股票出现反弹。",
                "source": "经济观察网",
                "time": (datetime.now() - timedelta(hours=8)).isoformat()
            }
        ]
        
        return mock_news[:3]  # 返回最近 3 条新闻
    
    @staticmethod
    def calculate_holding_contribution(fund_data: Dict, holdings: List[Dict]) -> List[Dict]:
        """计算重仓股对净值的贡献度"""
        if not holdings:
            return []
        
        total_weight = sum(h.get("weight", 0) for h in holdings)
        if total_weight == 0:
            total_weight = 1
        
        contributions = []
        for holding in holdings:
            weight = holding.get("weight", 0) / 100  # 转换为小数
            change_pct = holding.get("change", 0) / 100
            contribution = weight * change_pct * 100  # 转换为百分比
            
            contributions.append({
                "stock": holding.get("stock", ""),
                "code": holding.get("code", ""),
                "weight": holding.get("weight", 0),
                "change": holding.get("change", 0),
                "contribution": round(contribution, 3)
            })
        
        # 按贡献度排序
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions

# 导出单例
provider = FundDataProvider()
