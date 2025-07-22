from typing import Dict, Any
from ..logger_context import get_logger

def node_pretreatment(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_pretreatment"}

    from prompt import prompt_test as pt
    
    try:
        paper_text=state["paper_text"]
        # 提取论文文本结构
        is_PBF=llm.nschat(pt.pt_pbf.format(method=paper_text["method"])),
        classified_figs=llm.schat(pt.pt_figs.format(
            fa=state["fig_all"], 
            paper_text=paper_text['method'] + "\n" + paper_text['result']
            ))
        
        logger.info(f"Pretreatment node completed.")
        logger.info(f"is_PBF: {is_PBF}")
        logger.info(f"classified_figs: {classified_figs}")

        return {
            **state,
            "is_PBF": is_PBF,
            "classified_figs": classified_figs,
            "checkpoint": "node_pretreatment_complete"
        }
    except Exception as e:
        logger.error(f"Error in pretreatment node: {e}")
        return {
            **state,
            "error": f"pretreatment node failed: {str(e)}",
            "checkpoint": "node_pretreatment_error"
        }