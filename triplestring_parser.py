import re

def process_string(input_string):
    text_pattern = r'\{(.*?)\}'
    summary_pattern = r'\$\{(.*?)\}'
    
    text_vars = re.findall(text_pattern, input_string)
    summary_vars = re.findall(summary_pattern, input_string)
    
    variables = {}
    index = 0
    
    for var in text_vars + summary_vars:
        if var not in variables:
            variables[var] = f'{{{index}}}'
            index += 1
    
    processed_string = input_string
    for var, placeholder in variables.items():
        processed_string = re.sub(r'\{'+re.escape(var)+r'\}', placeholder, processed_string)
        processed_string = re.sub(r'\$\{'+re.escape(var)+r'\}', placeholder, processed_string)
    
    return processed_string, variables
