import os



#获取当前项目的根目录
def get_abs_path(file_path) -> str:
    #获取当前文件的绝对路径
    current_file_path = os.path.abspath(file_path)
    #获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)
    #获取当前项目的根目录
    project_dir = os.path.dirname(current_dir)

    return project_dir


