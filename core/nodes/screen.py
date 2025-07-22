from typing import Dict, Any
from ..logger_context import get_logger

def node_screen(state: Dict[str, Any]) -> Dict[str, Any]:
    """筛选节点：判断文章是否符合处理条件"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_screen"}
    
    from prompt import prompt_test as pt
    
    try:
        response = llm.nschat(pt.pt_screen.format(paper_text=state["cleana"])).strip().upper()
        
        # 检查点：记录筛选结果
        logger.info(f"Screen result: {response}")
        
        return {
            **state,
            "response": response,
            "checkpoint": "node_screen_complete"
        }
    except Exception as e:
        logger.error(f"Error in screen node: {e}")
        return {
            "doi": state["doi"],
            "error": f"Screen node failed: {str(e)}",
            "checkpoint": "node_screen_error"
        }