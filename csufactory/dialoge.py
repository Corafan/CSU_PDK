from __future__ import annotations
import inspect
import os
import csufactory.components as components
import datetime

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

def select_component():
    """只负责选择组件，不涉及参数输入"""
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
        confirm = input(f"确认选择 '{selected_component_name}' 吗？(Y/N,enter键表示确认): ").strip().upper()
        if confirm in ("Y", "y", ""):   # 输入 Y/y/回车 均视为确认
            return selected_component_name
        elif confirm in ("N", "n"):     # 输入 N/n 重新选择
            print("重新选择组件...")
            continue
        else:                           # 其他输入提示错误
            print("请输入 Y（确认）或 N（重新选择）")
            continue

def input_component_params(selected_component_name, old_params=None):
    """只负责输入组件参数"""
    # 动态导入组件函数
    module = __import__(f"csufactory.components.{selected_component_name}", fromlist=[selected_component_name])
    component_func = getattr(module, selected_component_name)

    docstring = inspect.getdoc(component_func)
    print(f"组件{selected_component_name}及其参数的描述如下：\n")
    print(docstring)

    # 获取组件函数的参数
    params = get_function_params(component_func)
    # 获取并提示用户输入参数
    param_values = {}  # 创建一个字典来存储用户输入的参数
    for param in params:
        # 修改：
        default_value = old_params[param.name] if old_params else param.default
        # 这里要改,还要增加layer_map和layerspec那部分的内容
        if param.name == "length":
            user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}): ")
        else:
            user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}):")
        if user_input:  # 如果用户输入了内容
            # 根据默认值的类型将用户输入转换为相应的类型
            if isinstance(default_value, float):
                param_values[param.name] = float(user_input)  # 转换为浮动类型
            elif isinstance(default_value, int):
                param_values[param.name] = int(user_input)  # 转换为整数类型
            else:
                param_values[param.name] = user_input  # 对于其他类型直接保存为字符串
        else:
            param_values[param.name] = default_value  # 如果用户没有输入任何内容，使用默认值
    return param_values

# 运行选择的组件函数，并传入用户输入的参数
def run_component_function(func_name, param_values):
    """运行组件函数，并传入用户输入的参数"""
    module = __import__(f"csufactory.components.{func_name}", fromlist=[func_name])
    component_func = getattr(module, func_name)
    component = component_func(**param_values)  # 使用用户输入的参数运行组件函数
    return component  # 返回生成的组件对象

def run():
    # 第一步：选择组件（只执行一次）
    selected_component_name = select_component()
    if not selected_component_name:
        return

    # 第二步：输入参数（可重复）
    params = input_component_params(selected_component_name)

    while True:  # 添加主循环
        # 运行并显示组件
        component = run_component_function(selected_component_name, params)
        component.show()

        #是否需要自动保存文件?
        save_choice = input(f"是否需要保存gds文件？（(Y,enter键表示需要;任意键表示不保存--退出或修改器件)）: ")
        if save_choice in ("Y", "y", ""):
            #文件名：
            component_name = input(f"请输入文件名(若未输入，则自动分配名称): ")
            if component_name=="":
                component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            else:
                component_name = component_name
            #文件保存地址：
            output_gds_path = input(f"请输入文件地址（若未输入，将默认保存到C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds）: ")
            if output_gds_path=="":
                # 无时间戳：
                output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
                # # 有时间戳：
                # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
            else:
                output_gds_path = output_gds_path
            component.write_gds(output_gds_path)
            print(f"GDS 文件已保存至: {output_gds_path}")
            break
        else:
            modify_choice = input("gds文件未保存，是否需要修改器件（Y/y）？或按任意键退出: ")
            if modify_choice in ("Y", "y"):
                # 带着旧参数返回器件参数输入部分，重新进行参数输入
                params = input_component_params(selected_component_name, old_params=params)
            else:
                print(f"gds文件未保存，可以手动进行保存哦！")
                break


#这里可以增加_是否要保存gds文件？是否需要修改器件？保存路径？（√）
#layer_map部分的选择！！！
#是否需要打印layer_stack?是否有参数需要修改？
#是否需要打印3d的？
#增加“返回上一步”的选项
#考虑增加”返回某一步“的选项
#考虑和csupdk.py那部分结合(打印端口)


# 主程序
if __name__ == "__main__":
    run()


# # 让用户选择组件并输入参数（现在拆分成两个函数--一个选择器件，一个输入参数）
# def prompt_user_for_params(old_params=None):
#     """与用户对话，获取输入的参数"""
#     components_list = list_components()
#     print(f"CSUPDK包含的组件有：")
#     for i, comp in enumerate(components_list, start=1):
#         print(f"{i}. {comp}")  # 打印目前csupdk包含的器件
#
#     while True:  # 循环直到用户确认选择
#         # 选择组件
#         component_choice = input(f"请选择组件（输入数字，如1或2等）: ")
#         try:
#             component_choice = int(component_choice) - 1  # 用户输入的数字从1开始，列表从0开始
#             if component_choice < 0 or component_choice >= len(components_list):
#                 raise ValueError("无效的选择")
#         except ValueError:
#             print("无效的选择")
#             continue  # 重新选择
#
#         # 向用户返回选择的组件名
#         selected_component_name = components_list[component_choice]
#         print(f"您选择的组件是: {selected_component_name}")
#
#         # 确认选择
#         confirm = input(f"确认选择 '{selected_component_name}' 吗？(Y/N,enter键表示确认): ").strip().upper()
#         if confirm in ("Y", "y", ""):  # 输入 Y/y/回车 均视为确认
#             break  # 跳出循环
#         elif confirm in ("N", "n"):  # 输入 N/n 重新选择
#             print("重新选择组件...")
#             continue
#         else:  # 其他输入提示错误
#             print("请输入 Y（确认）或 N（重新选择）")
#             continue
#
#     # 动态导入组件函数
#     module = __import__(f"csufactory.components.{selected_component_name}", fromlist=[selected_component_name])
#     component_func = getattr(module, selected_component_name)
#
#     docstring = inspect.getdoc(component_func)
#     print(f"组件{selected_component_name}及其参数的描述如下：\n")
#     print(docstring)
#
#     # 获取组件函数的参数
#     params = get_function_params(component_func)
#
#     # 获取并提示用户输入参数
#     param_values = {}   # 创建一个字典来存储用户输入的参数
#     for param in params:
#         #修改：
#         default_value = old_params[param.name] if old_params else param.default
#         # 这里要改,还要增加layer_map和layerspec那部分的内容
#         if param.name == "length":
#             user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}): ")
#         else:
#             user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}):")
#         if user_input:  # 如果用户输入了内容
#             # 根据默认值的类型将用户输入转换为相应的类型
#             if isinstance(default_value, float):
#                 param_values[param.name] = float(user_input) # 转换为浮动类型
#             elif isinstance(default_value, int):
#                 param_values[param.name] = int(user_input)   # 转换为整数类型
#             else:
#                 param_values[param.name] = user_input        # 对于其他类型直接保存为字符串
#         else:
#             param_values[param.name] = default_value         # 如果用户没有输入任何内容，使用默认值
#     return selected_component_name, param_values             # 返回组件名称和参数字典



# if __name__ == "__main__":
#     #第二版：
#     # 获取函数的参数
#     selected_component_name, params = prompt_user_for_params()
#     if selected_component_name:
#         # 使用用户输入的参数运行组件函数
#         component = run_component_function(selected_component_name, params)
#         # 显示生成的组件
#         component.show()


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



