import os
import tkinter as tk
from tkinter import filedialog, messagebox

def merge_code_files():
    # 1. Khởi tạo cửa sổ ẩn của tkinter
    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính
    root.attributes('-topmost', True) # Đưa hộp thoại lên trên cùng

    # 2. Mở hộp thoại chọn thư mục
    folder_path = filedialog.askdirectory(title="Chọn thư mục code của bạn")
    
    if not folder_path:
        print("Đã hủy chọn thư mục.")
        return

    output_file = "all_code.txt"
    ignore_files = {output_file}
    
    # Đếm số file đã xử lý để báo cáo
    count = 0

    try:
        # 3. Mở file txt để ghi kết quả
        with open(output_file, "w", encoding="utf-8") as out:
            for root_dir, dirs, files in os.walk(folder_path):
                # Bỏ qua các thư mục ẩn hoặc thư mục môi trường ảo (tùy chọn thêm)
                if any(ignored in root_dir for ignored in [".git", "__pycache__", "venv", ".vscode"]):
                    continue

                for file in files:
                    if file in ignore_files:
                        continue

                    file_path = os.path.join(root_dir, file)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Ghi Header cho mỗi file
                        out.write("=" * 80 + "\n")
                        out.write(f"PATH: {os.path.relpath(file_path, folder_path)}\n")
                        out.write("=" * 80 + "\n")

                        # Ghi nội dung
                        out.write(content + "\n\n")
                        count += 1

                    except Exception as e:
                        out.write("=" * 80 + "\n")
                        out.write(f"FILE: {file_path}\n")
                        out.write("=" * 80 + "\n")
                        out.write(f"[Lỗi không đọc được file: {e}]\n\n")

        # 4. Thông báo hoàn tất
        messagebox.showinfo("Thành công", f"Đã gộp xong {count} file vào: {output_file}")
        print(f"Hoàn tất! Kết quả tại: {os.path.abspath(output_file)}")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi lưu file: {e}")

if __name__ == "__main__":
    merge_code_files()