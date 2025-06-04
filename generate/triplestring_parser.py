import re

def process_string(input_string):
    """
    Processes an input string to extract variable placeholders and replace output variables with custom placeholders.
    Args:
        input_string (str): The string containing variable placeholders. Input variables are denoted by `{var}` and output variables by `${var}`.
    Returns:
        tuple:
            - input_vars (list of str): List of variable names found in `{var}` patterns (input variables).
            - output_vars (list of str): List of variable names found in `${var}` patterns (output variables).
            - processed_string (str): The input string with all `${var}` replaced by `<completionN></completionN>` placeholders, where N is a unique index for each output variable.
    Notes:
        - Escaped input variables (e.g., `${var}`) are only replaced, while `{var}` are only extracted.
        - Output variable placeholders are replaced in the order they appear and are unique per variable name.
    """

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