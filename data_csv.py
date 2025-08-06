import os
import csv  # 导入 csv 模块


def generate_html_by_type(csv_file_names, csv_data_dir, image_csv_name='images.csv', output_dir='output', output_prefix=''):
    """
    读取多个 CSV 文件，根据文件名推断 'type' 对问题进行分组，
    并为每种类型在指定目录中生成一个单独的 HTML 文件。
    同时，它会根据提供的图片 CSV 文件，在问题中包含对应的图片。

    Args:
        csv_file_names (list): 输入 CSV 文件名的列表（例如，['a.csv', 'b.csv', 'c.csv']）。
        csv_data_dir (str): 包含所有 CSV 文件和 'images' 文件夹的子目录名称。
        image_csv_name (str): 包含图片路径的 CSV 文件名（例如，'images.csv'）。
        output_dir (str): 保存 HTML 文件的子目录名称。
        output_prefix (str): 输出 HTML 文件名的前缀。
    """
    all_questions = []
    image_map = {}

    # 构建完整的图片 CSV 文件路径
    full_image_csv_path = os.path.join(csv_data_dir, image_csv_name)

    # 1. 从 images.csv 加载图片路径
    try:
        with open(full_image_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                j_id = cleaned_row.get('J')
                # image_path_from_csv 此时是 'images/0.jpg'
                image_path_from_csv = cleaned_row.get('ImagePath')
                if j_id and image_path_from_csv:
                    # image_map 中存储的是相对于 csv_data_dir 的路径，例如 'images/0.jpg'
                    image_map[j_id] = image_path_from_csv.replace('\\', '/')
        print(f"成功从 {full_image_csv_path} 加载图片路径。")
    except FileNotFoundError:
        print(f"警告: 未找到图片 CSV 文件 '{full_image_csv_path}'。将不会链接任何图片。")
    except Exception as e:
        print(f"加载图片 CSV '{full_image_csv_path}' 时出错: {e}")

    # 2. 解析问题 CSV 文件
    for csv_file_name in csv_file_names:
        full_csv_file_path = os.path.join(csv_data_dir, csv_file_name)
        try:
            base_name = os.path.basename(csv_file_name)
            doc_type = os.path.splitext(base_name)[0].upper()

            with open(full_csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cleaned_row = {k.strip(): v.strip() for k, v in row.items()}

                    question_data = {
                        "J": cleaned_row.get('J', ''),  # 保留 J 字段用于图片查找
                        "index": cleaned_row.get('I', ''),
                        "question": cleaned_row.get('Q', ''),
                        "options": {
                            "A": cleaned_row.get('A', ''),
                            "B": cleaned_row.get('B', ''),
                            "C": cleaned_row.get('C', ''),
                            "D": cleaned_row.get('D', '')
                        },
                        "answer": cleaned_row.get('T', ''),
                        "attachment": "",  # CSV 中没有此字段，设为空
                        "type": doc_type  # 从文件名推断类型
                    }

                    # 如果找到对应的图片路径，则添加到问题数据中
                    if question_data["J"] in image_map:
                        question_data["image_path"] = image_map[question_data["J"]]

                    all_questions.append(question_data)
        except FileNotFoundError:
            print(f"错误: 未找到文件 '{full_csv_file_path}'。跳过。")
            continue
        except Exception as e:
            print(f"处理 CSV 文件 '{full_csv_file_path}' 时出错: {e}。跳过。")
            continue

    if not all_questions:
        print("没有找到有效的问题进行处理。")
        return

    # 如果输出目录不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}")

    # 按 'type' 对问题进行分组
    grouped_questions = {}
    for question in all_questions:
        doc_type = question.get('type')
        if doc_type:
            if doc_type not in grouped_questions:
                grouped_questions[doc_type] = []
            grouped_questions[doc_type].append(question)

    # 为每个组生成 HTML 文件
    for doc_type, questions in grouped_questions.items():
        # 构建 HTML 的输出路径
        html_output_path = os.path.join(output_dir, f"{output_prefix}{doc_type}.html")

        # HTML 头部，链接到外部样式表
        # 样式表路径相对于 HTML 文件（假设 styles.css 在父目录中）
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{doc_type}题库</title>
            <link rel="stylesheet" href="./styles.css">
        </head>
        <body>
            <main>
                <h1>{doc_type}题库</h1>
        """

        for item in questions:
            question_text = item.get("question", "问题未找到")
            answer_keys = item.get("answer", "")
            options = item.get("options", {})
            # index = item.get("index", "")
            image_path_from_map = item.get("image_path")  # 获取图片路径 (例如 'images/0.jpg')

            # 根据答案键构建完整的答案文本
            full_answer_list = []
            # 确保 answer_keys 是字符串并遍历其字符
            for key_char in str(answer_keys):
                if key_char in options:
                    full_answer_list.append(options[key_char])

            full_answer_text = "<br>".join(full_answer_list)

            if not full_answer_text:
                full_answer_text = f"{answer_keys}"

            # 如果存在图片路径，则添加图片标签
            image_html = ""
            if image_path_from_map:
                # 调整图片路径，使其相对于 HTML 文件
                # HTML 文件在 'output/' 中，图片在 'csv_data_dir/images/' 中
                # 因此，从 'output/file.html' 到 'csv_data_dir/images/image.jpg' 需要 '../csv_data_dir/images/image.jpg'
                relative_image_path = os.path.join('..', csv_data_dir, image_path_from_map).replace('\\',
                                                                                                    '/')  # 确保 HTML 使用正斜杠
                image_html = f'<div class="question-image-container"><img src="{relative_image_path}" alt="问题图片" class="question-image"></div>'

            # 将问题和答案添加到 HTML 内容中
            html_content += f"""
            <div class="question-block">
                <p class="question">{question_text}</p>
                {image_html} <!-- 在这里插入图片 -->
                <p class="answer">{full_answer_text}</p>
            </div>
            """

        # 关闭 HTML 内容
        html_content += """
            </main>
        </body>
        </html>
        """

        # 将完整的 HTML 内容写入指定的 HTML 文件
        try:
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"成功生成HTML文件: {html_output_path}")
        except IOError as e:
            print(f"写入HTML文件时出错: {e}")

# 示例用法：
# 确保 'a.csv', 'b.csv', 'c.csv' 和 'images.csv' 位于与脚本相同的目录中。
# 脚本将在名为 'output' 的新文件夹中生成 HTML 文件。
# 请确保您的 'styles.css' 文件位于 'output' 文件夹的父目录中。

# 示例 CSV 文件的路径列表（仅文件名）
csv_files_to_process = ['class_a.csv', 'class_b.csv', 'class_c.csv']
# 包含所有 CSV 和图片的子目录名称
data_directory = 'data_csv'
# 图片映射 CSV 文件名
image_mapping_csv_name = 'images.csv'

generate_html_by_type(csv_files_to_process, data_directory, image_mapping_csv_name, output_dir='output')