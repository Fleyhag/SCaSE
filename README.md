# SCaSE
Material Data Extraction from Scientific Literature
This project is based on the paper, DOI: [doi].

It is specifically designed to extract sample-level material data from materials science literature, with a focus on alloy materials.

🔍 Project Overview
This repository provides a customized pipeline for extracting structured material data directly from scientific publications. The extracted data can be used for downstream tasks such as materials informatics, machine learning, and database construction.

📁 Directory Structure
data/100_labeled_Papers.zip  439 samples from 100 labeled alloy papers
data/example_literature/     Example input: full-text HTML from a ScienceDirect paper
web_extractor/               Chrome extension for downloading full-text HTML
config.yaml                  Configuration file for model and API key
prompt.py                    prompts used in SCaSE
run.py                       Main script to run the extraction pipeline


⚙️ Setup & Usage
1. Prerequisites
Python 3.9+
openai and langgraph libraries
Install dependencies using:

pip install -r requirements.txt

2. Configure API and Model Settings
Edit the config.yaml file to specify:

The LLM model you want to use
Your OpenAI API key
3. Run the Pipeline
To extract data from literature:

bash
深色版本
python run.py
The extracted data will be saved in data/output/ in JSON format.

📤 Input Format
The input should be the full-text HTML of a paper from ScienceDirect. You can use the provided Chrome extension in the web_extractor/ folder to download papers in the correct format.

How to Use the Chrome Extension
Open the paper on ScienceDirect.
Click the extension icon in the Chrome toolbar.
Click "Download Full Text".
The HTML file will be saved in the same format as the example in data/example_literature/.
📝 Citation
If you find this project useful in your research, please cite the original paper:

【doi】

✅ Notes
The pipeline is tailored for alloy materials, but can be adapted for other material classes with appropriate prompt engineering.
Empty folders are tracked using .gitkeep files.
