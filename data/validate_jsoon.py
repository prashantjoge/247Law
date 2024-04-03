import json


def fix_jsonl_file(input_file_path, output_file_path):
    fixed_lines = []
    with open(input_file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                # Attempt to load the line as JSON to check for validity
                json_obj = json.loads(line)
                # If successful, add the line to the list of fixed lines
                fixed_lines.append(json.dumps(json_obj))
            except json.JSONDecodeError as e:
                print(f"Error decoding line: {e}")
                # Handle or log the error, e.g., print the faulty line or fix it manually
                # For simplicity, we're just printing the error here

    # Write the fixed lines to a new file
    with open(output_file_path, "w", encoding="utf-8") as file:
        for line in fixed_lines:
            file.write(line + "\n")


# Example usage
input_path = "./validation_dataset-v1.jsonl"
output_path = "./fixed_file.jsonl"
fix_jsonl_file(input_path, output_path)
