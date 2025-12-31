# DeepInsight 基金实时智投系统

## 📊 项目概述

**DeepInsight** 是一个由 DeepSeek-R1 驱动的专业基金投研仪表盘，集资产监控、实时行情归因、深度研判及成本控制于一体。

### 核心特性

- 🎯 **持久化收藏管理**：支持基金代码增删改查，刷新不丢失
- 📈 **实时看板**：调用 AkShare 展示收藏基金的实时估值、涨跌幅及日内走势
- 🤖 **DeepSeek-R1 深度研判**：
  - 智能归因：拆解重仓股涨跌对净值的贡献度
  - 思考过程展示（CoT）：分析波动是"情绪噪音"还是"基本面反转"
  - 隐形持仓检测：估值与持仓走势背离提示
- 💰 **成本控制**：
  - 1 小时智能缓存，短时间内无重大异动直接读取旧报告
  - 新闻输入精简（<300 字）节省 Token
  - 实时费用看板显示 Token 消耗、RMB 费用、单次分析费用

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Streamlit
- OpenAI SDK（用于 DeepSeek API）
- AkShare（基金数据）
- SQLite3（本地存储）

### 安装步骤

1. **克隆/复制项目**

```bash
cd /home/ubuntu/deepinsight
```

2. **安装依赖**

```bash
pip3 install streamlit akshare openai python-dateutil pytz
```

3. **配置 API Key**

