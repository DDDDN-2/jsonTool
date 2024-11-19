import sys
import os

def check_environment():
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print("\n已安装的包:")
    os.system("pip list")

if __name__ == "__main__":
    check_environment() 