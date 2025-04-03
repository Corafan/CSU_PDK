from __future__ import annotations
import inspect
import os
import csufactory.components as components
from typing import Dict, Any
import gdsfactory as gf
import datetime
from functools import partial
from gdsfactory.add_pins import add_pins_inside1nm
from csufactory.generic_tech.layer_map import CSULAYER as LAYER

# # 定义添加端口的功能
# _add_pins = partial(
#     add_pins_inside1nm,
#     pin_length=0.5,
#     layer=LAYER.PORT
# )

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
    """只负责输入组件参数，增加参数级返回功能"""
    # 动态导入组件函数
    module = __import__(f"csufactory.components.{selected_component_name}", fromlist=[selected_component_name])
    component_func = getattr(module, selected_component_name)

    docstring = inspect.getdoc(component_func)
    print(f"组件{selected_component_name}及其参数的描述如下：\n")
    print(docstring)

    # 获取组件函数的参数
    params = get_function_params(component_func)
    param_values = {}  # 创建一个字典来存储用户输入的参数
    param_list = list(params)  # 将参数转为列表以便索引访问
    current_index = 0  # 当前正在输入的参数索引

    print("\n[B-返回上一步/Q-退出]")
    print("请依次输入以下参数（直接回车使用默认值）：")
    print("----------------------------------------")
    while current_index < len(param_list):
        param = param_list[current_index]

        # 设置默认值（优先使用旧参数，其次使用参数默认值）
        default_value = old_params[param.name] if (old_params and param.name in old_params) else param.default

        # # 显示当前参数和剩余参数
        # print(f"\n当前参数 ({current_index + 1}/{len(param_list)}):")
        # print(f"已输入参数: {list(param_values.keys())}")
        # print(f"待输入参数: {[p.name for p in param_list[current_index + 1:]]}")

        # 获取用户输入
        user_input = input(f"请输入参数 `{param.name}` (默认值: {default_value}) : ").strip()

        # 处理特殊命令
        if user_input.upper() in('B',"b"):  # 返回上一步
            if current_index > 0:
                current_index -= 1  # 回到上一个参数
                # 删除上一步的参数值，以便重新输入
                prev_param = param_list[current_index].name
                if prev_param in param_values:
                    del param_values[prev_param]
                print(f"已返回参数 {prev_param}，请重新输入")
            else:
                print("已经是第一个参数，无法返回")
            continue

        elif user_input.upper() in('Q',"q"):  # 退出
            print("参数输入已取消")
            return None

        # 处理正常参数输入
        if user_input:  # 如果用户输入了内容
            try:
                # 根据默认值的类型将用户输入转换为相应的类型
                if isinstance(default_value, float):
                    param_values[param.name] = float(user_input)
                elif isinstance(default_value, int):
                    param_values[param.name] = int(user_input)
                else:
                    param_values[param.name] = user_input
            except ValueError:
                print(f"错误：'{user_input}' 不是有效的 {type(default_value).__name__} 类型")
                continue  # 重新输入当前参数
        else:
            param_values[param.name] = default_value

        current_index += 1  # 移动到下一个参数
    print("----------------------------------------")
    return param_values

#运行选择的组件函数，并传入用户输入的参数
def run_component_function(func_name, param_values):
    """运行组件函数，并传入用户输入的参数"""
    module = __import__(f"csufactory.components.{func_name}", fromlist=[func_name])
    component_func = getattr(module, func_name)
    component = component_func(**param_values)  # 使用用户输入的参数运行组件函数
    return component  # 返回生成的组件对象

# def run_component_function(func_name: str, param_values: dict, add_ports: bool = True) -> gf.Component:
#     """运行组件函数并添加端口层
#
#     返回:
#         gf.Component: 成功返回组件对象，失败返回None
#     """
#     try:
#         module = __import__(f"csufactory.components.{func_name}", fromlist=[func_name])
#         component_func = getattr(module, func_name)
#
#         # 生成组件
#         component = component_func(**param_values)
#         if component is None:
#             raise ValueError("组件函数返回了None")
#
#         # 自动添加端口层
#         if add_ports:
#             try:
#                 component = _add_pins(component)
#                 print(f"已添加端口层 ({LAYER.PORT})")
#             except Exception as e:
#                 print(f"警告: 添加端口层失败 - {str(e)}")
#
#         return component
#
#     except Exception as e:
#         print(f"生成组件失败: {str(e)}")
#         return None

def save_gds(component):
    """保存组件到GDS文件"""
    # 文件名：
    component_name = input(f"请输入文件名(若未输入，则自动分配时间名称): ")
    if component_name == "":
        component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        component_name = component_name
    # 文件保存地址：
    output_gds_path = input(
        f"请输入文件地址（若未输入，将默认保存到C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds）: ")
    if output_gds_path == "":
        # 无时间戳：
        output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
        # # 有时间戳：
        # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    else:
        output_gds_path = output_gds_path
    component.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")

