"""
缓存管理模块：智能缓存与成本优化
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import get_cached_analysis, cache_analysis
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器"""
    
    # 缓存策略配置
    CACHE_STRATEGIES = {
        "movement_analysis": {
            "ttl_hours": 1,
            "description": "基金波动分析缓存"
        },
        "holdings_analysis": {
            "ttl_hours": 4,
            "description": "持仓分析缓存"
        },
        "news_summary": {
            "ttl_hours": 2,
            "description": "新闻摘要缓存"
        }
    }
    
    @staticmethod
    def should_use_cache(
        fund_code: str,
        analysis_type: str,
        volatility_pct: float
    ) -> bool:
        """
        判断是否应该使用缓存
        
        Args:
            fund_code: 基金代码
            analysis_type: 分析类型
            volatility_pct: 波动幅度（%）
        
        Returns:
            是否使用缓存
        """
        
        # 如果波动超过 ±1.5%，不使用缓存
        if abs(volatility_pct) > 1.5:
            logger.info(f"波动幅度 {volatility_pct}% 超过阈值，不使用缓存")
            return False
        
        # 检查缓存是否存在且未过期
        strategy = CacheManager.CACHE_STRATEGIES.get(analysis_type, {})
        ttl_hours = strategy.get("ttl_hours", 1)
        
        cached = get_cached_analysis(fund_code, analysis_type, max_age_hours=ttl_hours)
        
        if cached:
            logger.info(f"找到有效缓存: {fund_code} - {analysis_type}")
            return True
        
        return False
    
    @staticmethod
    def get_cache_status(fund_code: str, analysis_type: str) -> Dict[str, Any]:
        """获取缓存状态"""
        cached = get_cached_analysis(fund_code, analysis_type, max_age_hours=24)
        
        if cached:
            try:
                data = json.loads(cached)
                return {
                    "exists": True,
                    "analysis_time": data.get("analysis_time"),
                    "is_valid": True
                }
            except json.JSONDecodeError:
                return {
                    "exists": True,
                    "is_valid": False
                }
        
        return {
            "exists": False,
            "is_valid": False
        }
    
    @staticmethod
    def estimate_token_savings(
        original_tokens: int,
        cache_hit_rate: float = 0.7
    ) -> Dict[str, Any]:
        """
        估计缓存节省的 Token
        
        Args:
            original_tokens: 原始 Token 数
            cache_hit_rate: 缓存命中率（0-1）
        
        Returns:
            节省统计
        """
        
        cached_tokens = int(original_tokens * cache_hit_rate)
        saved_tokens = cached_tokens
        
        # 基于 DeepSeek 定价
        input_price = 0.55 / 1_000_000
        output_price = 2.19 / 1_000_000
        
        # 假设 output 是 input 的 2 倍
        avg_price = (input_price + output_price * 2) / 3
        saved_cost = saved_tokens * avg_price
        
        return {
            "total_tokens": original_tokens,
            "cached_tokens": cached_tokens,
            "saved_tokens": saved_tokens,
            "saved_cost": round(saved_cost, 4),
            "cache_hit_rate": cache_hit_rate
        }
    
    @staticmethod
    def optimize_news_input(news_items: list, max_chars: int = 300) -> str:
        """
        优化新闻输入：精简内容以节省 Token
        
        Args:
            news_items: 新闻列表
            max_chars: 最大字符数
        
        Returns:
            精简后的新闻文本
        """
        
        optimized = []
        total_chars = 0
        
        for news in news_items:
            title = news.get("title", "")
            summary = news.get("summary", "")[:100]  # 限制摘要长度
            
            item_text = f"{title}. {summary}"
            
            if total_chars + len(item_text) <= max_chars:
                optimized.append(item_text)
                total_chars += len(item_text)
            else:
                break
        
        result = " | ".join(optimized)
        
        logger.info(f"新闻输入优化: {len(news_items)} 条 -> {len(result)} 字符")
        
        return result
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "strategies": CacheManager.CACHE_STRATEGIES,
            "description": "缓存策略配置"
        }

# 导出单例
cache_manager = CacheManager()
