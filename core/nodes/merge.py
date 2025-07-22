from typing import Dict, Any
from ..logger_context import get_logger

def node_merge(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_merge"}

    from prompt import prompt_test as pt
    
    try:
        doi=state['doi']
        samples=llm.schat(pt.pt_merge_msu.format(
            file_name=doi, 
            msu1=state["msu1"],
            msu2=state["msu2"],
            msu3=state["msu3"]))
        
        logger.info(f"merge node completed.")
        logger.info(f"samples: {samples}")

        
        # 幻觉检查
        
        return {
            **state,
            "samples": samples,
            "checkpoint": "node_merge_complete"
        }
    
    except Exception as e:
        logger.error(f"Error in merge node: {e}")
        return {
            **state,
            "error": f"merge node failed: {str(e)}",
            "checkpoint": "node_merge_error"
        }