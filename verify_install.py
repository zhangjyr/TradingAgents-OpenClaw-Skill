#!/usr/bin/env python3
"""验证 TradingAgents Skill 安装"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TradingAgents Skill 安装验证")
print("=" * 60)

# 测试 1: 导入
print("\n[1/4] 测试导入...")
try:
    from __init__ import TradingAgentsSkill, analyze, quick_analyze, deep_analyze
    print("    [OK] 导入成功")
except ImportError as e:
    print(f"    [FAIL] 导入失败：{e}")
    print("\n    请安装 TradingAgents:")
    print("    cd projects/TradingAgents-Official")
    print("    pip install -r requirements.txt")
    sys.exit(1)

# 测试 2: 初始化
print("\n[2/4] 测试初始化...")
try:
    skill = TradingAgentsSkill()
    print("    [OK] 初始化成功")
except Exception as e:
    print(f"    [FAIL] 初始化失败：{e}")
    print("\n    可能原因:")
    print("    1. TradingAgents 未正确安装")
    print("    2. 缺少依赖包")
    print("    3. 环境变量未配置")
    sys.exit(1)

# 测试 3: 配置
print("\n[3/4] 测试配置加载...")
try:
    config = skill.get_config()
    llm_provider = config.get('llm_provider', 'unknown')
    deep_model = config.get('deep_think_llm', 'unknown')
    quick_model = config.get('quick_think_llm', 'unknown')
    output_language = config.get('output_language', 'unknown')
    print(f"    [OK] LLM 提供商：{llm_provider}")
    print(f"    [OK] 深度思考模型：{deep_model}")
    print(f"    [OK] 快速思考模型：{quick_model}")
    print(f"    [OK] 输出语言：{output_language}")
except Exception as e:
    print(f"    [FAIL] 配置加载失败：{e}")
    sys.exit(1)

print("\n[3.5/4] 测试 Codex / Claude Code 切换...")
try:
    skill.set_config("llm_provider", "codex")
    codex_config = skill.get_config()
    print(f"    [OK] Codex 深度模型：{codex_config.get('deep_think_llm', 'unknown')}")
    print(f"    [OK] Codex 快速模型：{codex_config.get('quick_think_llm', 'unknown')}")

    skill.set_config("llm_provider", "claude_code")
    claude_config = skill.get_config()
    print(f"    [OK] Claude Code 深度模型：{claude_config.get('deep_think_llm', 'unknown')}")
    print(f"    [OK] Claude Code 快速模型：{claude_config.get('quick_think_llm', 'unknown')}")
except Exception as e:
    print(f"    [FAIL] 提供商切换失败：{e}")
    sys.exit(1)

print("\n[3.6/4] 测试中文输出配置...")
try:
    skill.set_config("output_language", "中文")
    language_config = skill.get_config()
    print(f"    [OK] 输出语言：{language_config.get('output_language', 'unknown')}")
except Exception as e:
    print(f"    [FAIL] 输出语言配置失败：{e}")
    sys.exit(1)

# 测试 4: 接口可用性
print("\n[4/4] 测试 API 接口...")
try:
    # 检查方法是否存在
    assert hasattr(skill, 'analyze_stock'), "缺少 analyze_stock 方法"
    assert hasattr(skill, 'quick_analysis'), "缺少 quick_analysis 方法"
    assert hasattr(skill, 'deep_analysis'), "缺少 deep_analysis 方法"
    assert hasattr(skill, 'set_config'), "缺少 set_config 方法"
    assert hasattr(skill, 'get_config'), "缺少 get_config 方法"
    print("    [OK] 所有 API 接口可用")
except Exception as e:
    print(f"    [FAIL] API 测试失败：{e}")
    sys.exit(1)

# 完成
print("\n" + "=" * 60)
print("[SUCCESS] 所有验证通过！TradingAgents Skill 已就绪")
print("=" * 60)
print("\n使用方法:")
print("  from skills.trading_agents import TradingAgentsSkill")
print("  skill = TradingAgentsSkill()")
print("  result = skill.analyze_stock('NVDA', '2024-05-10')")
print("  print(result)")
print("\n注意：实际分析需要配置有效的 LLM 凭证")
print("OpenAI / Google / Anthropic 可走环境变量；Codex / Claude Code 需要本地登录态")
