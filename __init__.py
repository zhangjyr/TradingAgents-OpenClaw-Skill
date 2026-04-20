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

import json
import os
import shlex
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

def _resolve_trading_agents_root() -> Path:
    skill_dir = Path(__file__).resolve().parent
    candidate_roots = []

    env_root = os.getenv("TRADING_AGENTS_ROOT")
    if env_root:
        candidate_roots.append(Path(env_root).expanduser())

    candidate_roots.extend(
        [
            skill_dir.parent / "TradingAgents",
            skill_dir.parent / "TradingAgents-Official",
            skill_dir.parent.parent / "projects" / "TradingAgents-Official",
            skill_dir.parent.parent / "projects" / "TradingAgents",
            Path.cwd(),
        ]
    )

    for candidate in candidate_roots:
        if (candidate / "tradingagents" / "__init__.py").exists():
            return candidate

    return candidate_roots[0]


TRADING_AGENTS_ROOT = _resolve_trading_agents_root()
sys.path.insert(0, str(TRADING_AGENTS_ROOT))

try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    try:
        from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS
    except ImportError:
        MODEL_OPTIONS = {}
    TRADING_AGENTS_AVAILABLE = True
except ImportError as e:
    TRADING_AGENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


FALLBACK_PROVIDER_MODELS = {
    "openai": {
        "deep": "gpt-5.4",
        "quick": "gpt-5.4-mini",
    },
    "codex": {
        "deep": "gpt-5.4",
        "quick": "gpt-5.4-mini",
    },
    "claude_code": {
        "deep": "claude-opus-4-6",
        "quick": "claude-sonnet-4-6",
    },
}


def _resolve_provider_default_models(provider: Optional[str]) -> Dict[str, str]:
    normalized_provider = (provider or "").lower()
    provider_options = MODEL_OPTIONS.get(normalized_provider, {}) if TRADING_AGENTS_AVAILABLE else {}
    deep_options = provider_options.get("deep", [])
    quick_options = provider_options.get("quick", [])

    deep_model = deep_options[0][1] if deep_options else None
    quick_model = quick_options[0][1] if quick_options else None
    fallback = FALLBACK_PROVIDER_MODELS.get(normalized_provider, FALLBACK_PROVIDER_MODELS["openai"])

    return {
        "deep": deep_model or fallback["deep"],
        "quick": quick_model or fallback["quick"],
    }


def _with_invoked_skill(result: Dict[str, Any], invoked_skill: str) -> Dict[str, Any]:
    merged = dict(result)
    merged["invoked_skill"] = invoked_skill
    return merged


def _build_command_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description="TradingAgents OpenClaw Skill",
        exit_on_error=False,
    )
    parser.add_argument("ticker", help="股票代码（如 NVDA, AAPL）")
    parser.add_argument("--date", "-d", help="分析日期（YYYY-MM-DD）", default=None)
    parser.add_argument("--mode", "-m", choices=["quick", "normal", "deep"], default="normal", help="分析模式")
    parser.add_argument("--debate-rounds", "-r", type=int, default=None, help="辩论轮数")
    parser.add_argument("--provider", "-p", help="LLM 提供商", default="codex")
    parser.add_argument("--language", "-l", help="输出语言", default="中文")
    parser.add_argument("--debug", action="store_true", help="输出底层调试信息")
    parser.add_argument("--output", "-o", help="输出文件路径", default=None)
    return parser


def handle_trading_agents_command(
    command_args: str,
    *,
    debug: bool = False,
    invoked_skill: str = "trading-agents",
) -> Dict[str, Any]:
    parser = _build_command_parser()
    try:
        args = parser.parse_args(shlex.split(command_args))
    except Exception as error:
        return _with_invoked_skill(
            {
                "error": str(error),
                "action": "ERROR",
            },
            invoked_skill,
        )

    initial_config = {"output_language": args.language}
    if args.provider:
        initial_config["llm_provider"] = args.provider
    skill = TradingAgentsSkill(config=initial_config, debug=args.debug or debug)

    if args.mode == "quick":
        result = skill.quick_analysis(
            args.ticker,
            args.date,
            language=args.language,
            debug=args.debug or debug,
        )
    elif args.mode == "deep":
        rounds = args.debate_rounds or 3
        result = skill.deep_analysis(
            args.ticker,
            args.date,
            rounds,
            language=args.language,
            debug=args.debug or debug,
        )
    else:
        kwargs = {}
        if args.debate_rounds:
            kwargs["max_debate_rounds"] = args.debate_rounds
        kwargs["language"] = args.language
        kwargs["debug"] = args.debug or debug
        result = skill.analyze_stock(args.ticker, args.date, **kwargs)

    return _with_invoked_skill(result, invoked_skill)


