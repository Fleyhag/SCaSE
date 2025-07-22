import json
import re
from typing import TypeVar, Any, Optional

T = TypeVar("T")

def _json_interception(s: str, is_json_array: bool = False) -> Optional[str]:
    """截取JSON字符串"""
    if is_json_array:
        i = s.find("[")
        if i < 0:
            return None
        count = 1
        for j, c in enumerate(s[i + 1:], start=i + 1):
            if c == "]":
                count -= 1
            elif c == "[":
                count += 1
            if count == 0:
                break
        if count != 0:
            return None
        return s[i: j + 1]
    else:
        i = s.find("{")
        if i < 0:
            return None
        count = 1
        for j, c in enumerate(s[i + 1:], start=i + 1):
            if c == "}":
                count -= 1
            elif c == "{":
                count += 1
            if count == 0:
                break
        if count != 0:
            return None
        return s[i: j + 1]

def _illegal_json_ends(s: str) -> str:
    """修复非法JSON结尾"""
    temp_json = s
    illegal_json_ends_1 = [", }", ",}"]
    illegal_json_ends_2 = [", ]", ",]"]
    for illegal_json_end in illegal_json_ends_1:
        temp_json = temp_json.replace(illegal_json_end, " }")
    for illegal_json_end in illegal_json_ends_2:
        temp_json = temp_json.replace(illegal_json_end, " ]")
    return temp_json

def _extract_json(s: str) -> str:
    """提取JSON字符串"""
    temp_json = _json_interception(s, True)
    if not temp_json:
        temp_json = _json_interception(s)
    if not temp_json:
        raise ValueError("Failed to find a valid JSON structure")
    return temp_json

def _json_parse_str(model_out_text: str) -> str:
    """解析模型输出中的JSON字符串"""
    cleaned_output = model_out_text.rstrip()
    
    # 处理Markdown代码块
    if "```json" in cleaned_output:
        _, cleaned_output = cleaned_output.split("```json", 1)

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output[len("```json"):]
    if cleaned_output.startswith("```"):
        cleaned_output = cleaned_output[len("```"):]
    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output[:-len("```")]
        
    cleaned_output = cleaned_output.strip()
    
    # 提取JSON
    if not (cleaned_output.startswith("{") and cleaned_output.endswith("}")) and \
       not (cleaned_output.startswith("[") and cleaned_output.endswith("]")):
        cleaned_output = _extract_json(cleaned_output)
        
    # 清理格式
    cleaned_output = (
        cleaned_output.strip()
        .replace("\n", " ")
        .replace("\\n", " ")
        .replace("\\", " ")
    )
    cleaned_output = _illegal_json_ends(cleaned_output)
    
    return cleaned_output

def _fix_unescaped_quotes(s: str) -> str:
    result = []
    i = 0
    while i < len(s):
        c = s[i]

        if c == '"':
            # 获取前后1~3个字符，去除空格后用于判断
            prev = ''.join(s[max(0, i - 3):i]).replace(' ', '')
            next = ''.join(s[i + 1:i + 4]).replace(' ', '')
            is_structural = False

            # 头尾直接是结构性双引号
            if i == 0 or i == len(s) - 1:
                is_structural = True
            else:
                # 结构性场景一：前是 { 或 [ ，或后是 } 或 ]
                if prev and prev[-1] in '{[':
                    is_structural = True
                elif next and next[0] in '}]':
                    is_structural = True
                # 结构性场景二：例如 ,"key": 或 ,"value",
                elif prev and prev in ['":','",']:
                        is_structural = True
                elif next and next in [':"',',"']:
                        is_structural = True

            # 非结构双引号需转义
            if not is_structural:
                result.append('\\"')
            else:
                result.append(c)
        else:
            result.append(c)

        i += 1

    return ''.join(result)


def get_json(response: str) -> Optional[Any]:
    match = re.search(r"```json(.*?)```", response, re.DOTALL)
    if match:
        extracted_json = match.group(1).strip()
        try:
            json_message = json.loads(extracted_json)
            return json_message
        except json.JSONDecodeError:
            pass
        try:
            json_message = json.loads(extracted_json.replace("\\n", "").replace("\\", "").replace("  ", " "))
            return json_message
        except json.JSONDecodeError:
            pass
        try:
            matches = _json_parse_str(extracted_json)
            matches = _fix_unescaped_quotes(matches)
            json_message = json.loads(matches)
            return json_message
        except Exception:
            pass
    try:
        json_message = json.loads(response)
        return json_message
    except json.JSONDecodeError:
        pass
    try:
        json_message = json.loads(response.replace("\\n", "").replace("\\", "").replace("  ", " "))
        return json_message
    except json.JSONDecodeError:
        pass
    try:
        matches = _json_parse_str(response)
        matches = _fix_unescaped_quotes(matches)
        json_message = json.loads(matches)
        return json_message
    except Exception:
        print("--error parsing json", response)
        return None