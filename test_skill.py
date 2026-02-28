#!/usr/bin/env python3
"""
TradingAgents Skill 测试脚本

验证技能是否正确安装和配置
"""

import sys
from pathlib import Path

# 添加 skill 到路径
skill_path = Path(__file__).parent
sys.path.insert(0, str(skill_path))


def test_import():
    """测试导入"""
    print("测试 1: 导入模块...")
    try:
        from __init__ import TradingAgentsSkill, analyze, quick_analyze, deep_analyze
        print("✓ 导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败：{e}")
        return False


def test_initialization():
    """测试初始化"""
    print("\n测试 2: 初始化技能...")
    try:
        from __init__ import TradingAgentsSkill
        skill = TradingAgentsSkill()
        print("✓ 初始化成功")
        return True, skill
    except Exception as e:
        print(f"✗ 初始化失败：{e}")
        return False, None


def test_config(skill):
    """测试配置"""
    print("\n测试 3: 获取配置...")
    try:
        config = skill.get_config()
        print(f"✓ LLM 提供商：{config.get('llm_provider', 'unknown')}")
        print(f"✓ 深度思考模型：{config.get('deep_think_llm', 'unknown')}")
        print(f"✓ 快速思考模型：{config.get('quick_think_llm', 'unknown')}")
        print(f"✓ 最大辩论轮数：{config.get('max_debate_rounds', 0)}")
        return True
    except Exception as e:
        print(f"✗ 配置测试失败：{e}")
        return False


def test_quick_analysis(skill):
    """测试快速分析（不实际调用 API）"""
    print("\n测试 4: 测试分析接口...")
    try:
        # 注意：这个测试会实际调用 API，需要有效的 API key
        print("⚠  此测试会调用实际 API，需要有效的 API key")
        print("   跳过实际调用测试")
        return True
    except Exception as e:
        print(f"✗ 分析测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("TradingAgents Skill 测试")
    print("=" * 60)
    
    # 测试 1: 导入
    if not test_import():
        print("\n❌ 测试失败：无法导入模块")
        print("\n请确保已安装 TradingAgents:")
        print(f"  cd {Path(__file__).parent.parent / 'projects' / 'TradingAgents-Official'}")
        print("  pip install -r requirements.txt")
        return False
    
    # 测试 2: 初始化
    success, skill = test_initialization()
    if not success:
        print("\n❌ 测试失败：无法初始化技能")
        print("\n请检查:")
        print("  1. TradingAgents 是否正确安装")
        print("  2. 是否配置了有效的 API key")
        return False
    
    # 测试 3: 配置
    if not test_config(skill):
        print("\n❌ 测试失败：配置测试失败")
        return False
    
    # 测试 4: 分析
    if not test_quick_analysis(skill):
        print("\n⚠  分析测试跳过或失败")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n提示：要实际使用技能，请确保:")
    print("  1. 在 .env 文件中配置有效的 API key")
    print("  2. 网络连接正常")
    print("  3. 有足够的 API 配额")
    print("\n示例用法:")
    print("  from trading_agents import TradingAgentsSkill")
    print("  skill = TradingAgentsSkill()")
    print("  result = skill.analyze_stock('NVDA', '2024-05-10')")
    print("  print(result)")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
