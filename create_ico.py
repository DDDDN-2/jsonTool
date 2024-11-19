from PIL import Image

def create_ico():
    # 打开PNG图像
    img = Image.open('icon.png')
    # 保存为ICO
    img.save('icon.ico', format='ICO')
    print("ICO文件已创建：icon.ico")

if __name__ == "__main__":
    create_ico() 