从 [DeepSeek 官网](https://platform.deepseek.com) 获取 API Key，在应用启动后在侧边栏配置。

4. **启动应用**

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

## 📖 使用指南

### 第一步：配置 API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com)
2. 获取 API Key
3. 在应用侧边栏的"系统配置"中粘贴 API Key
4. 系统会显示 "✅ API Key 已配置"

### 第二步：管理收藏基金

1. 在侧边栏"快速操作"中点击"➕ 添加基金"
2. 输入基金代码和名称
3. 点击"添加收藏"
4. 基金将出现在实时看板中

**默认收藏基金：**
- 易方达蓝筹精选（005827）
- 纳指 ETF（513100）

### 第三步：查看实时数据

- **实时看板**：显示所有收藏基金的当前净值、日涨跌幅
- **详细分析**：选择基金后查看重仓股贡献度

### 第四步：触发深度分析

1. 在"详细分析"区域选择基金
2. 点击"🚀 更新研判"按钮
3. 系统调用 DeepSeek-R1 进行分析
4. 查看：
   - 💭 思考过程（CoT）
   - 📋 分析结果
   - 💵 成本统计

### 第五步：监控成本

- **成本统计看板**显示：
  - 📊 今日累计 Token 消耗
  - 💵 今日估算费用（RMB）
  - 🎯 单次分析平均费用
  - 📈 7 日成本趋势

## 🏗️ 系统架构

```
deepinsight/
├── app.py                 # Streamlit 前端应用
├── database.py            # 数据库管理（SQLite）
├── data_provider.py       # 数据接口（AkShare + 模拟）
├── deepseek_analyzer.py   # DeepSeek-R1 分析引擎
├── cache_manager.py       # 缓存管理与成本优化
├── config.py              # 配置文件
└── deepinsight.db         # SQLite 数据库（自动创建）
```

### 模块说明

#### database.py
- 基金收藏表：存储用户收藏的基金
- 分析缓存表：存储 DeepSeek 分析结果（1 小时过期）
- 成本统计表：记录每次分析的 Token 消耗和费用

#### data_provider.py
- `FundDataProvider.get_fund_realtime()`：获取基金实时数据
- `FundDataProvider.get_fund_holdings()`：获取基金持仓
- `FundDataProvider.calculate_holding_contribution()`：计算持仓贡献度
- `FundDataProvider.get_industry_news()`：获取相关新闻

#### deepseek_analyzer.py
- `DeepSeekAnalyzer.analyze_fund_movement()`：主分析方法
  - 检查缓存（1 小时有效期）
  - 波动 < 1.5% 时使用本地分析
  - 波动 >= 1.5% 时调用 DeepSeek-R1
- 成本计算：基于实际 Token 消耗

#### cache_manager.py
- 缓存策略配置
- 缓存命中判断
- Token 节省估计
- 新闻输入优化（<300 字）

## 💡 工作流程

### 完整分析流程

```
用户点击"更新研判"
    ↓
检查 1 小时缓存
    ├─ 缓存命中 → 返回缓存结果（0 费用）
    └─ 缓存未命中 ↓
检查波动幅度
    ├─ < 1.5% → 本地分析（0 费用）
    └─ >= 1.5% ↓
调用 DeepSeek-R1
    ├─ 获取新闻（过去 12 小时）
    ├─ 精简新闻（<300 字）
    ├─ 构建 Prompt
    ├─ 发送 API 请求
    ├─ 提取思考过程（CoT）
    └─ 计算 Token 消耗 & 费用 ↓
缓存结果（1 小时）
    ↓
显示结果 & 费用统计
```

### 成本优化策略

| 策略 | 节省方式 | 效果 |
|------|--------|------|
| 缓存机制 | 1 小时内无重大异动直接读取 | 节省 70% Token（假设 70% 缓存命中率） |
| 波动阈值 | 波动 < 1.5% 使用本地分析 | 避免不必要的 API 调用 |
| 输入精简 | 新闻摘要限制 <300 字 | 减少 30-50% 输入 Token |
| 智能触发 | 仅在用户点击时调用 | 避免自动轮询 |

## 📊 数据流

### 基金数据源

1. **AkShare 接口**（优先）
   - 实时净值
   - 日涨跌幅
   - 持仓信息

2. **模拟数据**（备用）
   - 演示模式下使用
   - 包含完整的基金和持仓数据

### 新闻数据源

- 模拟新闻（演示）
- 支持扩展为真实新闻 API

## 🔧 配置说明

### 环境变量

```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

### 应用配置（config.py）

```python
# DeepSeek 定价（RMB）
PRICING = {
    "input": 0.55 / 1_000_000,      # ¥0.55 per 1M tokens
    "output": 2.19 / 1_000_000,     # ¥2.19 per 1M tokens
}

# 缓存 TTL
CACHE_CONFIG = {
    "movement_analysis_ttl": 3600,      # 1 小时
    "holdings_analysis_ttl": 14400,     # 4 小时
}

# 数据获取
DATA_CONFIG = {
    "volatility_threshold": 1.5,        # 波动阈值（%）
    "news_lookback_hours": 12,          # 新闻回溯时间
}
```

## 🧪 测试

### 运行完整功能测试

```bash
python3 << 'EOF'
from database import init_database, add_favorite, get_favorites
from data_provider import FundDataProvider
from deepseek_analyzer import DeepSeekAnalyzer

# 初始化
init_database()
add_favorite("005827", "易方达蓝筹精选")

# 获取数据
provider = FundDataProvider()
fund_data = provider.get_fund_realtime("005827", use_mock=True)
print(f"基金净值: ¥{fund_data['current_value']:.4f}")

# 执行分析
analyzer = DeepSeekAnalyzer()
holdings = provider.get_fund_holdings("005827", use_mock=True)
contributions = provider.calculate_holding_contribution(fund_data, holdings)

analysis = analyzer.analyze_fund_movement(
    fund_code="005827",
    fund_name="易方达蓝筹精选",
    daily_change_pct=fund_data['daily_change_pct'],
    holdings_contribution=contributions,
    news_items=[],
    use_mock=True
)
print(f"分析完成，费用: ¥{analysis['estimated_cost']:.4f}")
EOF
```

## 📱 界面说明

### 实时看板
- 显示所有收藏基金的卡片
- 实时净值、日涨跌幅、颜色编码（绿/红）

### 详细分析
- 基本指标：当前净值、日涨跌幅、更新时间
- 重仓股贡献度表格
- 深度研判按钮

### 成本统计看板
- 今日累计 Token
- 今日估算费用（RMB）
- 单次分析平均费用
- 7 日成本趋势图表

## ⚠️ 免责声明

本系统仅供参考，**不构成投资建议**。投资有风险，请谨慎决策。

## 🔐 数据隐私

- 所有数据存储在本地 SQLite 数据库
- API Key 仅在内存中使用，不被保存
- 建议定期清理缓存数据

## 📞 支持

如有问题或建议，请提交 Issue 或联系开发者。

## 📄 许可证

MIT License

---

**版本**: 1.0  
**最后更新**: 2025-12-31  
**作者**: Manus AI