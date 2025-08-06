import json
import os


def generate_html_by_type(json_file_path, output_dir='output'):
    """
    Reads a JSON file containing a list of questions, groups them by 'type',
    and generates a separate HTML file for each type.

    Args:
        json_file_path (str): The path to the input JSON file.
        output_dir (str): The name of the subdirectory to save the HTML files.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file at '{json_file_path}'. Please check its format.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Group questions by their 'type'
    grouped_questions = {}
    for question in all_questions:
        doc_type = question.get('type')
        if doc_type:
            if doc_type not in grouped_questions:
                grouped_questions[doc_type] = []
            grouped_questions[doc_type].append(question)

    # Generate an HTML file for each group
    for doc_type, questions in grouped_questions.items():
        if len(questions) <= 0:
            continue

        if doc_type == '未知':
            output_path = os.path.join(output_dir, "未分类题库.html")
        else:
            output_path = os.path.join(output_dir, f"{doc_type}类题库.html")

        # HTML header with a link to an external stylesheet
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{doc_type}类题库</title>
            <link rel="stylesheet" href="./index.css">
        </head>
        <body>
            <main>
                <h1>{doc_type}类题库</h1>
        """

        for item in questions:
            question_text = item.get("question", "")
            answer_keys = item.get("answer", "")
            options = item.get("options", {})
            # index = item.get("index", "")

            if question_text == "":
                continue

            # Build the full answer text from the option keys and descriptions
            full_answer_list = []
            for key in answer_keys:
                if key in options:
                    full_answer_list.append(options[key])

            full_answer_text = "<br>".join(full_answer_list)

            if not full_answer_text:
                full_answer_text = f"答案: {answer_keys}"

            # Append the question and answer to the HTML content
            html_content += f"""
            <div class="question-block">
                <p class="question">{question_text}</p>
                <p class="answer">{full_answer_text}</p>
            </div>
            """

        # Close the HTML content
        html_content += """
            </main>
        </body>
        </html>
        """

        # Write the complete HTML content to the specified file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"成功生成HTML文件: {output_path}")
        except IOError as e:
            print(f"写入文件时出错: {e}")


# Example usage:
# Assuming your JSON data is in a file named 'data.json'.
# The script will generate output_type_A.html, output_type_B.html, etc.
generate_html_by_type('data/题库带分类.json')
