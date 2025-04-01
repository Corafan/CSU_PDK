from __future__ import annotations
import inspect
import os
import csufactory.components as components

#第二版：
# 获取所有组件（排除 __init__.py）
def list_components():
    comp_dir = os.path.dirname(components.__file__)
    comp_files = [
        f[:-3] for f in os.listdir(comp_dir) if f.endswith(".py") and f != "__init__.py"
    ]
    return comp_files

# 获取函数的参数列表
def get_function_params(func):
    """获取函数的参数列表"""
    signature = inspect.signature(func)  # 使用inspect模块获取函数的签名信息,签名包含了函数的参数及其默认值。
    params = signature.parameters  # 获取所有的参数信息,包含了参数的名称和其它信息（如类型、默认值等）。
    return [param for param in params.values()]  # 将字典中的参数转成一个列表,并返回这个列表。

# 让用户选择组件并输入参数
def prompt_user_for_params():
    """与用户对话，获取输入的参数"""
    components_list = list_components()
    print(f"CSUPDK包含的组件有：")
    for i, comp in enumerate(components_list, start=1):
        print(f"{i}. {comp}")  # 打印目前csupdk包含的器件

    while True:  # 循环直到用户确认选择
        # 选择组件
        component_choice = input(f"请选择组件（输入数字，如1或2等）: ")
        try:
            component_choice = int(component_choice) - 1  # 用户输入的数字从1开始，列表从0开始
            if component_choice < 0 or component_choice >= len(components_list):
                raise ValueError("无效的选择")
        except ValueError:
            print("无效的选择")
            continue  # 重新选择

        # 向用户返回选择的组件名
        selected_component_name = components_list[component_choice]
        print(f"您选择的组件是: {selected_component_name}")

        # 确认选择
        confirm = input(f"确认选择 '{selected_component_name}' 吗？(Y/N): ").strip().upper()
        if confirm == "Y":
            break  # 跳出循环
        elif confirm == "y":
            print("重新选择组件...")
            continue  # 重新选择
        elif confirm == "N":
            print("重新选择组件...")
            continue  # 重新选择
        elif confirm == "n":
            print("重新选择组件...")
            continue  # 重新选择
        else:
            print("请输入 Y（确认）或 N（重新选择）")
            continue  # 重新确认

    # 动态导入组件函数
    module = __import__(f"csufactory.components.{selected_component_name}", fromlist=[selected_component_name])
    component_func = getattr(module, selected_component_name)

    docstring = inspect.getdoc(component_func)
    print(f"组件{selected_component_name}及其参数的描述如下：\n")
    print(docstring)

    # 获取组件函数的参数
    params = get_function_params(component_func)

    # 获取并提示用户输入参数
    param_values = {}   # 创建一个字典来存储用户输入的参数
    for param in params:   #这里要改,还要增加layer_map和layerspec那部分的内容
        if param.name == "length":
            user_input = input(f"请输入参数 `{param.name}` (默认值: {param.default}): ")
        else:
            user_input = input(f"请输入参数 `{param.name}` (默认值: {param.default}): ")
        if user_input:  # 如果用户输入了内容
            # 根据默认值的类型将用户输入转换为相应的类型
            if isinstance(param.default, float):
                param_values[param.name] = float(user_input)  # 转换为浮动类型
            elif isinstance(param.default, int):
                param_values[param.name] = int(user_input)  # 转换为整数类型
            else:
                param_values[param.name] = user_input  # 对于其他类型直接保存为字符串
        else:  # 如果用户没有输入任何内容，使用默认值
            param_values[param.name] = param.default
    return selected_component_name, param_values  # 返回组件名称和参数字典

# 运行选择的组件函数，并传入用户输入的参数
def run_component_function(func_name, param_values):
    """运行组件函数，并传入用户输入的参数"""
    module = __import__(f"csufactory.components.{func_name}", fromlist=[func_name])
    component_func = getattr(module, func_name)
    component = component_func(**param_values)  # 使用用户输入的参数运行组件函数
    return component  # 返回生成的组件对象

#这里可以增加_是否要保存gds文件？保存路径？
#layer_map部分的选择！！！
#是否需要打印layer_stack?是否有参数需要修改？
#是否需要打印3d的？
#增加“返回上一步”的选项
#考虑增加”返回某一步“的选项
#考虑和csupdk.py那部分结合(打印端口)




# 主程序
if __name__ == "__main__":
    #第二版：
    # 获取函数的参数
    selected_component_name, params = prompt_user_for_params()
    if selected_component_name:
        # 使用用户输入的参数运行组件函数
        component = run_component_function(selected_component_name, params)
        # 显示生成的组件
        component.show()


#第一版：
# # 获取所有组件（排除 __init__.py）
# def list_components():
#     comp_dir = os.path.dirname(components.__file__)
#     comp_files = [
#         f[:-3] for f in os.listdir(comp_dir) if f.endswith(".py") and f != "__init__.py"
#     ]
#     return comp_files
#
# def get_function_params(func):
#     """获取函数的参数列表"""
#     signature = inspect.signature(func)  # 使用inspect模块获取函数的签名信息,签名包含了函数的参数及其默认值。
#     params = signature.parameters  # 获取所有的参数信息,包含了参数的名称和其它信息（如类型、默认值等）。
#     return [param for param in params.values()]  # 将字典中的参数转成一个列表,并返回这个列表。
#
# #这里继续使用了上一个函数返回的列表params
# def prompt_user_for_params(params):
#     """与用户对话，获取输入的参数"""
#     components_list = list_components()
#     print(f"CSUPDK包含的组件有：")
#     for i, comp in enumerate(components_list, start=1):
#         print(f"{i}. {comp}")
#
#     param_values = {}  # 创建一个字典来存储用户输入的参数
#     for param in params:  # 遍历每个参数
#         if param.name=="length":
#             user_input = input(f"请输入参数 `{param.name}` (默认值: {param.default}): ")  # 提示用户输入参数
#         if user_input:  # 如果用户输入了内容
#             # 根据默认值的类型将用户输入转换为相应的类型
#             if isinstance(param.default, float):
#                 param_values[param.name] = float(user_input)  # 转换为浮动类型
#             elif isinstance(param.default, int):
#                 param_values[param.name] = int(user_input)  # 转换为整数类型
#             else:
#                 param_values[param.name] = user_input  # 对于其他类型直接保存为字符串
#         else:  # 如果用户没有输入任何内容，使用默认值
#             param_values[param.name] = param.default
#     return param_values  # 返回包含用户输入的参数字典
#
# def run_component_function(func, params):
#     """运行组件函数，并传入用户输入的参数"""
#     param_values = prompt_user_for_params(params)  # 获取用户输入的参数
#     component = func(**param_values)  # 使用用户输入的参数运行组件函数
#     return component  # 返回生成的组件对象
#
# # 主程序
# if __name__ == "__main__":
#     第一版：
#     # 获取组件函数的参数
#     params = get_function_params(crossing)
#     # 与用户对话并获取参数
#     component = run_component_function(crossing, params)
#     # 显示生成的组件
#     component.show()
#
#     # c=crossing()
#     # c.show()



