from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END, START
from .llm import LLM
from .tools.hallucination_check import HallucinationChecker

from .nodes.start import node_start
from .nodes.screen import node_screen
from .nodes.paper_info import node_paperinfo
from .nodes.pretreatment import node_pretreatment
from .nodes.conditions import node_conditions
from .nodes.msu import node_msu
from .nodes.merge import node_merge
from .nodes.formatting import node_formatting


def check_response(state: Dict[str, Any]) -> str:
    if state.get("response") == "TRUE":
        return "continue"
    else:
        return "end"

def create_workflow(llm: Optional[LLM] = None) -> StateGraph:
    """创建工作流图"""
    if not llm:
        llm = LLM()
    
    # 创建幻觉检查工具
    hallucination_checker = HallucinationChecker(llm)
    
    # 创建工作流
    workflow = StateGraph(Dict[str, Any])
    
    # 添加节点
    workflow.add_node("node_start", node_start)
    workflow.add_node("node_screen", node_screen)
    workflow.add_node("node_paperinfo", node_paperinfo)
    workflow.add_node("node_pretreatment", node_pretreatment)
    workflow.add_node("node_conditions", node_conditions)
    workflow.add_node("node_msu", node_msu)
    workflow.add_node("node_merge", node_merge)
    workflow.add_node("node_formatting", node_formatting)
    
    # 添加边
    workflow.add_edge(START, "node_start")
    workflow.add_edge("node_start", "node_screen")
    workflow.add_conditional_edges(
        "node_screen", 
        check_response,
        {"continue": "node_paperinfo", "end": END}
    )
    workflow.add_edge("node_paperinfo", "node_pretreatment")
    workflow.add_edge("node_pretreatment", "node_conditions")
    workflow.add_edge("node_conditions", "node_msu")
    workflow.add_edge("node_msu", "node_merge")
    workflow.add_edge("node_merge", "node_formatting")
    workflow.add_edge("node_formatting", END)
    
    return workflow

def run_workflow(fp):
    from .file_utils import getfile
    try:
        llm = LLM()
        hallucination_checker = HallucinationChecker(llm)
        workflow = create_workflow(llm)
        app = workflow.compile()
        file = getfile(fp)
        if not file:
            return {"error": f"Failed to read file: {fp}"}
        final_state = app.invoke({
            "file": file,
            "llm": llm,
            # "hallucination_checker": hallucination_checker
        })
        return final_state
    except Exception as e:
        return {"error": f"Workflow execution failed: {str(e)}"}