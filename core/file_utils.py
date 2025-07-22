import os
import json

def getfile(fp):
    """读取文件或目录，提取论文数据"""
    if not os.path.isdir(fp):
        return None
        
    filename = fp.replace('\\', '/').rsplit('/')[-1]  # 获取目录名作为文件名
    # 构建JSON文件的路径并尝试打开
    json_path = os.path.join(fp, f"{filename}.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            ref = data.get('ref', '')
            doi = data.get('doi', '')
            title = data.get('title', '')
            figs = str(data.get('image_list', []))
    except Exception as e:
        print(f"Error loading JSON from {filename}: {e}")
        return None
        
    # 构建并读取section_i.txt文件
    sections = {}
    for section_file in os.listdir(fp):
        if section_file.startswith('section_') and section_file.endswith('.txt'):
            section_key = section_file.replace('.txt', '')
            with open(os.path.join(fp, section_file), 'r', encoding='utf-8') as f:
                sections[section_key] = f.read()
                
    # 构建并读取table_i.txt文件
    tables = {}
    for table_file in os.listdir(fp):
        if table_file.startswith('table_') and table_file.endswith('.txt'):
            table_num = table_file.replace('.txt', '')
            with open(os.path.join(fp, table_file), 'r', encoding='utf-8') as f:
                tables[table_num] = f.read()
                
    file = {
        'ref': ref,
        'doi': doi,
        'title': title,
        'sections': sections,
        'tables': tables,
        'figs': figs
    }
    return file

def save_to_json(data, output_path):
    """保存数据到JSON文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)