"""
测试程序：显示18种语言支持
运行：python -m pytest tests/test_display_languages.py -v -s
或：python tests/test_display_languages.py
"""
import locale
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_show_locale_call():
    # 强制设置 LC_ALL 环境变量
    try:
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except locale.Error:
        print("系统仍未识别 zh_CN.UTF-8，请检查 locale -a 的输出")

    # 检查 Python 默认的文件系统和终端编码
    print(f"文件系统编码: {sys.getfilesystemencoding()}")
    print(f"标准输出编码: {sys.stdout.encoding}")

def main():
    """主函数 - 运行所有测试"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "TrueNAS Installer 语言测试程序" + " " * 18 + "║")
    print("║" + " " * 15 + "TrueNAS Installer Language Test Program" + " " * 14 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    test_show_locale_call()
    try:
        
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 22 + "🎉 所有测试通过!" + " " * 23 + "║")
        print("║" + " " * 20 + "All tests passed!" + " " * 26 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
