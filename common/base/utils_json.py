import os
import json
def load_json_file(filepath):
    """加载JSON文件并返回其内容"""
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def merge_data(base_data, override_data):
    """根据override_data覆盖base_data中的数据"""
    for key, value in override_data.items():
        if key == "step" and isinstance(value, list):
            # 如果有'step'键，特别处理
            step_mapping = {item['step']: item for item in base_data['step']}
            for step_item in value:
                step_id = step_item['step']
                if step_id in step_mapping:
                    step_mapping[step_id] = merge_data(step_mapping[step_id], step_item)
                else:
                    base_data['step'].append(step_item)
        elif isinstance(value, dict):
            if key in base_data and isinstance(base_data[key], dict):
                base_data[key] = merge_data(base_data[key], value)
            else:
                base_data[key] = value
        else:
            base_data[key] = value
    return base_data


def load_and_process_json(filepath, override_data={}):
    file_data = load_json_file(filepath)
    file_data = merge_data(file_data, override_data)

    for key, value in file_data.items():
        if isinstance(value, list):
            for idx, step_item in enumerate(value):
                for sub_key, sub_value in step_item.items():
                    if os.path.isfile(sub_key):
                        loaded_data = load_and_process_json(sub_key, sub_value)
                        file_data[key][idx][sub_key] = loaded_data
        elif isinstance(value, dict):  # 如果value是一个dict
            for sub_key, sub_value in value.items():
                if os.path.isfile(sub_key):  # 如果sub_key是一个文件路径
                    loaded_data = load_and_process_json(sub_key, sub_value)
                    file_data[key][sub_key] = loaded_data

    return file_data

def process_test_case(testcase_path):
    testcase_data = load_json_file(testcase_path)
    result_data = []

    for step in testcase_data["step"]:
        processed_step = {}
        for key, value in step.items():
            if key != "step" and os.path.isfile(key):
                file_data = load_and_process_json(key, value)
                processed_step[key] = file_data
            else:
                processed_step[key] = value
        result_data.append(processed_step)
    #print(result_data)
    return result_data






