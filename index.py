import json


def json_to_html(json_file_path, html_file_path):
    """
    Parses a JSON file containing a list of question-answer dictionaries and
    generates a human-readable HTML file.

    Args:
        json_file_path (str): The path to the input JSON file.
        html_file_path (str): The path where the output HTML file will be saved.
    """
    try:
        # Open and load the JSON data from the specified file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file at '{json_file_path}'. Please check its format.")
        return

    # HTML header with basic styling for readability
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>题目和答案</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 20px; background-color: #f4f4f4; }
            .question-block {
                background: #fff;
                border: 1px solid #ddd;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .question { font-weight: bold; font-size: 1.1em; color: #333; }
            .answer { color: #007BFF; margin-top: 5px; font-style: italic; }
            .answer strong { color: #555; }
        </style>
    </head>
    <body>
        <h1>题目和答案</h1>
    """

    # Loop through each item in the JSON data
    for item in json_data:
        question_text = item.get("question", "问题未找到")
        answer_keys = item.get("answer", "")
        options = item.get("options", {})
        index = item.get("index", "")

        # Build the full answer text from the option keys and descriptions
        full_answer_list = []
        for key in answer_keys:
            if key in options:
                full_answer_list.append(f"{key}: {options[key]}")

        full_answer_text = "；".join(full_answer_list)

        if not full_answer_text:
            full_answer_text = f"答案: {answer_keys}"

        # Append the new question and answer to the HTML content
        html_content += f"""
        <div class="question-block">
            <p class="question">{index}. {question_text}</p>
            <p class="answer"><strong>答案:</strong> {full_answer_text}</p>
        </div>
        """

    # Close the HTML content
    html_content += """
    </body>
    </html>
    """

    # Write the complete HTML content to the specified file
    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"成功生成HTML文件: {html_file_path}")
    except IOError as e:
        print(f"写入文件时出错: {e}")


# Example usage:
# Assuming you have a JSON file named 'data.json' with the required structure.
# The script will save the output to a file named 'output.html'.
json_to_html('data.json', 'output.html')
