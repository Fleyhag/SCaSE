from typing import Dict, Any
from ..text_utils import TextOrganizer

def node_start(state: Dict[str, Any]) -> Dict[str, Any]:
    """起始节点：处理输入文件，提取基本信息"""
    file = state['file']
    
    # 检查点：验证文件结构
    if not file or not isinstance(file, dict) or 'sections' not in file:
        return {
            "error": "Invalid file structure",
            "checkpoint": "node_start"
        }
    
    # 提取和组织文本
    cleana, fig_all, table_all = TextOrganizer.extract_and_remove('\n'.join(file['sections'].values()))
    
    # 获取表格数据
    from ..text_utils import get_table
    tables = get_table(table_all, file['tables'])
    
    return {
        "llm":state['llm'],
        "doi": file.get('doi', ''),
        "sections": file.get('sections', {}),
        "cleana": cleana,
        "fig_all": fig_all,
        "tables": tables,
        "checkpoint": "node_start_complete"
    }