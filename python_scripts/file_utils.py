import os
import shutil

def copy_directory(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory '{src_dir}' does not exist.")
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

def copy_file(filepath, dest_dir):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Source file '{filepath}' does not exist.")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    shutil.copy(filepath, dest_dir)

def insert_line(filepath, line_number, new_text):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    lines.insert(line_number - 1, new_text + '\n')
    with open(filepath, 'w') as file:
        file.writelines(lines)

def find_and_replace(file_path, target_string, replacement_string):
    with open(file_path, 'r') as file:
        content = file.read()
    modified_content = content.replace(target_string, replacement_string)
    with open(file_path, 'w') as file:
        file.write(modified_content)

def replace_line(file_path, line_number, new_string):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if 0 < line_number <= len(lines):
            lines[line_number - 1] = new_string + '\n'
            with open(file_path, 'w') as file:
                file.writelines(lines)
        else:
            print(f"Line number {line_number} is out of range.")

    except Exception as e:
        print(f"An error occurred: {e}")

def append_text_to_file(file_path, text):
    try:
        with open(file_path, 'a') as file: 
            file.write(text)
    except Exception as e:
        print(f"An error occurred: {e}")

def create_directory_if_not_exists(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        print(f"An error occurred while creating the directory: {e}")

def set_execute_permissions(file_path):
    os.chmod(file_path, 0o777)