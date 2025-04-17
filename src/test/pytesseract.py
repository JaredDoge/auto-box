import pytesseract
from PIL import Image
import re
import json

# 设置 Tesseract 路径（根据系统修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows 示例

def extract_text_from_image(image_path):
    """用 OCR 提取图片中的文字（优化数字和符号识别）"""
    img = Image.open(image_path)
    # 配置 Tesseract 只识别数字和基本运算符（提升准确率）
    custom_config = r'--oem 3 --psm 6 outputbase digits -c tessedit_char_whitelist=0123456789+-*/=?.'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text.strip()

def solve_math_question(text):
    """解析加减乘除题目并计算答案"""
    # 清理题目：移除空格、问号、等号，保留运算符和数字
    cleaned = re.sub(r'[^\d+\-*/]', '', text)  # 只保留数字和 +-*/
    
    # 分离数字和运算符
    parts = re.split(r'([+\-*/])', cleaned)
    parts = [p for p in parts if p]  # 移除空字符串
    
    if len(parts) != 3:  # 格式应为 [数字, 运算符, 数字]
        return {"error": "题目格式无效，请确保是简单的加减乘除运算"}
    
    num1, operator, num2 = parts
    try:
        num1, num2 = float(num1), float(num2)
    except ValueError:
        return {"error": "数字解析失败"}
    
    # 根据运算符计算
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    elif operator == '*':
        answer = num1 * num2
    elif operator == '/':
        if num2 == 0:
            return {"error": "除零错误"}
        answer = num1 / num2
    else:
        return {"error": "不支持的运算符"}
    
    # 返回结构化结果
    return {
        "question": text,
        "operator": operator,
        "answer": answer,
        "explanation": f"{num1}{operator}{num2}={answer}"
    }

# 示例使用
if __name__ == "__main__":
    image_path = "888.png"  # 替换为你的图片路径
    try:
        extracted_text = extract_text_from_image(image_path)
        print("提取的文字:", extracted_text)
        
        result = solve_math_question(extracted_text)
        print("结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print({"error": f"处理失败: {str(e)}"})