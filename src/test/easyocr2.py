import easyocr

def extract_text_from_image(image_path):
    """使用 EasyOCR 提取文字（默认支持英文，速度快）"""
    reader = easyocr.Reader(['ch_tra', 'en'])  # 只加载英文模型（如需中文，改成 ['ch_tra', 'en']）
    result = reader.readtext(image_path, detail=0)  # detail=0 只返回文本
    return " ".join(result).strip()  # 合并识别结果并去除首尾空格

# 示例
if __name__ == "__main__":
    text = extract_text_from_image("./src/test/888.png")
    print("识别结果:", text)