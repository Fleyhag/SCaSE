from typing import Dict, Any, List, Optional
from ..llm import LLM

class HallucinationChecker:
    """幻觉检查工具"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
        
    def check_hallucination(self, source_text: str, response: str) -> Dict[str, Any]:
        """
        检查回答中是否存在幻觉
        
        Args:
            source_text: 原始文本
            response: LLM的回答
            
        Returns:
            包含检查结果的字典
        """
        prompt = f"""
        你是一个专业的事实核查员。请仔细阅读以下原始文本和AI助手的回答，检查回答中是否存在"幻觉"（即AI生成的但在原始文本中没有依据的内容）。
        
        原始文本:
        ```
        {source_text}
        ```
        
        AI助手的回答:
        ```
        {response}
        ```
        
        请执行以下检查:
        1. 识别回答中每个元素的关键陈述和关系。
        2. 验证每个陈述是否与原文一致，包括主体和客体的关系是否对应、数量是否一致、顺序是否正确等。
        3. 标记任何有误的元素为"幻觉"
        
        以JSON格式输出你的分析结果:
        {
            "has_hallucination": true/false,
            "hallucinations": [
                {
                    "statement": "有问题的元素",
                    "reason": "为什么这是幻觉的解释"
                }
            ],
            "confidence": 0-100 (你对分析结果的置信度)
        }
        """
        
        result = self.llm.nschat(prompt)
        from ..json_utils import get_json
        
        try:
            analysis = get_json(result)
            if not analysis:
                return {
                    "has_hallucination": True,
                    "hallucinations": [{"statement": "无法解析检查结果", "reason": "工具执行失败"}],
                    "confidence": 0
                }
            return analysis
        except Exception as e:
            return {
                "has_hallucination": True,
                "hallucinations": [{"statement": f"检查过程出错: {str(e)}", "reason": "工具执行失败"}],
                "confidence": 0
            }