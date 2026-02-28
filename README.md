# TradingAgents Skill for OpenClaw

多智能体交易框架集成 - 让 AI 智能体团队帮你分析股票！

## 📦 安装

### 1. 安装 TradingAgents 核心依赖

```bash
cd C:\Users\gaaiy\.openclaw\workspace\projects\TradingAgents-Official
pip install -r requirements.txt
```

### 2. 配置 API Keys

在 `~/.openclaw/workspace/.env` 文件中添加：

```bash
# 选择一个 LLM 提供商
OPENAI_API_KEY=sk-...          # OpenAI (推荐)
# 或
GOOGLE_API_KEY=...             # Google
# 或
ANTHROPIC_API_KEY=...          # Anthropic
# 或
XAI_API_KEY=...                # xAI

# 可选：数据提供商（默认使用 yfinance，无需 API key）
ALPHA_VANTAGE_API_KEY=...
```

## 🚀 快速开始

### 在 Python 中使用

```python
from trading_agents import TradingAgentsSkill

# 创建技能实例
skill = TradingAgentsSkill()

# 分析股票
result = skill.analyze_stock("NVDA", "2024-05-10")

# 查看结果
print(f"操作建议：{result['action']}")
print(f"置信度：{result['confidence']:.2%}")
print(f"理由：{result['reasoning']}")
```

### 使用便捷函数

```python
from trading_agents import analyze, quick_analyze, deep_analyze

# 标准分析
result = analyze("AAPL")

# 快速分析（1 轮辩论）
result = quick_analyze("MSFT")

# 深度分析（3 轮辩论）
result = deep_analyze("TSLA", debate_rounds=3)
```

### 命令行使用

```bash
# 标准分析
python skills/trading-agents/__init__.py NVDA

# 快速分析
python skills/trading-agents/__init__.py AAPL --mode quick

# 深度分析
python skills/trading-agents/__init__.py MSFT --mode deep --debate-rounds 3

# 指定日期
python skills/trading-agents/__init__.py TSLA --date 2024-05-10

# 保存到文件
python skills/trading-agents/__init__.py NVDA --output result.json
```

## 🎯 功能特性

### 多智能体协作

TradingAgents 模拟真实交易公司的团队决策流程：

- **基本面分析师**：评估公司财务和内在价值
- **情绪分析师**：分析社交媒体和公众情绪
- **新闻分析师**：监控全球新闻和宏观指标
- **技术分析师**：使用 MACD、RSI 等技术指标
- **多头研究员**：寻找上涨机会
- **空头研究员**：识别潜在风险
- **交易员**：综合报告，做出交易决策
- **风险管理**：评估市场波动性和流动性
- **投资组合经理**：最终审批交易

### 支持的 LLM 提供商

- ✅ OpenAI (GPT-5.x, GPT-4.x)
- ✅ Google (Gemini 3.x, 2.x)
- ✅ Anthropic (Claude 4.x, 3.x)
- ✅ xAI (Grok 4.x)
- ✅ OpenRouter
- ✅ Ollama (本地模型)

### 数据源

- **yfinance**（默认，无需 API key）
- **Alpha Vantage**（需要 API key）

## 📊 输出示例

```json
{
  "ticker": "NVDA",
  "date": "2024-05-10",
  "action": "BUY",
  "quantity": 100,
  "confidence": 0.75,
  "reasoning": "基本面强劲，AI 需求增长，技术面突破...",
  "risk_level": "MEDIUM",
  "target_price": 950.00,
  "stop_loss": 800.00,
  "analysis_details": {
    "fundamental_analysis": {...},
    "technical_analysis": {...},
    "sentiment_analysis": {...},
    "news_analysis": {...},
    "bull_arguments": [...],
    "bear_arguments": [...],
    "risk_assessment": {...}
  }
}
```

## ⚙️ 高级配置

### 自定义 LLM 配置

```python
config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",      # 复杂推理模型
    "quick_think_llm": "gpt-5-mini",  # 快速任务模型
    "max_debate_rounds": 2,           # 辩论轮数
}

skill = TradingAgentsSkill(config=config)
```

### 自定义数据源

```python
config = {
    "data_vendors": {
        "core_stock_apis": "alpha_vantage",
        "technical_indicators": "alpha_vantage",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    }
}

skill = TradingAgentsSkill(config=config)
```

### 运行时配置

```python
skill = TradingAgentsSkill()

# 修改配置
skill.set_config("max_debate_rounds", 3)
skill.set_config("llm_provider", "anthropic")

# 获取当前配置
current = skill.get_config()
```

## 🧠 学习与反思

TradingAgents 可以从历史交易中学习：

```python
skill = TradingAgentsSkill()

# 反思上次交易（假设回报率为 15%）
result = skill.reflect_and_remember(0.15)

if result['success']:
    print("学习成功！")
```

## 📁 文件结构

```
skills/trading-agents/
├── SKILL.md              # OpenClaw 技能描述
├── __init__.py           # 主代码（技能实现）
├── requirements.txt      # Python 依赖
├── README.md             # 本文件
├── example_usage.py      # 使用示例
└── test_skill.py         # 测试脚本
```

## 🧪 测试

运行测试脚本：

```bash
python skills/trading-agents/example_usage.py
```

## ⚠️ 重要声明

**TradingAgents 仅供研究使用！**

- ❌ 不构成投资建议
- ❌ 不保证交易表现
- ❌ 请勿用于真实交易决策
- ⚠️ 交易表现受多种因素影响（模型、温度、数据质量等）
- ⚠️ 使用本框架进行实盘交易的风险由用户自行承担

## 📚 参考资料

- **论文**: [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138)
- **GitHub**: https://github.com/TauricResearch/TradingAgents
- **Discord**: https://discord.com/invite/hk9PGKShPK
- **技术报告**: [Trading-R1](https://arxiv.org/abs/2509.11420)

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

遵循 TradingAgents-Official 项目的许可证。
