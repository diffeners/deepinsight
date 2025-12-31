"""
数据库管理模块：基金收藏、缓存、成本统计
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os

DB_PATH = Path(__file__).parent / "deepinsight.db"

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 基金收藏表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_code TEXT UNIQUE NOT NULL,
            fund_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 缓存表（用于 DeepSeek 分析结果）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_code TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fund_code, analysis_type)
        )
    """)
    
    # 成本统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            estimated_cost REAL DEFAULT 0.0,
            operation_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def add_favorite(fund_code: str, fund_name: str) -> bool:
    """添加收藏基金"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO favorites (fund_code, fund_name) VALUES (?, ?)",
            (fund_code, fund_name)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_favorite(fund_code: str) -> bool:
    """删除收藏基金"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE fund_code = ?", (fund_code,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_favorites() -> List[Dict]:
    """获取所有收藏基金"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT fund_code, fund_name FROM favorites ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"code": row[0], "name": row[1]} for row in rows]

def cache_analysis(fund_code: str, analysis_type: str, result: str) -> None:
    """缓存分析结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO analysis_cache (fund_code, analysis_type, result, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (fund_code, analysis_type, result))
    conn.commit()
    conn.close()

def get_cached_analysis(fund_code: str, analysis_type: str, max_age_hours: int = 1) -> Optional[str]:
    """获取缓存的分析结果（检查时效性）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    cursor.execute("""
        SELECT result FROM analysis_cache 
        WHERE fund_code = ? AND analysis_type = ? AND created_at > ?
    """, (fund_code, analysis_type, cutoff_time.isoformat()))
    
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def log_cost(tokens_used: int, estimated_cost: float, operation_type: str = "analysis") -> None:
    """记录成本消耗"""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO cost_log (date, tokens_used, estimated_cost, operation_type)
        VALUES (?, ?, ?, ?)
    """, (today, tokens_used, estimated_cost, operation_type))
    
    conn.commit()
    conn.close()

def get_today_cost() -> Tuple[int, float]:
    """获取今日累计成本"""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(tokens_used), SUM(estimated_cost) FROM cost_log WHERE date = ?
    """, (today,))
    
    row = cursor.fetchone()
    conn.close()
    
    tokens = row[0] or 0
    cost = row[1] or 0.0
    return tokens, cost

def get_cost_history(days: int = 7) -> List[Dict]:
    """获取成本历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT date, SUM(tokens_used), SUM(estimated_cost) 
        FROM cost_log 
        WHERE date >= ?
        GROUP BY date
        ORDER BY date DESC
    """, (start_date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{"date": row[0], "tokens": row[1] or 0, "cost": row[2] or 0.0} for row in rows]

def clear_old_cache(days: int = 7) -> None:
    """清理过期缓存"""
    cutoff_time = datetime.now() - timedelta(days=days)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM analysis_cache WHERE created_at < ?",
        (cutoff_time.isoformat(),)
    )
    conn.commit()
    conn.close()

# 初始化数据库
if not DB_PATH.exists():
    init_database()
