from typing import Dict, Any
from ..logger_context import get_logger

def node_formatting(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger= get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_formatting"}

    from prompt import prompt_test as pt
    
    try:
        raw_compositions=state['raw_compositions']
        sample_info=state['samples']
        raw_conditions_json=state['raw_conditions_json']
        is_PBF=state['is_PBF']
        compositions=llm.schat(pt.pt_structure1.format(
            composition=raw_compositions,
            samples=sample_info))
        conditions=llm.schat(pt.pt_structure2.format(
            conditions=raw_conditions_json,
            samples=sample_info,
            is_PBF=is_PBF))
        results=llm.schat(pt.pt_structure3.format(samples=sample_info))
        thermal_process=llm.schat(pt.pt_structure4.format(samples=sample_info))
        
        logger.info(f"formatting node completed.")
        logger.info(f"compositions: {compositions}")
        logger.info(f"conditions: {conditions}")
        logger.info(f"results: {results}")
        logger.info(f"thermal_process: {thermal_process}")
        
        return {
            **state,
            "compositions": compositions,
            "conditions": conditions,
            "results": results,
            "thermal_process": thermal_process,
            "checkpoint": "node_formatting_complete"
        }
    
    except Exception as e:
        logger.error(f"Error in formatting node: {e}")
        return {
            **state,
            "error": f"formatting node failed: {str(e)}",
            "checkpoint": "node_formatting_error"
        }