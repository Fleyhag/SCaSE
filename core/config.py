import os
import yaml

def load_config(config_path=None):
    if config_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(current_dir, "config.yaml")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()
llm_config = config.get("llm_config", {})