from langdetect import detect
from webApp.helper import json_tools
import os

def get_language_code_map() -> dict :
    language_detection_map_path = os.path.join("/var","www/aitanmall.com"\
        ,"private","data","language_detection_map.json")
    return json_tools.read_json(language_detection_map_path)

def detect_language(text:str) -> str:
    try:
        language_code_map = get_language_code_map()
        detected_language_code = str(detect(text))
        return language_code_map[detected_language_code]
    except Exception as e:
        return e