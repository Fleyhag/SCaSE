from typing import Dict, Any
from ..text_utils import TextOrganizer
from ..json_utils import get_json
from ..logger_context import get_logger

def node_paperinfo(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_paperinfo"}
    
    # 获取提示词
    from prompt import prompt_test as pt
    
    try:
        # 提取论文文本结构
        response_text = llm.nschat(pt.pt_text.format(paper_text=str(state["sections"])))
        response_text_1 = get_json(response_text)
        
        # 检查点：验证JSON解析结果
        if not response_text_1:
            logger.error("Failed to parse paper structure JSON")
            return {
                "doi": state["doi"],
                "error": "Failed to parse paper structure",
                "checkpoint": "node_paperinfo_json_error"
            }
        
        # 替换章节引用为实际内容
        response_text_2 = TextOrganizer.replace_sections(response_text_1, state["sections"])
        
        # 清理格式化响应
        paper_text = TextOrganizer.clean_formatted_response(response_text_2)
        
        # 处理缩写
        abbr = llm.schat(pt.pt_abbr.format(paper_text=state["cleana"]))
        abbr_json = get_json(abbr)
        
        # 替换缩写
        if abbr_json:
            for key in paper_text:
                if isinstance(paper_text[key], str):
                    text = paper_text[key]
                    for item in abbr_json:
                        abbr = item.get('abbr', '')
                        full = item.get('full', '')
                        if abbr and full:
                            import re
                            pattern = r'\b' + re.escape(abbr) + r'\b'
                            text = re.sub(pattern, full, text)
                    paper_text[key] = text
        
        return {
            **state,
            "paper_text": paper_text,
            "checkpoint": "node_paperinfo_complete"
        }
    except Exception as e:
        logger.error(f"Error in paper info node: {e}")
        return {
            "doi": state["doi"],
            "error": f"Paper info node failed: {str(e)}",
            "checkpoint": "node_paperinfo_error"
        }