class TradingAgentsSkill:
    """TradingAgents 多智能体交易技能"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, debug: bool = False):
        """
        初始化 TradingAgents 技能
        
        Args:
            config: 自定义配置字典，可选
            debug: 是否启用底层 LangGraph 调试输出
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
        # self.config["codex_reuse_thread"] = True
        self._apply_provider_model_defaults(explicit_keys=set(config.keys()) if config else set())
        
        # 设置环境变量（从 .env 文件加载）
        self._load_env()
        
        # 初始化交易图
        self.debug = debug
        self.trading_graph = None
    
    def _load_env(self):
        """从工作区加载 .env 文件"""
        from dotenv import load_dotenv
        
        # 尝试多个位置
        env_paths = [
            Path(__file__).resolve().parent.parent / ".env",
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
                debug=self.debug,
                config=self.config
            )

    def _normalize_decision(self, state: Dict[str, Any], decision: Any) -> Dict[str, Any]:
        if isinstance(decision, dict):
            return {
                "action": decision.get("action", "HOLD"),
                "quantity": decision.get("quantity", 0),
                "confidence": decision.get("confidence", 0.5),
                "reasoning": decision.get("reasoning", ""),
                "risk_level": decision.get("risk_level", "MEDIUM"),
                "target_price": decision.get("target_price", 0),
                "stop_loss": decision.get("stop_loss", 0),
            }

        if isinstance(decision, str):
            normalized_action = decision.strip().upper() or "HOLD"
            full_reasoning = state.get("final_trade_decision", "")
            if not isinstance(full_reasoning, str):
                full_reasoning = str(full_reasoning)
            return {
                "action": normalized_action,
                "quantity": 0,
                "confidence": 0.5,
                "reasoning": full_reasoning,
                "risk_level": "MEDIUM",
                "target_price": 0,
                "stop_loss": 0,
            }

        return {
            "action": "HOLD",
            "quantity": 0,
            "confidence": 0.5,
            "reasoning": str(decision),
            "risk_level": "MEDIUM",
            "target_price": 0,
            "stop_loss": 0,
        }

    def _apply_provider_model_defaults(
        self,
        explicit_keys: Optional[set[str]] = None,
        previous_provider: Optional[str] = None,
    ):
        explicit_keys = explicit_keys or set()
        current_provider = self.config.get("llm_provider", DEFAULT_CONFIG.get("llm_provider"))
        current_defaults = _resolve_provider_default_models(current_provider)
        previous_defaults = _resolve_provider_default_models(previous_provider)

        if (
            "deep_think_llm" not in explicit_keys
            and (
                previous_provider is None
                or self.config.get("deep_think_llm") == previous_defaults["deep"]
                or self.config.get("deep_think_llm") == DEFAULT_CONFIG.get("deep_think_llm")
            )
        ):
            self.config["deep_think_llm"] = current_defaults["deep"]

        if (
            "quick_think_llm" not in explicit_keys
            and (
                previous_provider is None
                or self.config.get("quick_think_llm") == previous_defaults["quick"]
                or self.config.get("quick_think_llm") == DEFAULT_CONFIG.get("quick_think_llm")
            )
        ):
            self.config["quick_think_llm"] = current_defaults["quick"]
    
    def analyze_stock(
        self,
        ticker: str,
        date: Optional[str] = None,
        max_debate_rounds: Optional[int] = None,
        llm_provider: Optional[str] = None,
        deep_think_llm: Optional[str] = None,
        quick_think_llm: Optional[str] = None,
        language: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        分析股票并生成交易决策
        
        Args:
            ticker: 股票代码（如 "NVDA", "AAPL"）
            date: 分析日期（YYYY-MM-DD 格式），默认为最近交易日
            max_debate_rounds: 最大辩论轮数，默认使用配置值
            llm_provider: LLM 提供商（openai/codex/claude_code/google/anthropic/xai/openrouter/ollama）
            deep_think_llm: 深度思考模型名称
            quick_think_llm: 快速思考模型名称
            language: 输出语言，例如 "中文" 或 "English"
            debug: 是否输出底层调试信息
        
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
            previous_provider = self.config.get("llm_provider")
            self.config["llm_provider"] = llm_provider
            self._apply_provider_model_defaults(
                explicit_keys={"deep_think_llm", "quick_think_llm"}
                if deep_think_llm is not None and quick_think_llm is not None
                else {"deep_think_llm"}
                if deep_think_llm is not None
                else {"quick_think_llm"}
                if quick_think_llm is not None
                else set(),
                previous_provider=previous_provider,
            )
        if deep_think_llm is not None:
            self.config["deep_think_llm"] = deep_think_llm
        if quick_think_llm is not None:
            self.config["quick_think_llm"] = quick_think_llm
        if language is not None:
            self.config["output_language"] = language
        if debug is not None and debug != self.debug:
            self.debug = debug
            self.trading_graph = None
        
        # 确保已初始化
        self._ensure_initialized()
        
        # 如果没有提供日期，使用最近日期
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # 执行传播分析
            state, decision = self.trading_graph.propagate(ticker, date)
            normalized_decision = self._normalize_decision(state, decision)
            
            # 构建结果
            result = {
                "ticker": ticker,
                "date": date,
                "action": normalized_decision["action"],
                "quantity": normalized_decision["quantity"],
                "confidence": normalized_decision["confidence"],
                "reasoning": normalized_decision["reasoning"],
                "risk_level": normalized_decision["risk_level"],
                "target_price": normalized_decision["target_price"],
                "stop_loss": normalized_decision["stop_loss"],
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
        language: Optional[str] = None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        快速分析（减少辩论轮数，使用更快模型）
        
        Args:
            ticker: 股票代码
            date: 分析日期
            language: 输出语言
            debug: 是否输出底层调试信息
        
        Returns:
            简化的交易决策
        """
        return self.analyze_stock(
            ticker=ticker,
            date=date,
            max_debate_rounds=1,
            quick_think_llm=self.config.get(
                "quick_think_llm",
                _resolve_provider_default_models(self.config.get("llm_provider"))["quick"],
            ),
            language=language,
            debug=debug,
        )
    
    def deep_analysis(
        self,
        ticker: str,
        date: Optional[str] = None,
        debate_rounds: int = 3,
        language: Optional[str] = None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        深度分析（增加辩论轮数，使用更强模型）
        
        Args:
            ticker: 股票代码
            date: 分析日期
            debate_rounds: 辩论轮数
            language: 输出语言
            debug: 是否输出底层调试信息
        
        Returns:
            详细的交易决策
        """
        return self.analyze_stock(
            ticker=ticker,
            date=date,
            max_debate_rounds=debate_rounds,
            deep_think_llm=self.config.get(
                "deep_think_llm",
                _resolve_provider_default_models(self.config.get("llm_provider"))["deep"],
            ),
            language=language,
            debug=debug,
        )
    
    def set_config(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        previous_provider = self.config.get("llm_provider")
        self.config[key] = value
        if key == "llm_provider":
            self._apply_provider_model_defaults(previous_provider=previous_provider)
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
def analyze(
    ticker: str,
    date: str = None,
    language: str = "中文",
    debug: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    快速分析股票的便捷函数
    
    Usage:
        result = analyze("NVDA")
        print(result["action"])
    """
    skill = TradingAgentsSkill(debug=debug)
    kwargs.setdefault("language", language)
    kwargs.setdefault("debug", debug)
    return skill.analyze_stock(ticker, date, **kwargs)


def quick_analyze(
    ticker: str,
    date: str = None,
    language: str = "中文",
    debug: bool = False,
) -> Dict[str, Any]:
    """快速分析便捷函数"""
    skill = TradingAgentsSkill(debug=debug)
    return skill.quick_analysis(ticker, date, language=language, debug=debug)


def deep_analyze(
    ticker: str,
    date: str = None,
    debate_rounds: int = 3,
    language: str = "中文",
    debug: bool = False,
) -> Dict[str, Any]:
    """深度分析便捷函数"""
    skill = TradingAgentsSkill(debug=debug)
    return skill.deep_analysis(ticker, date, debate_rounds, language=language, debug=debug)


# CLI 入口
if __name__ == "__main__":
    parser = _build_command_parser()
    args = parser.parse_args()
    command_tokens = [args.ticker]
    if args.date:
        command_tokens.extend(["--date", args.date])
    if args.mode:
        command_tokens.extend(["--mode", args.mode])
    if args.debate_rounds is not None:
        command_tokens.extend(["--debate-rounds", str(args.debate_rounds)])
    if args.provider:
        command_tokens.extend(["--provider", args.provider])
    if args.language:
        command_tokens.extend(["--language", args.language])
    if args.debug:
        command_tokens.append("--debug")

    result = handle_trading_agents_command(" ".join(shlex.quote(token) for token in command_tokens))
    
    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到：{args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
