import re

def process_string(input_string):
    input_pattern = r'(?<!\$)\{(.*?)\}'
    output_pattern = r'\$\{(.*?)\}'
    
    input_vars = re.findall(input_pattern, input_string)
    output_vars = re.findall(output_pattern, input_string)
    
    variables = {}
    index = 0
    
    for var in output_vars:
        if var not in variables:
            variables[var] = f"<completion{index}></completion{index}>"
            index += 1
    
    processed_string = input_string
    for var, placeholder in variables.items():
        processed_string = re.sub(r'\$\{'+re.escape(var)+r'\}', placeholder, processed_string)
    
    return input_vars, output_vars, processed_string