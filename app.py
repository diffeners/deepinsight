"""
DeepInsight 基金实时智投系统
Streamlit 前端应用
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import sys

# 导入本地模块
from database import (
    init_database, add_favorite, remove_favorite, get_favorites,
    get_today_cost, get_cost_history
)
from data_provider import FundDataProvider
from deepseek_analyzer import DeepSeekAnalyzer

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="DeepInsight 基金智投系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式（深色金融界面）
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background-color: #0f1419;
        color: #e0e0e0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
        border-left: 4px solid #00d4ff;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .positive {
        color: #00ff41;
    }
    
    .negative {
        color: #ff4444;
    }
    
    .neutral {
        color: #ffa500;
    }
    
    .header-title {
        font-size: 32px;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #00ff41);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    .cost-panel {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00d4ff;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    
    .analysis-box {
        background: #1a2332;
        border-left: 4px solid #00ff41;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化 ====================
init_database()

if "analyzer" not in st.session_state:
    st.session_state.analyzer = DeepSeekAnalyzer()

if "provider" not in st.session_state:
    st.session_state.provider = FundDataProvider()

if "use_mock_data" not in st.session_state:
    st.session_state.use_mock_data = True

# ==================== 侧边栏配置 ====================
with st.sidebar:
    st.markdown("### ⚙️ 系统配置")
    
    # API Key 配置
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        help="从 https://platform.deepseek.com 获取"
    )
    
    if api_key:
        st.session_state.analyzer = DeepSeekAnalyzer(api_key)
        st.success("✅ API Key 已配置")
    
    # 数据源选择
    st.markdown("### 📊 数据源")
    st.session_state.use_mock_data = st.checkbox(
        "使用模拟数据（演示模式）",
        value=True,
        help="勾选时使用模拟数据，取消时尝试调用 AkShare"
    )
    
    st.markdown("---")
    st.markdown("### 📈 快速操作")
    
    # 添加收藏
    with st.expander("➕ 添加基金"):
        col1, col2 = st.columns(2)
        with col1:
            fund_code = st.text_input("基金代码", placeholder="005827")
        with col2:
            fund_name = st.text_input("基金名称", placeholder="易方达蓝筹精选")
        
        if st.button("添加收藏", key="add_fav"):
            if fund_code and fund_name:
                if add_favorite(fund_code, fund_name):
                    st.success(f"✅ 已添加 {fund_name}")
                    st.rerun()
                else:
                    st.warning("⚠️ 基金已存在")
            else:
                st.error("❌ 请填写完整信息")
    
    st.markdown("---")
    st.markdown("### 📚 帮助")
    st.markdown("""
    **使用指南：**
    1. 配置 DeepSeek API Key
    2. 添加关注的基金
    3. 点击"更新研判"触发分析
    4. 查看成本统计
    """)

# ==================== 主页面 ====================
st.markdown('<div class="header-title">📊 DeepInsight 基金智投系统</div>', unsafe_allow_html=True)
st.markdown("*由 DeepSeek-R1 驱动的专业基金研究仪表盘*")
st.markdown("---")

# 获取收藏基金
favorites = get_favorites()

if not favorites:
    # 初始化默认收藏
    add_favorite("005827", "易方达蓝筹精选")
    add_favorite("513100", "纳指 ETF")
    st.rerun()

# ==================== 实时看板 ====================
st.markdown("### 📊 实时看板")

# 创建列布局
cols = st.columns(len(favorites))

fund_data_cache = {}

for idx, (col, fav) in enumerate(zip(cols, favorites)):
    with col:
        fund_code = fav["code"]
        fund_name = fav["name"]
        
        # 获取基金数据
        fund_data = st.session_state.provider.get_fund_realtime(
            fund_code,
            use_mock=st.session_state.use_mock_data
        )
        
        if fund_data:
            fund_data_cache[fund_code] = fund_data
            
            # 确定颜色
            change_pct = fund_data.get("daily_change_pct", 0)
            if change_pct > 0:
                color_class = "positive"
                arrow = "📈"
            elif change_pct < 0:
                color_class = "negative"
                arrow = "📉"
            else:
                color_class = "neutral"
                arrow = "➡️"
            
            # 显示卡片
            st.markdown(f"""
            <div class="metric-card">
                <h4>{fund_name}</h4>
                <p style="font-size: 12px; color: #888;">{fund_code}</p>
                <p style="font-size: 24px; font-weight: bold;">¥{fund_data.get('current_value', 0):.4f}</p>
                <p class="{color_class}" style="font-size: 18px; font-weight: bold;">
                    {arrow} {change_pct:+.2f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 删除按钮
            if st.button("🗑️ 删除", key=f"del_{fund_code}"):
                remove_favorite(fund_code)
                st.rerun()

st.markdown("---")

# ==================== 详细分析 ====================
st.markdown("### 🔍 详细分析")

selected_fund = st.selectbox(
    "选择基金进行深度分析",
    options=[f["code"] for f in favorites],
    format_func=lambda x: next((f["name"] for f in favorites if f["code"] == x), x)
)

if selected_fund and selected_fund in fund_data_cache:
    fund_data = fund_data_cache[selected_fund]
    fund_name = next((f["name"] for f in favorites if f["code"] == selected_fund), "")
    
    # 显示基本信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前净值", f"¥{fund_data.get('current_value', 0):.4f}")
    with col2:
        change = fund_data.get("daily_change_pct", 0)
        st.metric("日涨跌幅", f"{change:+.2f}%", delta=f"{change:+.2f}%")
    with col3:
        st.metric("更新时间", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # 持仓贡献分析
    st.markdown("#### 📍 重仓股贡献度")
    
    holdings = st.session_state.provider.get_fund_holdings(
        selected_fund,
        use_mock=st.session_state.use_mock_data
    )
    
    if holdings:
        # 计算贡献度
        contributions = st.session_state.provider.calculate_holding_contribution(
            fund_data, holdings
        )
        
        # 显示表格
        df_holdings = pd.DataFrame(contributions)
        st.dataframe(
            df_holdings[["stock", "weight", "change", "contribution"]].head(5),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 深度分析触发
    st.markdown("#### 🤖 DeepSeek-R1 深度研判")
    
    if st.button("🚀 更新研判", key=f"analyze_{selected_fund}"):
        with st.spinner("🔄 正在调用 DeepSeek-R1 进行深度分析..."):
            # 获取新闻
            news = st.session_state.provider.get_industry_news(
                keywords=fund_name,
                hours=12
            )
            
            # 执行分析
            analysis = st.session_state.analyzer.analyze_fund_movement(
                fund_code=selected_fund,
                fund_name=fund_name,
                daily_change_pct=fund_data.get("daily_change_pct", 0),
                holdings_contribution=contributions if holdings else [],
                news_items=news,
                use_cache=True,
                use_mock=st.session_state.use_mock_data
            )
            
            # 显示思考过程
            if analysis.get("thinking_process"):
                with st.expander("💭 思考过程（CoT）", expanded=False):
                    st.markdown(analysis["thinking_process"])
            
            # 显示分析结果
            if analysis.get("analysis_result"):
                st.markdown("#### 📋 分析结果")
                st.markdown(analysis["analysis_result"])
            elif analysis.get("assessment"):
                st.markdown("#### 📋 分析结果")
                st.markdown(analysis["assessment"])
            
            # 显示成本信息
            if analysis.get("tokens_used", 0) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Token 消耗", f"{analysis['tokens_used']}")
                with col2:
                    st.metric("估算费用", f"¥{analysis.get('estimated_cost', 0):.4f}")
                with col3:
                    st.metric("数据来源", "DeepSeek-R1" if not analysis.get("is_mock") else "模拟")
    
    st.markdown("---")
    
    # 相关新闻
    st.markdown("#### 📰 相关新闻")
    news = st.session_state.provider.get_industry_news(fund_name, hours=12)
    
    for news_item in news:
        with st.expander(f"📌 {news_item['title']}"):
            st.markdown(f"**来源:** {news_item['source']}")
            st.markdown(f"**时间:** {news_item['time']}")
            st.markdown(f"**摘要:** {news_item['summary']}")

st.markdown("---")

# ==================== 成本统计看板 ====================
st.markdown("### 💰 成本统计看板")

# 获取今日成本
today_tokens, today_cost = get_today_cost()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="cost-panel">
        <h3 style="color: #00d4ff; margin: 0;">📊 今日累计</h3>
        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #00ff41;">
            {today_tokens:,} Tokens
        </p>
        <p style="color: #888; font-size: 12px;">Token 消耗</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="cost-panel">
        <h3 style="color: #00d4ff; margin: 0;">💵 今日费用</h3>
        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #ffa500;">
            ¥{today_cost:.4f}
        </p>
        <p style="color: #888; font-size: 12px;">估算费用（RMB）</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # 计算平均单次费用
    avg_cost = today_cost / max(1, today_tokens) if today_tokens > 0 else 0
    st.markdown(f"""
    <div class="cost-panel">
        <h3 style="color: #00d4ff; margin: 0;">🎯 单次分析</h3>
        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #00ff41;">
            ¥{avg_cost:.6f}
        </p>
        <p style="color: #888; font-size: 12px;">平均单次费用</p>
    </div>
    """, unsafe_allow_html=True)

# 历史成本趋势
st.markdown("#### 📈 7 日成本趋势")

history = get_cost_history(days=7)
if history:
    df_history = pd.DataFrame(history)
    
    # 创建两个图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(
            df_history.set_index("date")["tokens"],
            use_container_width=True
        )
        st.markdown("**Token 消耗趋势**")
    
    with col2:
        st.bar_chart(
            df_history.set_index("date")["cost"],
            use_container_width=True
        )
        st.markdown("**费用趋势（RMB）**")

st.markdown("---")

# ==================== 页脚 ====================
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px; margin-top: 40px;">
    <p>DeepInsight 基金智投系统 v1.0 | 由 DeepSeek-R1 驱动</p>
    <p>⚠️ 免责声明：本系统仅供参考，不构成投资建议。投资有风险，请谨慎决策。</p>
</div>
""", unsafe_allow_html=True)
