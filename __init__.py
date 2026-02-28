#!/usr/bin/env python3
"""
TradingAgents Skill for OpenClaw
多智能体交易框架集成

Usage:
    from trading_agents import TradingAgentsSkill
    
    skill = TradingAgentsSkill()
    result = skill.analyze_stock("NVDA", "2024-05-10")
    print(result)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

# 添加 TradingAgents 到路径
TRADING_AGENTS_ROOT = Path(__file__).parent.parent.parent / "projects" / "TradingAgents-Official"
sys.path.insert(0, str(TRADING_AGENTS_ROOT))

try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    TRADING_AGENTS_AVAILABLE = True
except ImportError as e:
    TRADING_AGENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TradingAgentsSkill:
    """TradingAgents 多智能体交易技能"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 TradingAgents 技能
        
        Args:
            config: 自定义配置字典，可选
        """
        if not TRADING_AGENTS_AVAILABLE:
            raise ImportError(
                f"TradingAgents 未安装或导入失败：{IMPORT_ERROR}\n"
                f"请运行：pip install -r {TRADING_AGENTS_ROOT}/requirements.txt"
            )
        
        # 使用默认配置或自定义配置
        if config is None:
            self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = {**DEFAULT_CONFIG, **config}
        
        # 设置环境变量（从 .env 文件加载）
        self._load_env()
        
        # 初始化交易图
        self.trading_graph = None
    
    def _load_env(self):
        """从工作区加载 .env 文件"""
        from dotenv import load_dotenv
        
        # 尝试多个位置
        env_paths = [
            Path(__file__).parent.parent.parent / ".env",
            TRADING_AGENTS_ROOT / ".env",
            Path.cwd() / ".env",
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
        else:
            # 如果没有 .env 文件，尝试从系统环境变量加载
            load_dotenv()
    
    def _ensure_initialized(self):
        """确保 trading_graph 已初始化"""
        if self.trading_graph is None:
            self.trading_graph = TradingAgentsGraph(
                debug=True,
                config=self.config
            )
    
    def analyze_stock(
        self,
        ticker: str,
        date: Optional[str] = None,
        max_debate_rounds: Optional[int] = None,
        llm_provider: Optional[str] = None,
        deep_think_llm: Optional[str] = None,
        quick_think_llm: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        分析股票并生成交易决策
        
        Args:
            ticker: 股票代码（如 "NVDA", "AAPL"）
            date: 分析日期（YYYY-MM-DD 格式），默认为最近交易日
            max_debate_rounds: 最大辩论轮数，默认使用配置值
            llm_provider: LLM 提供商（openai/google/anthropic/xai/openrouter/ollama）
            deep_think_llm: 深度思考模型名称
            quick_think_llm: 快速思考模型名称
        
        Returns:
            包含交易决策的字典：
            {
                "ticker": str,
                "date": str,
                "action": str,  # BUY/SELL/HOLD
                "quantity": int,
                "confidence": float,
                "reasoning": str,
                "risk_level": str,
                "target_price": float,
                "stop_loss": float,
                "analysis_details": dict  # 详细分析过程
            }
        """
        # 应用运行时配置覆盖
        if max_debate_rounds is not None:
            self.config["max_debate_rounds"] = max_debate_rounds
        if llm_provider is not None:
            self.config["llm_provider"] = llm_provider
        if deep_think_llm is not None:
            self.config["deep_think_llm"] = deep_think_llm
        if quick_think_llm is not None:
            self.config["quick_think_llm"] = quick_think_llm
        
        # 确保已初始化
        self._ensure_initialized()
        
        # 如果没有提供日期，使用最近日期
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # 执行传播分析
            state, decision = self.trading_graph.propagate(ticker, date)
            
            # 构建结果
            result = {
                "ticker": ticker,
                "date": date,
                "action": decision.get("action", "HOLD"),
                "quantity": decision.get("quantity", 0),
                "confidence": decision.get("confidence", 0.5),
                "reasoning": decision.get("reasoning", ""),
                "risk_level": decision.get("risk_level", "MEDIUM"),
                "target_price": decision.get("target_price", 0),
                "stop_loss": decision.get("stop_loss", 0),
                "analysis_details": {
                    "fundamental_analysis": state.get("fundamental_analysis", {}),
                    "technical_analysis": state.get("technical_analysis", {}),
                    "sentiment_analysis": state.get("sentiment_analysis", {}),
                    "news_analysis": state.get("news_analysis", {}),
                    "bull_arguments": state.get("bull_arguments", []),
                    "bear_arguments": state.get("bear_arguments", []),
                    "risk_assessment": state.get("risk_assessment", {}),
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "ticker": ticker,
                "date": date,
                "action": "ERROR",
            }
    
    def quick_analysis(
        self,
        ticker: str,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        快速分析（减少辩论轮数，使用更快模型）
        
        Args:
            ticker: 股票代码
            date: 分析日期
        
        Returns:
            简化的交易决策
        """
        return self.analyze_stock(
            ticker=ticker,
            date=date,
            max_debate_rounds=1,
            quick_think_llm=self.config.get("quick_think_llm", "gpt-5-mini"),
        )
    
    def deep_analysis(
        self,
        ticker: str,
        date: Optional[str] = None,
        debate_rounds: int = 3,
    ) -> Dict[str, Any]:
        """
        深度分析（增加辩论轮数，使用更强模型）
        
        Args:
            ticker: 股票代码
            date: 分析日期
            debate_rounds: 辩论轮数
        
        Returns:
            详细的交易决策
        """
        return self.analyze_stock(
            ticker=ticker,
            date=date,
            max_debate_rounds=debate_rounds,
            deep_think_llm=self.config.get("deep_think_llm", "gpt-5.2"),
        )
    
    def set_config(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        # 重置 trading_graph 以应用新配置
        self.trading_graph = None
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config.copy()
    
    def reflect_and_remember(self, position_returns: float) -> Dict[str, Any]:
        """
        从历史交易中学习和反思
        
        Args:
            position_returns: 持仓回报率
        
        Returns:
            学习结果
        """
        self._ensure_initialized()
        
        try:
            result = self.trading_graph.reflect_and_remember(position_returns)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# 便捷函数
def analyze(ticker: str, date: str = None, **kwargs) -> Dict[str, Any]:
    """
    快速分析股票的便捷函数
    
    Usage:
        result = analyze("NVDA")
        print(result["action"])
    """
    skill = TradingAgentsSkill()
    return skill.analyze_stock(ticker, date, **kwargs)


def quick_analyze(ticker: str, date: str = None) -> Dict[str, Any]:
    """快速分析便捷函数"""
    skill = TradingAgentsSkill()
    return skill.quick_analysis(ticker, date)


def deep_analyze(ticker: str, date: str = None, debate_rounds: int = 3) -> Dict[str, Any]:
    """深度分析便捷函数"""
    skill = TradingAgentsSkill()
    return skill.deep_analysis(ticker, date, debate_rounds)


# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TradingAgents OpenClaw Skill")
    parser.add_argument("ticker", help="股票代码（如 NVDA, AAPL）")
    parser.add_argument("--date", "-d", help="分析日期（YYYY-MM-DD）", default=None)
    parser.add_argument("--mode", "-m", choices=["quick", "normal", "deep"], default="normal",
                       help="分析模式")
    parser.add_argument("--debate-rounds", "-r", type=int, default=None,
                       help="辩论轮数")
    parser.add_argument("--provider", "-p", help="LLM 提供商", default=None)
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    
    args = parser.parse_args()
    
    # 创建技能实例
    skill = TradingAgentsSkill()
    
    # 根据模式执行分析
    if args.mode == "quick":
        result = skill.quick_analysis(args.ticker, args.date)
    elif args.mode == "deep":
        rounds = args.debate_rounds or 3
        result = skill.deep_analysis(args.ticker, args.date, rounds)
    else:
        kwargs = {}
        if args.debate_rounds:
            kwargs["max_debate_rounds"] = args.debate_rounds
        if args.provider:
            kwargs["llm_provider"] = args.provider
        result = skill.analyze_stock(args.ticker, args.date, **kwargs)
    
    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到：{args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
