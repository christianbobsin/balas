import argparse

def check_is_builtin(content, c):
   builtin_string = "BuiltinOperator_"
   i = 0
   while content[c+i] == builtin_string[i]:
       i += 1
       if i >= len(builtin_string):
           return True
   return False


def check_is_tflite_status(content, c):
   tflite_string = "TfLiteStatus"
   tflite_string_rev = tflite_string[::-1]
   i = 0
   while content[c-i] == tflite_string_rev[i]:
       i += 1
       if i >= len(tflite_string_rev):
           return True
   return False


def find_tflite_status(content, c):
   i = c
   while True:
       i -= 1
       if not check_is_tflite_status(content, i):
           continue
       return i


def find_start_of_func(content, c):
   i = find_tflite_status(content, c)
   while content[i] != "A":
       i += 1
   return i


def get_op_name(content, i):
   name = ""
   while content[i] != ",":
       name += content[i]
       i += 1
   return name


def get_func_name(content, i):
   name = ""
   while content[i] != "(":
       name += content[i]
       i += 1
   return name


def generate_map(headers_path):
   resolver_map = {}
   with open(headers_path, "r") as file:
       content = file.read()
       count_found_builtin = 0
       curr_op_name = ""
       curr_op_func = ""
       for c in range(len(content)):
           if not check_is_builtin(content, c):
               continue
           count_found_builtin += 1
           if count_found_builtin <= 3:
               continue
           if count_found_builtin == 99:
               break
           curr_op_name = get_op_name(content, c+16)
           start_of_func_name = find_start_of_func(content, c)
           curr_op_func = get_func_name(content, start_of_func_name)
           resolver_map[curr_op_name] = curr_op_func
   with open("python_scripts/code_generator/resolver_map.py", "w") as file:
       file.write(str(resolver_map))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("headers_path", help="Path to the TFLM micro_mutable_op_resolver.h file")
    args = parser.parse_args()
    generate_map(args.headers_path)


