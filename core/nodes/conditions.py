from typing import Dict, Any
from ..json_utils import get_json
from ..logger_context import get_logger

def node_conditions(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_conditions"}

    from prompt import prompt_test as pt
    
    try:
        paper_text=state['paper_text']
        tables=state['tables']
        classified_figs=state['classified_figs']
        is_PBF=state['is_PBF']
        response=llm.schat(pt.pt_conditions.format(
            method=paper_text["method"],
            fa=classified_figs,
            tables=str(tables),
            is_PBF=is_PBF))
        raw_conditions_json=get_json(response)
        del raw_conditions_json["fabrication_process"]
        raw_compositions=llm.schat(pt.pt_composition.format(
            method=paper_text["method"],
            tables=str(tables)
            ))
        
        logger.info(f"conditions node completed.")
        logger.info(f"raw_compositions: {raw_compositions}")
        logger.info(f"raw_condition_json: {raw_conditions_json}")
        
        return {
            **state,
            "raw_conditions_json": raw_conditions_json,
            "raw_compositions": raw_compositions,
            "checkpoint": "node_conditions_complete"
        }
    
    except Exception as e:
        logger.error(f"Error in conditions node: {e}")
        return {
            **state,
            "error": f"conditions node failed: {str(e)}",
            "checkpoint": "node_conditions_error"
        }