from PIL import Image, ImageDraw, ImageFont

def create_json_icon():
    # 创建一个白色背景的图像
    size = (64, 64)
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的边框
    draw.rectangle([2, 2, 61, 61], outline='#2196F3', width=2)
    
    # 添加文本
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制文本
    draw.text((10, 20), "JSON", fill='#2196F3', font=font)
    
    # 保存图标
    img.save('icon.png')
    print("图标已创建：icon.png")

if __name__ == "__main__":
    create_json_icon()