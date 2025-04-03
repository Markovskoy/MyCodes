import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # Скрываем окно

file_path = filedialog.askopenfilename(title="Выберите файл")
print(f"Выбран файл: {file_path}")

root.destroy()  # Закрываем `tkinter`, чтобы он не висел в памяти
