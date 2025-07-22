import re
import json
from typing import Dict, Tuple, List, Any

class TextOrganizer:
    """文本组织工具类"""
    
    @staticmethod
    def extract_and_remove(input_text: str) -> Tuple[str, str, str]:
        """提取并移除图表标注"""
        fig_pattern = r'\{\{[^}]*?Fig[^}]*?\}\}'
        tbl_pattern = r'\{\{[^}]*?\$div#\S+?[^}]*?\}\}'
        
        # 初始化空字典来存储提取出来的图注和表头
        extracted_figures = {}
        extracted_tables = {}
        
        def process_matches(pattern, item_type, text, storage):
            matches = re.findall(pattern, text)
            for match in matches:
                # 提取标题，移除$figure#或$div#及其后面的文本
                title = re.search(r'^[^$]+', match).group(0).strip().rstrip(':').strip()[2:]
                title = re.sub(r'^Fig\.\s*\d+[a-z]?\.\s*', '', title)
                key_name = f"{item_type}_{len(storage) + 1}"
                storage[key_name] = title
            # 使用re.sub移除匹配项，并替换为空字符串
            return re.sub(pattern, '', text)

        # 一定要先处理图注
        input_text = process_matches(fig_pattern, 'figure', input_text, extracted_figures)
        # 处理表头
        cleaned_text = process_matches(tbl_pattern, 'table', input_text, extracted_tables)
        
        # 将提取出的项目转为JSON格式的字符串
        extracted_figure_json = json.dumps(extracted_figures, ensure_ascii=False, indent=4)
        extracted_table_json = json.dumps(extracted_tables, ensure_ascii=False, indent=4)
        
        return cleaned_text, extracted_figure_json, extracted_table_json

    @staticmethod
    def replace_sections(response_text_1: Dict[str, List[str]], sections: Dict[str, str]) -> Dict[str, str]:
        """替换章节引用为实际内容"""
        # 创建一个新的字典来存储结果
        formatted_response = {}

        for key, section_list in response_text_1.items():
            # 对于每个键，初始化一个空字符串用于累积内容
            content = ""
            
            for section_key in section_list:
                # 尝试从 sections 中获取内容并添加到累积字符串中
                if section_key in sections:
                    if content:  # 如果已经有内容，则在新内容前添加换行符
                        content += "\n"
                    content += sections[section_key]
            
            # 将累积的内容存入新的字典中
            formatted_response[key] = content

        return formatted_response

    @staticmethod
    def clean_formatted_response(response: Dict[str, str]) -> Dict[str, str]:
        """清理格式化响应"""
        cleaned_response = {}
        for key, content in response.items():
            cleaned_text, _, _ = TextOrganizer.extract_and_remove(content)
            cleaned_response[key] = cleaned_text
        return cleaned_response

def get_table(ta: str, tables: Dict[str, str]) -> str:
    """获取表格数据"""
    try:
        ta_dict = json.loads(ta)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        ta_dict = {}

    combined_tables = {}
    for key in tables.keys():
        if key in ta_dict:
            combined_tables[key] = {
                'title': ta_dict[key],
                'content': tables[key]
            }
        else:
            combined_tables[key] = {
                'title': 'unknown',
                'content': tables[key]
            }
    return json.dumps(combined_tables, ensure_ascii=False, indent=4)