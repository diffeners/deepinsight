"""
DeepSeek-R1 分析引擎：深度研判与思考过程展示
集成成本控制和缓存机制
"""
import os
import json
from typing import Dict, Optional, Tuple, List
from openai import OpenAI
from datetime import datetime
import logging
from database import cache_analysis, get_cached_analysis, log_cost

logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """DeepSeek-R1 分析器"""
    
    # 定价信息（基于 DeepSeek 官方）
    PRICING = {
        "input": 0.55 / 1_000_000,      # ¥0.55 per 1M tokens
        "output": 2.19 / 1_000_000,     # ¥2.19 per 1M tokens
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器"""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.client = None
        self.total_tokens_today = 0
        self.total_cost_today = 0.0
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
    
    def analyze_fund_movement(
        self,
        fund_code: str,
        fund_name: str,
        daily_change_pct: float,
        holdings_contribution: List[Dict],
        news_items: List[Dict],
        use_cache: bool = True,
        use_mock: bool = False
    ) -> Dict:
        """
        分析基金波动
        
        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            daily_change_pct: 日涨跌幅
            holdings_contribution: 重仓股贡献度列表
            news_items: 相关新闻列表
            use_cache: 是否使用缓存
            use_mock: 是否使用模拟数据
        
        Returns:
            分析结果字典
        """
        
        # 检查缓存
        if use_cache:
            cached = get_cached_analysis(fund_code, "movement_analysis")
            if cached:
                logger.info(f"使用缓存分析: {fund_code}")
                return json.loads(cached)
        
        # 如果波动不大或无 API Key，使用本地分析
        if abs(daily_change_pct) < 1.5 or use_mock or not self.client:
            return self._local_analysis(
                fund_code, fund_name, daily_change_pct,
                holdings_contribution, news_items
            )
        
        # 调用 DeepSeek-R1
        return self._deepseek_analysis(
            fund_code, fund_name, daily_change_pct,
            holdings_contribution, news_items
        )
    
    def _local_analysis(
        self,
        fund_code: str,
        fund_name: str,
        daily_change_pct: float,
        holdings_contribution: List[Dict],
        news_items: List[Dict]
    ) -> Dict:
        """本地分析（无需调用 API）"""
        
        # 计算主要贡献股
        top_contributor = holdings_contribution[0] if holdings_contribution else None
        
        # 判断波动性质
        if abs(daily_change_pct) < 0.5:
            volatility_type = "低波动"
            assessment = "市场情绪平稳，基金表现稳定"
        elif abs(daily_change_pct) < 1.5:
            volatility_type = "正常波动"
            assessment = "市场波动正常，持仓结构未发生重大变化"
        else:
            volatility_type = "高波动"
            assessment = "市场出现明显波动，建议关注持仓变化"
        
        # 构建分析结果
        analysis = {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "analysis_time": datetime.now().isoformat(),
            "daily_change_pct": daily_change_pct,
            "volatility_type": volatility_type,
            "thinking_process": f"""
## 本地分析过程

### 1. 数据观察
- 基金代码: {fund_code}
- 基金名称: {fund_name}
- 日涨跌幅: {daily_change_pct:+.2f}%
- 波动等级: {volatility_type}

### 2. 持仓贡献分析
""",
            "top_contributor": top_contributor,
            "assessment": assessment,
            "risk_warning": "无明显风险信号" if abs(daily_change_pct) < 1.5 else "建议关注市场风险",
            "recommendation": "继续持有" if daily_change_pct > -1 else "建议评估",
            "tokens_used": 0,
            "estimated_cost": 0.0,
            "is_cached": False,
            "is_mock": True
        }
        
        # 添加持仓贡献详情
        if holdings_contribution:
            analysis["thinking_process"] += "主要贡献股票:\\n"
            for contrib in holdings_contribution[:3]:
                analysis["thinking_process"] += f"- {contrib['stock']}: {contrib['contribution']:+.2f}% 贡献度\\n"
        
        analysis["thinking_process"] += f"""
### 3. 结论
{assessment}

### 4. 建议
{analysis['recommendation']}
"""
        
        # 缓存结果
        cache_analysis(fund_code, "movement_analysis", json.dumps(analysis))
        
        return analysis
    
    def _deepseek_analysis(
        self,
        fund_code: str,
        fund_name: str,
        daily_change_pct: float,
        holdings_contribution: List[Dict],
        news_items: List[Dict]
    ) -> Dict:
        """调用 DeepSeek-R1 进行深度分析"""
        
        # 准备输入数据
        holdings_text = "\\n".join([
            f"- {h['stock']} ({h['code']}): 权重 {h['weight']:.1f}%, 涨跌 {h['change']:+.2f}%, 贡献 {h['contribution']:+.3f}%"
            for h in holdings_contribution[:5]
        ])
        
        news_text = "\\n".join([
            f"- [{n['source']}] {n['title']}: {n['summary'][:100]}"
            for n in news_items[:3]
        ])
        
        prompt = f"""
你是一位资深的基金研究分析师。请对以下基金进行深度分析，展示你的思考过程。

## 基金信息
- 基金代码: {fund_code}
- 基金名称: {fund_name}
- 日涨跌幅: {daily_change_pct:+.2f}%

## 重仓股贡献度
{holdings_text}

## 相关新闻（过去12小时）
{news_text}

## 分析要求
1. 深度分析这个波动是"情绪噪音"还是"基本面反转"
2. 检查是否存在"隐形持仓变动"（估值与持仓走势背离）
3. 给出明确的投资建议

## 输出格式
请按以下格式输出：

### 思考过程
[详细的分析思路]

### 波动性质判断
[情绪噪音/基本面反转/混合信号]

### 持仓变动评估
[是否存在隐形变动，有什么证据]

### 风险提示
[主要风险点]

### 投资建议
[具体建议]
"""
        
        try:
            # 调用 DeepSeek API
            response = self.client.messages.create(
                model="deepseek-reasoner",
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # 提取思考过程和回复
            thinking = ""
            content = ""
            
            for block in response.content:
                if block.type == "thinking":
                    thinking = block.thinking
                elif block.type == "text":
                    content = block.text
            
            # 计算成本
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            input_cost = input_tokens * self.PRICING["input"]
            output_cost = output_tokens * self.PRICING["output"]
            total_cost = input_cost + output_cost
            
            # 记录成本
            log_cost(total_tokens, total_cost, "deepseek_analysis")
            
            # 构建分析结果
            analysis = {
                "fund_code": fund_code,
                "fund_name": fund_name,
                "analysis_time": datetime.now().isoformat(),
                "daily_change_pct": daily_change_pct,
                "thinking_process": thinking,
                "analysis_result": content,
                "tokens_used": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost": round(total_cost, 4),
                "is_cached": False,
                "is_mock": False
            }
            
            # 缓存结果
            cache_analysis(fund_code, "movement_analysis", json.dumps(analysis))
            
            return analysis
            
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            # 降级到本地分析
            return self._local_analysis(
                fund_code, fund_name, daily_change_pct,
                holdings_contribution, news_items
            )
    
    def get_analysis_summary(self, analysis: Dict) -> str:
        """获取分析摘要"""
        if analysis.get("is_mock"):
            return analysis.get("assessment", "分析中...")
        
        # 从 DeepSeek 结果中提取摘要
        result = analysis.get("analysis_result", "")
        lines = result.split("\\n")
        
        # 提取关键信息
        summary_lines = []
        for line in lines:
            if any(keyword in line for keyword in ["建议", "风险", "判断", "评估"]):
                summary_lines.append(line.strip())
        
        return "\\n".join(summary_lines[:3]) if summary_lines else "分析完成"

# 导出单例
analyzer = DeepSeekAnalyzer()
