#!/usr/bin/env python3
"""
TradingAgents OpenClaw Skill 示例脚本

演示如何在 OpenClaw 中使用 TradingAgents 多智能体交易框架
"""

import sys
from pathlib import Path

# 添加 skill 到路径
skill_path = Path(__file__).parent
sys.path.insert(0, str(skill_path))

from __init__ import TradingAgentsSkill, analyze, quick_analyze, deep_analyze


def example_basic_usage():
    """基础用法示例"""
    print("=" * 60)
    print("示例 1: 基础用法")
    print("=" * 60)
    
    # 创建技能实例
    skill = TradingAgentsSkill()
    
    # 分析股票
    result = skill.analyze_stock("NVDA", "2024-05-10")
    
    print(f"股票代码：{result['ticker']}")
    print(f"分析日期：{result['date']}")
    print(f"操作建议：{result['action']}")
    print(f"置信度：{result['confidence']:.2%}")
    print(f"风险等级：{result['risk_level']}")
    print(f"目标价：${result['target_price']:.2f}")
    print(f"止损价：${result['stop_loss']:.2f}")
    print(f"分析理由：{result['reasoning'][:200]}...")
    print()


def example_quick_analysis():
    """快速分析示例"""
    print("=" * 60)
    print("示例 2: 快速分析（1 轮辩论）")
    print("=" * 60)
    
    result = quick_analyze("AAPL")
    
    print(f"操作建议：{result['action']}")
    print(f"置信度：{result['confidence']:.2%}")
    print(f"理由：{result['reasoning'][:150]}...")
    print()


def example_deep_analysis():
    """深度分析示例"""
    print("=" * 60)
    print("示例 3: 深度分析（3 轮辩论）")
    print("=" * 60)
    
    result = deep_analyze("MSFT", debate_rounds=3)
    
    print(f"操作建议：{result['action']}")
    print(f"置信度：{result['confidence']:.2%}")
    print(f"详细分析:")
    
    details = result.get('analysis_details', {})
    if details.get('fundamental_analysis'):
        print(f"  - 基本面：{str(details['fundamental_analysis'])[:100]}...")
    if details.get('technical_analysis'):
        print(f"  - 技术面：{str(details['technical_analysis'])[:100]}...")
    if details.get('bull_arguments'):
        print(f"  - 多头观点：{len(details['bull_arguments'])} 条")
    if details.get('bear_arguments'):
        print(f"  - 空头观点：{len(details['bear_arguments'])} 条")
    print()


def example_custom_config():
    """自定义配置示例"""
    print("=" * 60)
    print("示例 4: 自定义配置")
    print("=" * 60)
    
    # 自定义配置
    config = {
        "llm_provider": "codex",
        "deep_think_llm": "gpt-5.4",
        "quick_think_llm": "gpt-5.4-mini",
        "max_debate_rounds": 2,
        "data_vendors": {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
        }
    }
    
    skill = TradingAgentsSkill(config=config)
    
    # 获取当前配置
    current_config = skill.get_config()
    print(f"LLM 提供商：{current_config['llm_provider']}")
    print(f"深度思考模型：{current_config['deep_think_llm']}")
    print(f"最大辩论轮数：{current_config['max_debate_rounds']}")
    print()

    skill.set_config("llm_provider", "claude_code")
    current_config = skill.get_config()
    print(f"切换后提供商：{current_config['llm_provider']}")
    print(f"切换后深度模型：{current_config['deep_think_llm']}")
    print(f"切换后快速模型：{current_config['quick_think_llm']}")
    print()


def example_reflect():
    """反思学习示例"""
    print("=" * 60)
    print("示例 5: 反思与学习")
    print("=" * 60)
    
    skill = TradingAgentsSkill()
    
    # 假设上次交易回报率为 15%
    result = skill.reflect_and_remember(0.15)
    
    if result.get('success'):
        print("✓ 学习成功！")
        print(f"结果：{result.get('result')}")
    else:
        print(f"✗ 学习失败：{result.get('error')}")
    print()


def main():
    """运行所有示例"""
    print("\n")
    print("⭐" * 30)
    print("TradingAgents OpenClaw Skill 示例")
    print("⭐" * 30)
    print()
    
    try:
        # 检查是否安装了 TradingAgents
        example_basic_usage()
        example_quick_analysis()
        example_deep_analysis()
        example_custom_config()
        example_reflect()
        
    except ImportError as e:
        print(f"❌ 错误：{e}")
        print("\n请先安装依赖:")
        print(f"  cd {Path(__file__).parent.parent / 'projects' / 'TradingAgents-Official'}")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 运行时错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
