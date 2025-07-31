# find_null_bytes.py
import os

def find_null_bytes(directory):
    """
    يبحث عن بايتات فارغة (\x00) في جميع ملفات .py داخل الدليل المحدد.
    """
    found_issues = False
    print(f"جاري البحث عن بايتات فارغة في ملفات Python داخل: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f: # افتح الملف كـ binary
                        content = f.read()
                        if b'\x00' in content:
                            print(f"  ❌ تم العثور على بايتات فارغة في: {filepath}")
                            found_issues = True
                except Exception as e:
                    print(f"  ⚠️ خطأ في قراءة الملف {filepath}: {e}")
    if not found_issues:
        print(f"  ✅ لم يتم العثور على بايتات فارغة في أي ملف .py داخل: {directory}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
        
    # **قم بفحص جذر المشروع بالكامل.**
    # هذا سيشمل جميع المجلدات الفرعية وملفات .py فيها.
    find_null_bytes(project_root)
    