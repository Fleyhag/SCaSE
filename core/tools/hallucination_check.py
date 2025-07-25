from typing import Dict, Any, List, Optional
from ..llm import LLM

class HallucinationChecker:
    """幻觉检查工具"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
        
    def check_hallucination(self, source_text: str, response: str) -> Dict[str, Any]:
       
        prompt = f"""
        
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
