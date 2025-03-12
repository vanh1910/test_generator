import subprocess
import os
from main import main

# Đường dẫn chỉ định
path = r"E:\randomthings\test_generator"  # Thay thế bằng đường dẫn thực tế

# Lệnh CMD cần chạy
command = "python main.py"  # Thay thế bằng lệnh bạn muốn chạy

# Số lần lặp
num_iterations = 5

# Chuyển đến thư mục chỉ định
os.chdir(path)

# Vòng lặp chạy lệnh CMD
for i in range(num_iterations):
    main();