###########打印层栈信息##########
def export_layer_stacks(material: str, layer_stacks: Dict[str, Any], output_dir: str, export_mode: str = "separate",
                        combined_filename: str = None):
    """导出层栈数据到文件

    Args:
        material: 材料名称
        layer_stacks: 层栈字典 {百分比: 层栈对象}
        output_dir: 输出目录路径
        export_mode: 导出模式 ("separate"或"combined")
        combined_filename: 合并文件名(仅当export_mode="combined"时使用)
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"无法创建目录 {output_dir}: {str(e)}")
        return

    if export_mode == "separate":
        # 只导出单独文件
        success_count = 0
        for percent_str, stack in layer_stacks.items():
            if _export_single_stack(material, percent_str, stack, output_dir):
                success_count += 1
        print(f"\n✓ 成功导出 {success_count}/{len(layer_stacks)} 个单独文件")
    elif export_mode == "combined":
        # 只导出合并文件
        if combined_filename is None:
            combined_filename = f"{material}_Combined_LayerStacks.txt"
        _export_combined_stacks(material, layer_stacks, output_dir, combined_filename)


def _export_single_stack(material: str, percent_str: str, stack: Any, output_dir: str):
    """导出单个层栈到单独文件"""
    # 生成标准化文件名
    filename = f"{material}_LayerStack_{percent_str.replace('%', 'percent')}.txt"
    path = os.path.join(output_dir, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            _write_stack_content(material, f, percent_str, stack)

        print(f"✓ 成功保存: {path}")
        return path
    except Exception as e:
        print(f"× 导出失败: {str(e)}")
        return None


def _export_multiple_stacks(material: str, layer_stacks: Dict[str, Any], output_dir: str, combined_filename: str,
                            is_combined_export: bool = False):
    """导出多个层栈到合并文件和单独文件"""
    combined_path = os.path.join(output_dir, combined_filename)
    success_count = 0

    try:
        with open(combined_path, "w", encoding="utf-8") as combined_file:
            combined_file.write(f"===== Material: {material} =====\n\n")
            print(f"\n正在合并 {len(layer_stacks)} 个层栈到: {combined_filename}")

            for percent_str, stack in layer_stacks.items():
                _write_stack_content(material, combined_file, percent_str, stack)
                # 如果不是合并导出模式，才导出单个文件
                if not is_combined_export:
                    if _export_single_stack(material, percent_str, stack, output_dir):
                        success_count += 1

        print(f"\n✓ 合并完成: {combined_path}")
        if not is_combined_export:
            print(f"✓ 成功导出 {success_count}/{len(layer_stacks)} 个单独文件")
    except Exception as e:
        print(f"× 合并文件导出失败: {str(e)}")


def _export_combined_stacks(material: str, layer_stacks: Dict[str, Any], output_dir: str, combined_filename: str):
    """导出多个层栈到合并文件"""
    combined_path = os.path.join(output_dir, combined_filename)

    try:
        with open(combined_path, "w", encoding="utf-8") as combined_file:
            combined_file.write(f"===== Material: {material} =====\n\n")
            print(f"\n正在合并 {len(layer_stacks)} 个层栈到: {combined_filename}")

            for percent_str, stack in layer_stacks.items():
                _write_stack_content(material, combined_file, percent_str, stack)

        print(f"\n✓ 合并完成: {combined_path}")
    except Exception as e:
        print(f"× 合并文件导出失败: {str(e)}")


def _write_stack_content(material: str, file_obj, percent_str: str, stack: Any):
    """将层栈内容写入文件对象"""
    # 写入标题和基本信息
    file_obj.write(f"\n===== {material} - {percent_str} =====\n")
    file_obj.write(f"Design Rules for {percent_str} Delta N index (um)\n")
    file_obj.write("\t\tParameter\n")

    # 写入基底信息
    if hasattr(stack, 'layers') and 'substrate' in stack.layers:
        substrate = stack.layers['substrate']
        if hasattr(substrate, 'info'):
            file_obj.write("Substrate Properties:\n")
            for k, v in substrate.info.items():
                file_obj.write(f"\t{k}: {v}\n")

    # 写入各层信息
    for layer_name, layer in stack.layers.items():

        file_obj.write(f"\nLayer: {layer_name}\n")
        file_obj.write(f"\tThickness: {getattr(layer, 'thickness', 'N/A')}\n")
        file_obj.write(f"\tThickness_tolerance: {getattr(layer, 'thickness_tolerance', 'N/A')}\n")
        file_obj.write(f"\tMaterial: {getattr(layer, 'material', 'N/A')}\n")
        file_obj.write(f"\tZmin: {getattr(layer, 'zmin', 'N/A')}\n")
        file_obj.write(f"\tDerivedLayer: {getattr(layer, 'derived_layer', 'N/A')}\n")

        # 写入额外信息
        if layer_name != "substrate" and getattr(layer, 'info', None):
            file_obj.write("\tInfo:\n")
            for key, value in layer.info.items():
                file_obj.write(f"\t\t{key}: {value}\n")
#############打印层栈信息##########

def run():
    """运行用户交互"""
    # 初始化参数字典
    params = {}
    selected_component_name = None
    # 操作历史记录，每个元素格式：(操作类型, 组件名, 参数字典)
    history = []

    while True:  # 主循环：控制整个程序流程
        # 第一步：选择组件(不返回则只进行一次)
        if not selected_component_name:
            selected_component_name = select_component()
            if not selected_component_name:
                return  # 用户取消选择时退出程序
            # 记录器件选择操作，保存当前组件名和参数
            history.append(("器件选择", selected_component_name, params.copy()))

        # 第二步：参数输入（带上次参数作为默认值）
        params = input_component_params(selected_component_name, old_params=params)
        # 记录参数输入操作，保存当前组件名和参数
        history.append(("参数输入", selected_component_name, params.copy()))
        # 运行并显示组件
        component = run_component_function(selected_component_name, params)
        component.show()
        # 记录显示操作
        history.append(("显示器件", component))

        # 操作选择循环（重新选器件or保存文件or修改参数or退出）
        while True:
            print("\n请选择操作：")
            print("[S] 保存当前GDS文件")
            print("[M] 修改当前器件参数")
            print("[R] 重新选择器件")
            print("[L] 导出层栈信息")
            print("[B] 返回上一步")
            print("[Q] 退出程序")
            choice = input("请输入您的选择(不区分大小写): ").strip().upper()

            if choice in ("S", "s"):
                # 文件名：
                save_gds(component)
                continue  # 返回操作选择菜单

            elif choice in ("M", "m"):
                break  # 跳出操作循环，回到主循环

            elif choice in ("R", "r"):  # 重新选择器件
                selected_component_name = None  # 重置组件选择
                params = {}  # 清空参数
                history = []  # 清空历史
                break  # 跳出参数和操作循环，回到组件选择

            elif choice in ("B", "b"):  # 返回上一步
                if len(history) >= 2:  # 确保有上一步
                    last_action, last_comp, last_params = history[-2]  # 获取上一步完整状态

                    if last_action == "参数输入":
                        # 恢复到参数输入状态
                        selected_component_name = last_comp  # 恢复组件名
                        params = last_params.copy()  # 恢复参数
                        history = history[:-1]  # 移除当前状态
                        break  # 回到参数输入

                    elif last_action == "器件选择":
                        # 恢复到器件选择状态
                        selected_component_name = None  # 重置组件选择
                        params = {}  # 清空参数
                        history = history[:-1]  # 移除当前状态
                        break  # 回到组件选择

                print("已是最初步骤，无法再返回")
                continue

            elif choice in ("Q", "q"):  # 退出程序
                print("gds文件未保存,程序已退出,可以手动保存gds文件")
                return  # 退出了

            elif choice in ("L", "l"):  # 导出层栈
                try:
                    from csufactory.components.generate_Para.component_layer_stack import (
                        Si_zp45_LayerStack, Si_zp75_LayerStack, Si_150_LayerStack,
                        Quartz_zp45_LayerStack, Quartz_zp75_LayerStack
                    )

                    # 按材料分类的层栈字典
                    material_stacks = {
                        "Si": {
                            "0.45%": Si_zp45_LayerStack,
                            "0.75%": Si_zp75_LayerStack,
                            "1.5%": Si_150_LayerStack
                        },
                        "Quartz": {
                            "0.45%": Quartz_zp45_LayerStack,
                            "0.75%": Quartz_zp75_LayerStack
                        }
                    }

                    # 第一步：选择材料范围
                    print("\n请选择要导出的材料:")
                    print("1. Si")
                    print("2. Quartz")
                    print("3. 全部材料")
                    material_choice = input("请输入选择(1-3): ").strip()

                    # 获取输出目录（所有导出模式共用）
                    default_dir = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter"
                    path_choice = input(f"使用默认保存路径({default_dir})? [Y/N]: ").strip().upper()
                    output_dir = default_dir if path_choice != "N" else input("请输入新保存路径: ").strip()

                    # 第二步：根据选择确定要导出的层栈
                    if material_choice == "1":
                        selected_material = "Si"
                        stacks_to_export = material_stacks["Si"]
                    elif material_choice == "2":
                        selected_material = "Quartz"
                        stacks_to_export = material_stacks["Quartz"]
                    elif material_choice == "3":
                        selected_material = "All"
                        # 合并所有材料的层栈
                        stacks_to_export = {}
                        for mat, stacks in material_stacks.items():
                            stacks_to_export.update({f"{mat}_{k}": v for k, v in stacks.items()})
                    else:
                        print("无效选择")
                        continue

                    # 第三步：选择导出模式
                    if material_choice in ("1", "2"):  # 单个材料
                        print(f"\n[{selected_material}] 导出选项:")
                        print("1. 导出单个层栈")
                        print("2. 导出全部分开文件")
                        print("3. 导出合并文件")

                        mode = input("请选择导出模式(1-3): ").strip()

                        if mode == "1":
                            print(f"\n[{selected_material}] 可选层栈:")
                            percents = list(stacks_to_export.keys())
                            for i, percent in enumerate(percents, 1):
                                print(f"{i}. {percent}")

                            percent_choice = input("选择要导出的层栈(数字): ").strip()
                            if percent_choice.isdigit() and 0 < int(percent_choice) <= len(percents):
                                selected_percent = percents[int(percent_choice) - 1]
                                export_layer_stacks(
                                    material=selected_material,
                                    layer_stacks={selected_percent: stacks_to_export[selected_percent]},
                                    output_dir=output_dir,
                                    export_mode="separate"
                                )
                            else:
                                print("无效选择")

                        elif mode == "2":
                            export_layer_stacks(
                                material=selected_material,
                                layer_stacks=stacks_to_export,
                                output_dir=output_dir,
                                export_mode="separate"
                            )

                        elif mode == "3":
                            default_name = f"{selected_material}_Combined.txt"
                            file_choice = input(f"请输入文件名（默认合并文件名为{default_name}) [Y/enter表示默认]: ").strip().upper()
                            if file_choice in ("Y", "y", ""):
                                file_name = default_name
                            else:
                                file_name = file_choice+ ".txt"


                            export_layer_stacks(
                                material=selected_material,
                                layer_stacks=stacks_to_export,
                                output_dir=output_dir,
                                export_mode="combined",
                                combined_filename=file_name
                            )

                        else:
                            print("无效选择")
#############################这里可以用_export_multiple_stacks这个函数来做一个新功能，打印单个材料合并和分开的。
                    elif material_choice == "3":  # 全部材料
                        print("\n[全部材料] 导出选项:")
                        print("1. 导出全部分开文件")
                        print("2. 导出合并文件")

                        mode = input("请选择导出模式(1-2): ").strip()

                        if mode == "1":
                            # 导出全部分开文件（不生成合并文件）
                            for mat, stacks in material_stacks.items():
                                print(f"\n正在导出 {mat} 的层栈文件...")
                                export_layer_stacks(
                                    material=mat,
                                    layer_stacks=stacks,
                                    output_dir=output_dir,
                                    export_mode="separate"
                                )
                        elif mode == "2":
                            # 导出合并文件
                            all_stacks = {}
                            for mat, stacks in material_stacks.items():
                                all_stacks.update({f"{mat}_{k}": v for k, v in stacks.items()})

                            # 询问合并文件名
                            default_name = "ALL_Materials_Combined.txt"
                            file_choice = input(f"请输入文件名（默认合并文件名为{default_name}) [Y/enter表示默认]: ").strip().upper()
                            if file_choice in ("Y", "y", ""):
                                file_name = default_name
                            else:
                                file_name = file_choice + ".txt"

                            print("\n正在导出合并文件...")
                            export_layer_stacks(
                                material="All_Materials",
                                layer_stacks=all_stacks,
                                output_dir=output_dir,
                                export_mode="combined",
                                combined_filename=file_name
                            )
                        else:
                            print("无效选择")

                except ImportError as e:
                    print(f"无法导入层栈: {str(e)}")
                except Exception as e:
                    print(f"发生错误: {str(e)}")

                continue  # 返回操作菜单
        # 根据用户选择决定下一步流程
        if choice in ("R", "r"):
            continue  # 直接继续主循环，重新选择组件
        elif choice in ("M", "m"):
            continue  # 继续主循环，重新输入参数（保留组件选择和当前参数）
        elif choice in ("B", "b"):
            continue  # 已在上面的返回逻辑中处理



#这里可以增加_是否要保存gds文件？是否需要修改器件？保存路径？（√）
#layer_map部分的选择！！！（这里不需要选择，在做器件的时候已经决定了器件层是WG）
#增加“返回上一步”的选项（√）
#增加”返回指定一步“的选项（√）
#增加输入参数时”返回上一步“的选项（√）
#是否需要打印layer_stack?（√）
#layer_stack是否有参数需要修改？（好像有点复杂，不如直接去文件中修改）

#是否需要打印3d的？
#考虑和csupdk.py那部分结合(打印端口)


# 主程序
if __name__ == "__main__":
    run()

# def input_component_params(selected_component_name, old_params=None):
#     """只负责输入组件参数"""
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
#     # 获取并提示用户输入参数
#     param_values = {}  # 创建一个字典来存储用户输入的参数
#     for param in params:
#         # 修改：
#         default_value = old_params[param.name] if old_params else param.default
#         # 这里要改,还要增加layer_map和layerspec那部分的内容
#         if param.name == "length":
#             user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}): ")
#         else:
#             user_input = input(f"请输入参数 `{param.name}` (未输入则保持默认值或上轮输入值: {default_value}):")
#         if user_input:  # 如果用户输入了内容
#             # 根据默认值的类型将用户输入转换为相应的类型
#             if isinstance(default_value, float):
#                 param_values[param.name] = float(user_input)  # 转换为浮动类型
#             elif isinstance(default_value, int):
#                 param_values[param.name] = int(user_input)  # 转换为整数类型
#             else:
#                 param_values[param.name] = user_input  # 对于其他类型直接保存为字符串
#         else:
#             param_values[param.name] = default_value  # 如果用户没有输入任何内容，使用默认值
#     return param_values

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

# def export_layer_stacks(material: str, layer_stacks: Dict[str, Any], combined_filename: str = None):
#     # 路径询问保持原有实现
#     default_dir = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter"
#     path_choice = input(f"使用默认保存路径({default_dir})? [Y/N]: ").strip().upper()
#     output_dir = default_dir if path_choice != "N" else input("请输入新保存路径: ").strip()
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 确保路径存在
#     os.makedirs(output_dir, exist_ok=True)
#
#     if len(layer_stacks) == 1:
#         percent, stack = next(iter(layer_stacks.items()))
#         _export_single_stack(material, percent, stack, output_dir)
#     else:
#         if combined_filename is None:
#             combined_filename = f"{material}_Combined.txt"  # 自动添加材料前缀
#         # 询问合并文件名
#         file_choice = input(f"使用默认合并文件名({combined_filename})? [Y/n]: ").strip().upper()
#         if file_choice in('N',"n"):
#             new_name = input("请输入新文件名(不含路径): ").strip()
#             if new_name:
#                 combined_filename = new_name
#
#         _export_multiple_stacks(material, layer_stacks, output_dir, combined_filename)
#
# def _export_single_stack(material: str, percent_str: str, stack: Any, output_dir: str):
#     """导出单个层栈（添加材料前缀）"""
#     filename = f"{material}_LayerStack_{percent_str.replace('%', 'percent')}.txt"
#     path = os.path.join(output_dir, filename)
#
#     with open(path, "w", encoding="utf-8") as f:
#         # 在文件头添加材料信息
#         _write_stack_content(material,f, percent_str, stack)
#
#     print(f"TXT文件已保存至: {path}--(有需要可自行修改参数)")
#     return path
#
#
# def _export_multiple_stacks(material: str, layer_stacks: Dict[str, Any], output_dir: str, combined_filename: str):
#     """导出多个层栈（添加材料信息）"""
#     combined_path = os.path.join(output_dir, combined_filename)
#
#     with open(combined_path, "w", encoding="utf-8") as combined_file:
#         combined_file.write(f"===== Material: {material} =====\n\n")  # 添加材料标题
#         print(f"将合并LayerStack中的主要参数保存至下方文件内：")
#
#         for percent_str, stack in layer_stacks.items():
#             _write_stack_content(material,combined_file, percent_str, stack)
#             _export_single_stack(material, percent_str, stack, output_dir)
#
#     print(f"\n合并文件已保存至: {combined_path}(有需要可自行修改参数)")
#
#
# def _write_stack_content(material: str,file_obj, percent_str: str, stack: Any):
#     """将层栈内容写入文件对象"""
#     file_obj.write(f"\n====={material}-{percent_str} =====\n")
#     file_obj.write(f"Design Rules for {percent_str} Delta N index (um)\n")
#     file_obj.write("\t\tParameter\n")
#
#     # 写入基底信息
#     if hasattr(stack, 'layers') and 'substrate' in stack.layers:
#         substrate = stack.layers['substrate']
#         if hasattr(substrate, 'info'):
#             for k, v in substrate.info.items():
#                 file_obj.write(f"{k}: {v}\n")
#
#     # 写入各层信息
#     for layer_name, layer in stack.layers.items():
#
#         file_obj.write(f"\nLayerName: {layer_name}:\n")
#         file_obj.write(f"\tThickness: {layer.thickness},\n")
#         file_obj.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
#         file_obj.write(f"\tMaterial: {layer.material},\n")
#         file_obj.write(f"\tZmin: {layer.zmin},\n")
#         file_obj.write(f"\tDerivedLayer: {layer.derived_layer}\n")
#
#         if layer_name != "substrate" and getattr(layer, 'info', None):
#             file_obj.write("\tInfo:\n")
#             for key, value in layer.info.items():
#                 file_obj.write(f"\t\t{key}: {value}\n")

# elif choice in ("L", "l"):  # 导出层栈
#     try:
#         from csufactory.components.generate_Para.component_layer_stack import (
#             Si_zp45_LayerStack, Si_zp75_LayerStack, Si_150_LayerStack,
#             Quartz_zp45_LayerStack, Quartz_zp75_LayerStack
#         )
#
#         # 按材料分类的层栈字典
#         material_stacks = {
#             "Si": {
#                 "0.45%": Si_zp45_LayerStack,
#                 "0.75%": Si_zp75_LayerStack,
#                 "1.5%": Si_150_LayerStack
#             },
#             "Quartz": {
#                 "0.45%": Quartz_zp45_LayerStack,
#                 "0.75%": Quartz_zp75_LayerStack
#             }
#         }
#
#         # 第一步：选择材料范围
#         print("\n请选择要导出的材料:")
#         print("1. Si")
#         print("2. Quartz")
#         print("3. 全部材料")
#         material_choice = input("请输入选择(1-3): ").strip()
#
#         # 第二步：根据选择确定要导出的层栈
#         if material_choice == "1":
#             selected_material = "Si"
#             stacks_to_export = material_stacks["Si"]
#         elif material_choice == "2":
#             selected_material = "Quartz"
#             stacks_to_export = material_stacks["Quartz"]
#         elif material_choice == "3":
#             selected_material = "All"
#             # 合并所有材料的层栈
#             stacks_to_export = {}
#             for mat, stacks in material_stacks.items():
#                 stacks_to_export.update({f"{mat}_{k}": v for k, v in stacks.items()})
#         else:
#             print("无效选择")
#             continue
#
#         # 第三步：选择导出模式
#         if material_choice in ("1", "2"):  # 单个材料
#             print(f"\n[{selected_material}] 导出选项:")
#             print("1. 导出单个层栈")
#             print("2. 导出全部分开文件")
#             print("3. 导出合并文件")
#
#             mode = input("请选择导出模式(1-3): ").strip()
#
#             if mode == "1":
#                 print(f"\n[{selected_material}] 可选层栈:")
#                 percents = list(stacks_to_export.keys())
#                 for i, percent in enumerate(percents, 1):
#                     print(f"{i}. {percent}")
#
#                 percent_choice = input("选择要导出的层栈(数字): ").strip()
#                 if percent_choice.isdigit() and 0 < int(percent_choice) <= len(percents):
#                     selected_percent = percents[int(percent_choice) - 1]
#                     export_layer_stacks(
#                         material=selected_material,
#                         layer_stacks={selected_percent: stacks_to_export[selected_percent]}
#                     )
#                 else:
#                     print("无效选择")
#
#             elif mode == "2":
#                 export_layer_stacks(
#                     material=selected_material,
#                     layer_stacks=stacks_to_export
#                 )
#
#             elif mode == "3":
#                 export_layer_stacks(
#                     material=selected_material,
#                     layer_stacks=stacks_to_export,
#                     combined_filename=f"{selected_material}_Combined.txt"
#                 )
#
#             else:
#                 print("无效选择")
#
#
#         # 修改运行部分中的导出逻辑
#
#         elif material_choice == "3":  # 全部材料
#
#             print("\n[全部材料] 导出选项:")
#             print("1. 导出全部分开文件")
#             print("2. 导出合并文件")
#             mode = input("请选择导出模式(1-2): ").strip()
#             # 获取输出目录（只需要询问一次）
#             default_dir = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter"
#             path_choice = input(f"使用默认保存路径({default_dir})? [Y/N]: ").strip().upper()
#             output_dir = default_dir if path_choice != "N" else input("请输入新保存路径: ").strip()
#             if mode == "1":
#                 # 导出全部分开文件（不生成合并文件）
#                 for mat, stacks in material_stacks.items():
#                     print(f"\n正在导出 {mat} 的层栈文件...")
#                     export_layer_stacks(
#                         material=mat,
#                         layer_stacks=stacks,
#                         output_dir=output_dir,
#                         export_mode="separate"
#                     )
#
#             elif mode == "2":
#                 # 导出合并文件
#                 all_stacks = {}
#                 for mat, stacks in material_stacks.items():
#                     all_stacks.update({f"{mat}_{k}": v for k, v in stacks.items()})
#                 # 询问合并文件名
#                 default_name = "ALL_Materials_Combined.txt"
#                 file_choice = input(f"使用默认合并文件名({default_name})? [Y/n]: ").strip().upper()
#                 if file_choice == "N":
#                     default_name = input("请输入新文件名(不含路径和扩展名): ").strip() + ".txt"
#                 print("\n正在导出合并文件...")
#
#                 export_layer_stacks(
#                     material="All_Materials",
#                     layer_stacks=all_stacks,
#                     output_dir=output_dir,
#                     export_mode="combined",
#                     combined_filename=default_name
#                 )
#             else:
#                 print("无效选择")
#
#     except ImportError as e:
#         print(f"无法导入层栈: {str(e)}")
#     except Exception as e:
#         print(f"发生错误: {str(e)}")
#
#     continue  # 返回操作菜单

# elif choice in ("L", "l"):  # 导出层栈
#     try:
#         from csufactory.components.generate_Para.component_layer_stack import (
#             Si_zp45_LayerStack,
#             Si_zp75_LayerStack,
#             Si_150_LayerStack,
#             Quartz_zp45_LayerStack,
#             Quartz_zp75_LayerStack,
#         )
#         # 按材料分类的层栈字典
#         material_stacks = {
#             "Si": {
#                 "0.45%": Si_zp45_LayerStack,
#                 "0.75%": Si_zp75_LayerStack,
#                 "1.5%": Si_150_LayerStack
#             },
#             "Quartz": {
#                 "0.45%": Quartz_zp45_LayerStack,
#                 "0.75%": Quartz_zp75_LayerStack
#             }
#         }
#         # 第一步：选择材料类型
#         print("\n请选择材料类型:")
#         materials = list(material_stacks.keys())
#         for i, material in enumerate(materials, 1):
#             print(f"{i}. {material}")
#
#         material_choice = input("输入材料编号: ").strip()
#
#         if not material_choice.isdigit() or not (0 < int(material_choice) <= len(materials)):
#             print("无效选择")
#             continue
#
#         selected_material = materials[int(material_choice) - 1]
#         available_stacks = material_stacks[selected_material]
#         # 第二步：选择导出模
#         print(f"\n[{selected_material}] 导出选项:")
#         print("1. 导出当前材料的单个层栈")
#         print("2. 导出当前材料全部分开文件")
#         print("3. 导出当前材料合并文件")
#         # print("4. 导出所有材料全部分开文件")
#         # print("5. 导出所有材料合并文件")
#
#         mode = input("请选择导出模式(1-5): ").strip()
#
#         # 第三步：执行导出（路径询问在export_layer_stacks内部处理）
#         if mode == "1":
#             print(f"\n[{selected_material}] 可选层栈:")
#             percents = list(available_stacks.keys())
#             for i, percent in enumerate(percents, 1):
#                 print(f"{i}. {percent}")
#
#             percent_choice = input("选择要导出的层栈(数字): ").strip()
#             if percent_choice.isdigit() and 0 < int(percent_choice) <= len(percents):
#                 selected_percent = percents[int(percent_choice) - 1]
#                 export_layer_stacks(
#                     material=selected_material,
#                     layer_stacks={selected_percent: available_stacks[selected_percent]}
#                 )
#             else:
#                 print("无效选择")
#
#         elif mode == "2":
#             export_layer_stacks(
#                 material=selected_material,
#                 layer_stacks=available_stacks
#             )
#
#         elif mode == "3":
#             export_layer_stacks(
#                 material=selected_material,
#                 layer_stacks=available_stacks,
#                 combined_filename=f"{selected_material}_Combined.txt"
#             )
#
#         # elif mode == "4":
#         #     for mat, stacks in material_stacks.items():
#         #         export_layer_stacks(
#         #             material=mat,
#         #             layer_stacks=stacks
#         #         )
#         #
#         # elif mode == "5":
#         #     all_stacks = {}
#         #     for mat, stacks in material_stacks.items():
#         #         all_stacks.update({f"{mat}_{k}": v for k, v in stacks.items()})
#         #
#         #     export_layer_stacks(
#         #         material="All_Materials",
#         #         layer_stacks=all_stacks,
#         #         combined_filename="ALL_Materials_Combined.txt"
#         #     )
#
#         else:
#             print("无效选择")
#
#     except ImportError as e:
#         print(f"无法导入层栈: {str(e)}")
#
#     continue  # 返回操作菜单

# #帮我优化一下这个循环，我想要有像你一样的（重新选择组件、修改参数、退出和保存等）
# 这个有点不对，
# def run():
#     # 第一步：选择组件（只执行一次）
#     selected_component_name = select_component()
#     if not selected_component_name:
#         return
#
#     # 第二步：输入参数（可重复）
#     params = input_component_params(selected_component_name)
#     while True:  # 添加主循环
#         # 运行并显示组件
#         # 尝试添加幕布，但是这样的话无法show ports和hide ports
#         # c=gf.Component()
#         # component = run_component_function(selected_component_name, params)
#         # c.add_ref(component)
#         # c.show()
#         component = run_component_function(selected_component_name, params)
#         component.show()
#
#         #保存文件or修改参数or退出
#         while True:
#             save_choice = input(f"是否需要修改文件？（N-修改器件）保存gds文件？（(Y,enter键表示需要;任意键表示不保存并退出)）: ")
#             if save_choice in ("Y", "y", ""):
#                 #文件名：
#                 component_name = input(f"请输入文件名(若未输入，则自动分配名称): ")
#                 if component_name=="":
#                     component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#                 else:
#                     component_name = component_name
#                 #文件保存地址：
#                 output_gds_path = input(f"请输入文件地址（若未输入，将默认保存到C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds）: ")
#                 if output_gds_path=="":
#                     # 无时间戳：
#                     output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
#                     # # 有时间戳：
#                     # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#                     # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
#                 else:
#                     output_gds_path = output_gds_path
#                 component.write_gds(output_gds_path)
#                 print(f"GDS 文件已保存至: {output_gds_path}")
#                 break
#             elif save_choice in ("N", "n"):
#                     params = input_component_params(selected_component_name, old_params=params)
#             else:
#                 modify_choice = input("gds文件未保存,按任意键退出。返回上一步输入“N”: ")
#                 if modify_choice in ("N", "n"):
#                     continue
#                 # 带着旧参数返回器件参数输入部分，重新进行参数输入
#                 else:
#                     print(f"gds文件未保存，可以手动进行保存哦！")
#                     break
#             break

#跳转至有点鸡肋
# def run():
#     """运行用户交互"""
#     # 初始化参数字典
#     params = {}
#     selected_component_name = None
#     history = []  # 用于记录操作历史
#
#     while True:  # 主循环：控制整个程序流程
#         # 第一步：选择组件(不返回则只进行一次)
#         if not selected_component_name:
#             selected_component_name = select_component()
#             if not selected_component_name:
#                 return  # 用户取消选择时退出程序
#             history.append(("器件选择", selected_component_name, params.copy()))
#
#         # 第二步：参数输入（带上次参数作为默认值）
#         params = input_component_params(selected_component_name, old_params=params)
#         history.append(("器件参数输入", selected_component_name, params.copy()))
#
#         component = run_component_function(selected_component_name, params)
#         component.show()
#         history.append(("生成gds图并展示在klayout", component))
#
#         # 操作选择循环（重新选器件or保存文件or修改参数or退出）
#         while True:
#             print("\n请选择操作：")
#             print("[S] 保存当前GDS文件")
#             print("[M] 修改当前器件参数")
#             print("[R] 重新选择器件")
#             print("[B] 返回上一步")
#             print("[J] 跳转到指定步骤")
#             print("[Q] 退出程序")
#             choice = input("请输入您的选择(不区分大小写): ").strip().upper()
#
#             if choice in ("S", "s"):
#                 # 文件名：
#                 save_gds(component)
#                 continue  # 返回操作选择菜单
#
#             elif choice in ("M", "m"):
#                 break  # 跳出操作循环，回到主循环
#
#             elif choice in ("R", "r"):  # 重新选择器件
#                 selected_component_name = None  # 重置组件选择
#                 params = {}  # 清空参数
#                 history = []  # 清空历史
#                 break  # 跳出参数和操作循环，回到组件选择
#
#             elif choice in ("B", "b"):  # 返回上一步
#                 if len(history) >= 2:  # 确保有上一步
#                     last_action, last_comp, last_params = history[-2]  # 获取上一步记录
#
#                     if last_action == "器件参数输入":
#                         selected_component_name = last_comp  # 恢复组件名
#                         params = last_params.copy()  # 恢复参数
#                         history = history[:-1]  # 移除当前状态
#                         break  # 回到参数输入
#
#                     elif last_action == "器件选择":
#                         selected_component_name = None  # 重置组件选择
#                         params = {}  # 清空参数
#                         history = history[:-1]  # 移除当前状态
#                         break  # 回到组件选择
#
#                 print("无法再返回了")
#                 continue
#
#             elif choice in ("J", "j"):  # 跳转到指定步骤
#                 print("\n操作历史：")
#                 # 显示历史记录
#                 for i, (action, *_) in enumerate(history):
#                     print(f"{i + 1}. {action}")  # 显示步骤编号和类型
#
#                 try:
#                     step = int(input("输入要跳转的步骤号: ")) - 1
#                     if 0 <= step < len(history):
#                         action, *states = history[step]
#
#                         if action == "器件选择":
#                             selected_component_name, params = states[0], states[1]
#                             history = history[:step + 1]
#                             break
#
#                         elif action == "器件参数输入":
#                             selected_component_name, params = states[0], states[1].copy()
#                             history = history[:step + 1]
#                             break
#
#                     else:
#                         print("无效的步骤号")
#                 except ValueError:
#                     print("请输入有效数字")
#                 continue
#
#             elif choice in ("Q", "q"):  # 退出程序
#                 print("gds文件未保存,程序已退出,可以手动保存gds文件")
#                 return  # 退出了
#
#             else:
#                 print("无效输入，请重新选择")
#                 continue
#
#         # 根据选择决定下一步
#         if choice in ("R", "r"):
#             continue  # 直接继续主循环，重新选择组件
#         elif choice in ("M", "m"):
#             continue  # 继续主循环，重新输入参数（保留组件选择和当前参数）
#         elif choice in ("B", "b") or choice in ("J", "j"):
#             continue  # 已在上面的逻辑中处理
#

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



