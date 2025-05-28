import pandas as pd
import requests
import json

# 替换为智谱 GLM-4V API 密钥和请求地址
API_KEY = "YOUR_AIP_KEY"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def analyze_image(image_url):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4v",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": "请详细描述这张商品图片的内容。如果图片中存在模糊不清、难以辨认的部分，请明确指出这些部分是模糊的，而不是尝试描述它们。"}
                ]
            }
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result and result['choices'] and result['choices'][0]['message']['content']:
            content = result['choices'][0]['message']['content']
            return content
        else:
            return "未能获取到图片描述"
    except requests.exceptions.RequestException as e:
        return f"请求图片分析接口失败: {e}"
    except json.JSONDecodeError as e:
        return f"解析图片分析接口响应失败: {e}"
    except Exception as e:
        return f"分析图片时发生未知错误: {e}"

def process_excel(file_path):
    """读取 Excel 文件，分析商品图片，并将结果写回原文件。"""
    try:
        df = pd.read_excel(file_path)
        if "主图链接" not in df.columns:
            print("Error: Excel 文件中缺少 '主图链接' 列。")
            return

        df['图片描述'] = df['主图链接'].apply(analyze_image)

        # 将包含链接和描述的 DataFrame 写回原 Excel 文件
        df.to_excel(file_path, index=False)
        print(f"图片描述已添加到文件: {file_path}")

    except FileNotFoundError:
        print(f"Error: 文件 {file_path} 未找到。")
    except Exception as e:
        print(f"处理 Excel 文件时发生错误: {e}")

if __name__ == "__main__":
    excel_file_path = "商品信息.xlsx"  # 替换为你的 Excel 文件路径
    process_excel(excel_file_path)