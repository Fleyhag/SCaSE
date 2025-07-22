from typing import Dict, Any
from ..logger_context import get_logger

def node_msu(state: Dict[str, Any]) -> Dict[str, Any]:
    """论文信息节点：提取论文的结构化信息"""
    logger = get_logger()
    # 获取LLM客户端
    llm = state.get('llm')
    if not llm:
        return {"doi": state["doi"], "error": "LLM client not found", "checkpoint": "node_msu"}

    from prompt import prompt_test as pt
    
    try:
        paper_text=state['paper_text']
        tables=state['tables']
        classified_figs=state['classified_figs']
        raw_conditions_json=state['raw_conditions_json']
        raw_compositions=state['raw_compositions']
        msu1=llm.schat(pt.pt_msu1.format(
            paper_text=paper_text["result"],
            classified_figures=classified_figs,
            tables=str(tables),
            composition=raw_compositions,
            conditions=raw_conditions_json)),
        msu2=llm.schat(pt.pt_msu2.format(
            paper_text=paper_text["result"],
            classified_figures=classified_figs,
            composition=raw_compositions,
            conditions=raw_conditions_json)),
        msu3=llm.schat(pt.pt_msu3.format(
            paper_text=paper_text["result"],
            classified_figures=classified_figs,
            tables=str(tables),
            composition=raw_compositions,
            conditions=raw_conditions_json))
        
        logger.info(f"msu node completed.")
        logger.info(f"msu1: {msu1}")
        logger.info(f"msu2: {msu2}")
        logger.info(f"msu3: {msu3}")

        
        # 幻觉检查
        if 'hallucination_checker' in state:
            hallucination_result = state['hallucination_checker'].check_hallucination(
                paper_text["method"]+"\n"+ paper_text["result"], msu1
            )
            if hallucination_result.get('has_hallucination', False):
                logger.warning(f"Hallucination detected in pretreatment: {hallucination_result}") 
        
        return {
            **state,
            "msu1": msu1,
            "msu2": msu2,
            "msu3": msu3,
            "checkpoint": "node_msu_complete"
        }
    
    except Exception as e:
        logger.error(f"Error in msu node: {e}")
        return {
            **state,
            "error": f"msu node failed: {str(e)}",
            "checkpoint": "node_msu_error"
        }