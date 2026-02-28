# TradingAgents Skill 快速入门指南

## 📦 5 分钟快速开始

### 步骤 1: 安装依赖（2 分钟）

```bash
# 进入 TradingAgents 项目目录
cd C:\Users\gaaiy\.openclaw\workspace\projects\TradingAgents-Official

# 安装所有依赖
pip install -r requirements.txt
```

### 步骤 2: 配置 API Key（1 分钟）

在 `C:\Users\gaaiy\.openclaw\workspace\.env` 文件中添加：

```bash
# 选择一个 LLM 提供商（推荐 OpenAI）
OPENAI_API_KEY=sk-your-api-key-here
```

**获取 API Key:**
- OpenAI: https://platform.openai.com/api-keys
- Google: https://makersuite.google.com/app/apikey
- Anthropic: https://console.anthropic.com/settings/keys

### 步骤 3: 测试运行（2 分钟）

```bash
# 进入工作区
cd C:\Users\gaaiy\.openclaw\workspace

# 运行测试脚本
python skills/trading-agents/test_skill.py
```

如果看到 `✅ 所有测试通过！`，说明安装成功！

## 🚀 开始使用

### 方法 1: Python 代码

```python
from skills.trading_agents import TradingAgentsSkill

# 创建技能
skill = TradingAgentsSkill()

# 分析股票
result = skill.analyze_stock("NVDA", "2024-05-10")

# 打印结果
print(f"建议：{result['action']}")
print(f"置信度：{result['confidence']:.0%}")
print(f"理由：{result['reasoning']}")
```

### 方法 2: 命令行

```bash
# 分析 NVDA
python skills/trading-agents/__init__.py NVDA

# 快速分析 AAPL
python skills/trading-agents/__init__.py AAPL --mode quick

# 深度分析 MSFT（3 轮辩论）
python skills/trading-agents/__init__.py MSFT --mode deep --debate-rounds 3
```

### 方法 3: 在 OpenClaw 中

直接在对话中说：
```
"分析一下 NVDA 股票"
"AAPL 现在能买吗"
"用多智能体分析 MSFT"
```

## 📊 理解输出

典型的分析结果包含：

```json
{
  "action": "BUY",           // 操作建议：BUY/SELL/HOLD
  "quantity": 100,           // 建议数量
  "confidence": 0.75,        // 置信度（0-1）
  "reasoning": "...",        // 分析理由
  "risk_level": "MEDIUM",    // 风险等级
  "target_price": 950.00,    // 目标价
  "stop_loss": 800.00        // 止损价
}
```

## ⚙️ 常见配置

### 更换 LLM 提供商

```python
skill = TradingAgentsSkill()
skill.set_config("llm_provider", "anthropic")  # 或 google, xai
```

### 调整辩论轮数

```python
# 更多辩论 = 更深入分析，但更慢
skill.set_config("max_debate_rounds", 3)
```

### 使用不同的模型

```python
skill.set_config("deep_think_llm", "gpt-5.2")      # 强模型
skill.set_config("quick_think_llm", "gpt-5-mini")  # 快模型
```

## 🐛 常见问题

### Q: 导入错误 "No module named 'tradingagents'"

**A:** 确保已安装 TradingAgents 依赖：
```bash
cd C:\Users\gaaiy\.openclaw\workspace\projects\TradingAgents-Official
pip install -r requirements.txt
```

### Q: API Key 错误

**A:** 检查 `.env` 文件是否存在且 API Key 正确：
```bash
# 在 .env 文件中
OPENAI_API_KEY=sk-...  # 确保没有多余空格
```

### Q: 分析很慢

**A:** 这是正常的！多智能体分析需要：
- 多个智能体协作
- 多轮辩论
- 大量数据获取

**解决方法:**
- 使用 `quick_analyze()` 快速模式
- 减少辩论轮数：`set_config("max_debate_rounds", 1)`
- 使用更快的模型：`set_config("quick_think_llm", "gpt-5-mini")`

### Q: 结果不准确

**A:** TradingAgents 是研究工具，不是投资建议！
- 仅供学习和研究
- 不要用于真实交易
- 结果受多种因素影响（模型、数据、市场条件）

## 📚 下一步

- 阅读完整的 [README.md](README.md)
- 查看 [SKILL.md](SKILL.md) 了解详细功能
- 运行 [example_usage.py](example_usage.py) 看更多示例
- 阅读 [TradingAgents 论文](https://arxiv.org/abs/2412.20138)

## ⚠️ 重要提醒

**TradingAgents 仅供研究使用！**

- ❌ 不构成投资建议
- ❌ 不保证交易表现
- ⚠️ 使用风险自负

祝你使用愉快！🎉
