import os,json,logging
from core.workflow import run_workflow
from core.json_utils import get_json
from datetime import datetime
from core.config import load_config
from core.logger_context import set_logger

def setup_logger(log_dir, log_name):
    os.makedirs(log_dir, exist_ok=True)
    if log_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f"scase_{timestamp}.log"

    log_path = os.path.join(log_dir, log_name)

    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台日志处理器
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(file_formatter)
    # logger.addHandler(console_handler)

    return logger

        
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.yaml")
    
    config = load_config(config_path)

    paper_dir = config["paper_dir"]
    sample_dir = config["sample_dir"]

    if os.path.exists(paper_dir) and os.path.exists(sample_dir):
        pass
    else:
        paper_dir = os.path.join(current_dir, paper_dir)
        sample_dir = os.path.join(current_dir, sample_dir)

    for doi in os.listdir(paper_dir):
        print("-start extracting from: ",doi)
        fp = os.path.join(paper_dir, doi)
        logger = setup_logger(log_dir=config["log_dir"], log_name=doi+".log")
        logger.info(f"开始处理DOI: {doi}")
        set_logger(logger)

        final_state=run_workflow(fp)

        ref_path= os.path.join(fp, f"{doi}.json")
        with open(ref_path, 'r', encoding='utf-8') as ref_file:
            ref_info = json.load(ref_file)
        samples={}
        for key, value in final_state.items():
            if key in ["compositions", "conditions", "results", "thermal_process"]:

                sample_data = get_json(value)
                if sample_data:
                    for entry in sample_data:
                        sample_id = entry['sample_id']
                        if sample_id not in samples:
                            samples[sample_id] = {
                                'ref': ref_info.get('ref', ''),
                                'doi': ref_info.get('doi', ''),
                                'title': ref_info.get('title', '')
                            }
                        # 更新样品数据
                        samples[sample_id].update(entry)
                else:
                    print(f"invalid JSON {doi}:{key}")
        for sample_id, sample_data in samples.items():
            output_filepath = os.path.join(sample_dir, f"{sample_id}.json")
            with open(output_filepath, 'w', encoding='utf-8') as output_file:
                json.dump(sample_data, output_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()