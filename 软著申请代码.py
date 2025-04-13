from __future__ import annotations
import os
import inspect
import functools
import csufactory.components as components
from typing import Dict, Any
import datetime
import gdsfactory as gf
from typing import get_origin, get_args, Union, Tuple, List
import ast
from gdsfactory.typings import LayerSpec, CrossSectionSpec
def list_components():
    """获取所有组件（排除 __init__.py）"""
    comp_dir = os.path.dirname(components.__file__)
    comp_files = [
        f[:-3] for f in os.listdir(comp_dir) if f.endswith(".py") and f != "__init__.py"
    ]
    return comp_files
def get_function_params(func):
    """获取函数的参数信息并返回参数列表"""
    #获取函数的签名信息,签名包含了函数的参数及其默认值。
    signature = inspect.signature(func)
    params = signature.parameters
    return [param for param in params.values()]
def select_component():
    """选择组件，不涉及参数输入"""
    components_list = list_components()
    print(f"CSUPDK包含的组件有：")
    for i, comp in enumerate(components_list, start=1):
        print(f"{i}. {comp}")
    while True:
        component_choice = input(f"请选择组件（输入数字，如1或2等）: ")
        try:
            #用户输入的数字从1开始，列表从0开始
            component_choice = int(component_choice) - 1
            if component_choice < 0 or component_choice >= len(components_list):
                raise ValueError("无效的选择")
        except ValueError:
            print("无效的选择")
            continue
        selected_component_name = components_list[component_choice]
        print(f"您选择的组件是: {selected_component_name}")
        confirm = input(f"确认选择 '{selected_component_name}' 吗？(Y/N,enter键表示确认): ").strip().upper()
        if confirm in ("Y", "y", ""):
            return selected_component_name
        elif confirm in ("N", "n"):
            print("重新选择组件...")
            continue
        else:
            print("请输入 Y（确认）或 N（重新选择）")
            continue
def convert_param_value(param_name: str, param_type, value):
    """智能转换参数值到目标类型"""
    if value is None or value == '':
        return None
    # 处理 Union 类型 (如 Union[float, None])
    if get_origin(param_type) is Union:
        types = [t for t in get_args(param_type) if t is not type(None)]
        if types:
            param_type = types[0]
    origin = get_origin(param_type)
    args = get_args(param_type)
    try:
        # 数值类型转换
        if param_type in (float, 'float'):
            if isinstance(value, str):
                if 'um' in value:
                    return float(value.replace('um', '').strip())
                elif 'nm' in value:
                    return float(value.replace('nm', '').strip()) / 1000
            return float(value)
        elif param_type in (int, 'int'):
            return int(float(value))
        elif param_type in (bool, 'bool'):
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'y']
            return bool(value)
        elif param_type in (str, 'str'):
            return str(value)
        # GDS类型
        elif param_type is LayerSpec:
            return gf.get_layer(value)
        elif param_type is CrossSectionSpec:
            return gf.get_cross_section(value) if isinstance(value, str) else value
        # 容器类型：tuple[float, float] / list[float]
        elif origin in (tuple, Tuple):
            if isinstance(value, str):
                try:
                    val = ast.literal_eval(value)
                    if not isinstance(val, tuple):
                        val = tuple(val.split(','))
                except Exception:
                    val = tuple(value.split(','))
            else:
                val = value
            return tuple(float(v.replace('um', '').replace('nm', '').strip()) / (1000 if 'nm' in v else 1)
                         if isinstance(v, str) else float(v)
                         for v in val)
        elif origin in (list, List):
            if isinstance(value, str):
                try:
                    val = ast.literal_eval(value)
                    if not isinstance(val, list):
                        val = list(val.split(','))
                except Exception:
                    val = list(value.split(','))
            else:
                val = value
            return [float(v.replace('um', '').replace('nm', '').strip()) / (1000 if 'nm' in v else 1)
                    if isinstance(v, str) else float(v)
                    for v in val]
        # 默认直接返回
        return value
    except Exception as e:
        print(f"[警告] 参数 {param_name} 转换失败 ({value} → {param_type}): {str(e)}")
        return value
def convert_params(func, param_dict: dict):
    """根据函数签名自动转换参数字典中的值到正确类型"""
    sig = inspect.signature(func)
    converted = {}
    for name, value in param_dict.items():
        if name not in sig.parameters:
            continue
        param = sig.parameters[name]
        param_type = param.annotation
        # 跳过无注解参数
        if param_type is inspect.Parameter.empty:
            converted[name] = value
            continue
        converted[name] = convert_param_value(name, param_type, value)
    return converted
def input_component_params(selected_component_name, old_params=None):
    """输入组件参数，增加参数级返回功能"""
    module = __import__(f"csufactory.components.{selected_component_name}", fromlist=[selected_component_name])
    component_func = getattr(module, selected_component_name)
    docstring = inspect.getdoc(component_func)
    print(f"组件{selected_component_name}及其参数的描述如下：\n")
    print(docstring)
    params = get_function_params(component_func)
    param_values = {}
    param_list = list(params)
    current_index = 0
    print("\n[B-返回上一步/Q-退出]")
    print("请依次输入以下参数（直接回车使用默认值）：")
    print("----------------------------------------")
    while current_index < len(param_list):
        param = param_list[current_index]
        #设置默认值（优先使用旧参数，其次使用参数默认值）
        default_value = old_params[param.name] if (old_params and param.name in old_params) else param.default
        # 特殊参数处理
        if param.name in ['radius', 'angle', 'width']:
            user_input = input(f"请输入参数 {param.name} (单位: um, 默认: {default_value}): ").strip()
            if user_input:
                try:
                    # 处理带单位的输入
                    if 'um' in user_input:
                        param_values[param.name] = float(user_input.replace('um', ''))
                    elif 'nm' in user_input:
                        param_values[param.name] = float(user_input.replace('nm', '')) / 1000
                    else:
                        param_values[param.name] = float(user_input)
                except ValueError:
                    print(f"错误：'{user_input}' 不是有效的数值，使用默认值 {default_value}")
                    param_values[param.name] = default_value
            else:
                param_values[param.name] = default_value
            current_index += 1
            continue
        # 显示参数类型信息
        param_type = getattr(param.annotation, "__name__", str(param.annotation))
        input_prompt = f"请输入参数 {param.name} ({param_type}) (默认: {default_value}): "
        if isinstance(default_value, functools.partial):
            func = default_value.func
            func_params = inspect.signature(func).parameters
            func_keywords = default_value.keywords
            print(f"\n参数 `{param.name}`是一个函数,你可以自定义其参数：\n(默认值: {default_value})")
            new_kwargs = {}
            for key, val in func_keywords.items():
                user_input = input(f"请输入 `{key}` (默认值: {val})：").strip()
                if user_input:
                    try:
                        if isinstance(val, float):
                            new_kwargs[key] = float(user_input)
                        elif isinstance(val, int):
                            new_kwargs[key] = int(user_input)
                        else:
                            new_kwargs[key] = user_input
                    except ValueError:
                        print(f"无法识别类型，使用默认值 {val}")
                        new_kwargs[key] = val
                else:
                    new_kwargs[key] = val
            param_values[param.name] = functools.partial(func, **new_kwargs)
            current_index += 1
            continue
        #获取用户输入
        user_input = input(input_prompt).strip()
        if user_input.upper() in('B',"b"):
            if current_index > 0:
                # 回到上一个参数
                current_index -= 1
                # 删除上一步的参数值，以便重新输入
                prev_param = param_list[current_index].name
                if prev_param in param_values:
                    del param_values[prev_param]
                print(f"已返回参数 {prev_param}，请重新输入")
            else:
                print("已经是第一个参数，无法返回")
            continue
        elif user_input.upper() in('Q',"q"):
            print("参数输入已取消")
            return None
        if user_input:
            try:
                if isinstance(default_value, float):
                    param_values[param.name] = float(user_input)
                elif isinstance(default_value, int):
                    param_values[param.name] = int(user_input)
                else:
                    param_values[param.name] = user_input
            except ValueError:
                print(f"错误：'{user_input}' 不是有效的 {type(default_value).__name__} 类型")
                continue
        else:
            param_values[param.name] = default_value
        current_index += 1
    print("----------------------------------------")
    return param_values
def run_component_function(func_name, param_values):
    """运行组件函数，并传入用户输入的参数"""
    module = __import__(f"csufactory.components.{func_name}", fromlist=[func_name])
    component_func = getattr(module, func_name)
    # 类型转换
    converted_params = convert_params(component_func, param_values)
    try:
        component = component_func(**converted_params)
        return component
    except Exception as e:
        print(f"组件执行失败: {str(e)}")
        print("使用的参数:", converted_params)
        raise
def save_gds(component):
    """保存组件到GDS文件"""
    component_name = input(f"请输入文件名(若未输入，则自动分配时间名称): ")
    if component_name == "":
        component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        component_name = component_name
    output_gds_path = input(f"请输入文件地址（若未输入，将默认保存到C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds）: ")
    if output_gds_path == "":
        output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    else:
        output_gds_path = output_gds_path
    component.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
def export_layer_stacks(
        material: str,
        layer_stacks: Dict[str, Any],
        output_dir: str,
        export_mode: str = "separate",
        combined_filename: str = None
):
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
        success_count = 0
        for percent_str, stack in layer_stacks.items():
            if _export_single_stack(material, percent_str, stack, output_dir):
                success_count += 1
        print(f"\n✓ 成功导出 {success_count}/{len(layer_stacks)} 个单独文件")
    elif export_mode == "combined":
        if combined_filename is None:
            combined_filename = f"{material}_Combined_LayerStacks.txt"
        _export_combined_stacks(material, layer_stacks, output_dir, combined_filename)
def _export_single_stack(
        material: str,
        percent_str: str,
        stack: Any,
        output_dir: str
):
    """导出单个层栈到单独文件"""
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
def _export_multiple_stacks(
        material: str,
        layer_stacks: Dict[str, Any],
        output_dir: str,
        combined_filename: str,
        is_combined_export: bool = False
):
    """导出多个层栈到合并文件和单独文件"""
    combined_path = os.path.join(output_dir, combined_filename)
    success_count = 0
    try:
        with open(combined_path, "w", encoding="utf-8") as combined_file:
            combined_file.write(f"===== Material: {material} =====\n\n")
            print(f"\n正在合并 {len(layer_stacks)} 个层栈到: {combined_filename}")
            for percent_str, stack in layer_stacks.items():
                _write_stack_content(material, combined_file, percent_str, stack)
                #如果不是合并导出模式，导出单个文件。
                if not is_combined_export:
                    if _export_single_stack(material, percent_str, stack, output_dir):
                        success_count += 1
        print(f"\n✓ 合并完成: {combined_path}")
        if not is_combined_export:
            print(f"✓ 成功导出 {success_count}/{len(layer_stacks)} 个单独文件")
    except Exception as e:
        print(f"× 合并文件导出失败: {str(e)}")
def _export_combined_stacks(
        material: str,
        layer_stacks: Dict[str, Any],
        output_dir: str,
        combined_filename: str
):
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
    file_obj.write(f"\n===== {material} - {percent_str} =====\n")
    file_obj.write(f"Design Rules for {percent_str} Delta N index (um)\n")
    file_obj.write("\t\tParameter\n")
    if hasattr(stack, 'layers') and 'substrate' in stack.layers:
        substrate = stack.layers['substrate']
        if hasattr(substrate, 'info'):
            file_obj.write("Substrate Properties:\n")
            for k, v in substrate.info.items():
                file_obj.write(f"\t{k}: {v}\n")
    for layer_name, layer in stack.layers.items():
        file_obj.write(f"\nLayer: {layer_name}\n")
        file_obj.write(f"\tThickness: {getattr(layer, 'thickness', 'N/A')}\n")
        file_obj.write(f"\tThickness_tolerance: {getattr(layer, 'thickness_tolerance', 'N/A')}\n")
        file_obj.write(f"\tMaterial: {getattr(layer, 'material', 'N/A')}\n")
        file_obj.write(f"\tZmin: {getattr(layer, 'zmin', 'N/A')}\n")
        file_obj.write(f"\tDerivedLayer: {getattr(layer, 'derived_layer', 'N/A')}\n")
        if layer_name != "substrate" and getattr(layer, 'info', None):
            file_obj.write("\tInfo:\n")
            for key, value in layer.info.items():
                file_obj.write(f"\t\t{key}: {value}\n")
def run():
    """运行用户交互"""
    params = {}
    selected_component_name = None
    history = []
    while True: # 主循环：控制整个程序流程
        # 第一步：选择组件(不返回则只进行一次)
        if not selected_component_name:
            selected_component_name = select_component()
            if not selected_component_name:
                return
            # 记录器件选择操作，保存当前组件名和参数
            history.append(("器件选择", selected_component_name, params.copy()))
        # 第二步：参数输入（上次参数作为默认值）
        params = input_component_params(selected_component_name, old_params=params)
        history.append(("参数输入", selected_component_name, params.copy()))
        component = run_component_function(selected_component_name, params)
        component.show()
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
                save_gds(component)
                continue
            elif choice in ("M", "m"):
                break
            elif choice in ("R", "r"):
                selected_component_name = None
                params = {}
                history = []
                break
            elif choice in ("B", "b"):
                # 确保有上一步
                if len(history) >= 2:
                    last_action, last_comp, last_params = history[-2]
                    if last_action == "参数输入":
                        selected_component_name = last_comp
                        params = last_params.copy()
                        history = history[:-1]
                        break
                    elif last_action == "器件选择":
                        selected_component_name = None
                        params = {}
                        history = history[:-1]
                        break
                print("已是最初步骤，无法再返回")
                continue
            elif choice in ("Q", "q"):
                print("gds文件未保存,程序已退出,可以手动保存gds文件")
                return
            elif choice in ("L", "l"):
                try:
                    from csufactory.components.generate_Para.component_layer_stack import (
                        Si_zp45_LayerStack, Si_zp75_LayerStack, Si_150_LayerStack,
                        Quartz_zp45_LayerStack, Quartz_zp75_LayerStack
                    )
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
                        stacks_to_export = {}
                        for mat, stacks in material_stacks.items():
                            stacks_to_export.update({f"{mat}_{k}": v for k, v in stacks.items()})
                    else:
                        print("无效选择")
                        continue
                    # 第三步：选择导出模式
                    if material_choice in ("1", "2"):
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
                    elif material_choice == "3":
                        print("\n[全部材料] 导出选项:")
                        print("1. 导出全部分开文件")
                        print("2. 导出合并文件")
                        mode = input("请选择导出模式(1-2): ").strip()
                        if mode == "1":
                            for mat, stacks in material_stacks.items():
                                print(f"\n正在导出 {mat} 的层栈文件...")
                                export_layer_stacks(
                                    material=mat,
                                    layer_stacks=stacks,
                                    output_dir=output_dir,
                                    export_mode="separate"
                                )
                        elif mode == "2":
                            all_stacks = {}
                            for mat, stacks in material_stacks.items():
                                all_stacks.update({f"{mat}_{k}": v for k, v in stacks.items()})
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
                continue
        if choice in ("R", "r"):
            continue
        elif choice in ("M", "m"):
            continue
        elif choice in ("B", "b"):
            continue
from __future__ import annotations
from csufactory.components.wg_arc import wg_arc
from csufactory.components.awg import awg, free_propagation_region
from csufactory.components.Sbend import Sbend
from csufactory.components.coupler import coupler
from csufactory.components.crossing import crossing
from csufactory.components.grating import grating
from csufactory.components.mmi import mmi
from csufactory.components.ring_coupler import ring_coupler
from csufactory.components.ring_resonator import ring_resonator
from csufactory.components.star_coupler import star_coupler
from csufactory.components.Ybranch_1x2 import Ybranch_1x2
from csufactory.components.ybranch import ybranch
__all__ = [
    "wg_arc",
    "awg",
    "free_propagation_region",
    "Sbend",
    "coupler",
    "crossing",
    "grating",
    "mmi",
    "ring_coupler",
    "ring_resonator",
    "star_coupler",
    "Ybranch_1x2",
    "ybranch",
    ]
#生成器件AWG
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from functools import partial
from gdsfactory.typings import ComponentFactory, CrossSectionSpec
from gdsfactory.components.awg import free_propagation_region
@gf.cell
def awg(
        inputs: int = 3,
        arms: int = 10,
        outputs: int = 3,
        free_propagation_region_input_function: ComponentFactory = partial(
            free_propagation_region, width1=2, width2=20.0,length=20,wg_width=0.5),
        free_propagation_region_output_function: ComponentFactory = partial(
            free_propagation_region, width1=10, width2=20.0,length=20,wg_width=0.5),
        fpr_spacing: float = 50.0,
        arm_spacing: float = 1.0,
        cross_section: CrossSectionSpec = "strip"
)-> Component:
    """生成阵列波导光栅.
      Args:
          inputs:输入端口数量.
          arms:阵列波导数量.
          outputs:输出波导数量.
          free_propagation_region_input_function:输入的星型耦合器尺寸.
          free_propagation_region_output_function:输出的星型耦合器尺寸.
          fpr_spacing:输入输出星型耦合器的阵列波导在x方向上的间距。
          arm_spacing:相邻阵列波导之间y方向上的高度差.
          cross_section:横截面类型，其中包含层类型和层号.
      函数Free propagation region:
      Args:
          width1: 输入区域的宽度.
          width2: 输出区域的宽度.
          length: 自由传播区的长度.
          wg_width:波导宽度.
      .. code::
                   length
                   <-->
                     /|
                    / |
             width1|  | width2
                    \ |
                     \|
      """
    return gf.components.awg(
        inputs = inputs,
        arms=arms,
        outputs= outputs,
        free_propagation_region_input_function= free_propagation_region_input_function,
        free_propagation_region_output_function=free_propagation_region_output_function,
        fpr_spacing= fpr_spacing,
        arm_spacing= arm_spacing,
        cross_section=cross_section
    )
#生成器件coupler
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
@gf.cell
def coupler(
        gap: float = 0.5,
        length: float = 0.5,
        dy: Delta = 8,
        dx: Delta = 10.0,
        cross_section: CrossSectionSpec = "strip",
        allow_min_radius_violation: bool = False,
) -> Component:
    r"""生成方向耦合器。
    Args:
        gap: 两个直波导之间的间隙，um。
        length: 直波导长度，um。
        dy: y方向上两个端口之间的垂直距离，um。
        dx: x方向上弯曲波导的长度，um。
        cross_section: 横截面类型，一般无需修改。
        allow_min_radius_violation: 如果为True,则无需检查最小弯曲半径，一般无需修改。
    .. code::
               dx                                 dx
            |------|                           |------|
         o2 ________                           ______o3
                    \                         /           |
                     \        length         /            |
                      ======================= gap         | dy
                     /                       \            |
            ________/                         \_______    |
         o1                                          o4
                        coupler_straight
    """
    return gf.components.coupler(
        gap=gap,
        length=length,
        dx=dx,
        dy=dy,
        cross_section=cross_section,
        allow_min_radius_violation=allow_min_radius_violation,
    )
#生成器件crossing
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec
from gdsfactory.typings import CrossSectionSpec
@gf.cell
def crossing(
    length: float = 10.0,
    width: float = 2.0,
    layer: LayerSpec = "WG",
    port_type: str | None = None,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """生成一个十字crossing.
    Args:
        length:从中心正方形到任意一个端口的距离。
        width:十字crossing的宽度。
        layer:层，（层号，层类型）
        port_type: 电信号端口或光信号端口，electrical或optical.
        （ports按顺时针旋转，o1在左侧）
    """
    layer = gf.get_layer(layer)
    c = gf.Component()
    width_center=width+2
    x1 = gf.get_cross_section(cross_section, width=width_center)
    R = c<<gf.components.straight(length=width_center,cross_section=x1)
    R.dcenter = (0, 0)
    x2 = gf.get_cross_section(cross_section, width=width)
    r = gf.components.straight(length=length, cross_section=x2)
    r1 = c.add_ref(r)
    r2 = c.add_ref(r).drotate(90)
    r3 = c.add_ref(r).drotate(180)
    r4 = c.add_ref(r).drotate(270)
    r1.dmovex( width_center / 2)
    r2.dmovey(width_center / 2)
    r3.dmovex(- width_center / 2)
    r4.dmovey(-width_center / 2)
    c.add_port(
        f"o1",
        width=width,
        layer=layer,
        orientation=180,
        center=(-length - width_center / 2, 0),
        )
    c.add_port(
        f"o2",
        width=width,
        layer=layer,
        orientation=90,
        center=(0, +length + width_center / 2),
        )
    c.add_port(
        f"o3",
        width=width,
        layer=layer,
        orientation=0,
        center=(+length + width_center / 2, 0),
        )
    c.add_port(
        f"o4",
        width=width,
        layer=layer,
        orientation=270,
        center=(0, -length - width_center / 2),
        )
    return c
#生成器件grating
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec
@gf.cell
def grating(
    width:float =4,
    length:float =20,
    num_wg: int = 5,  # 波导数量
    cross_section: ComponentSpec = "strip",
) -> Component:
    """生成一个光栅（grating）。
    Args:
        width:光栅宽度（y方向长度）。
        length:光栅长度（x方向的长度）。
        num_wg: 波导的数量。
        layer:层类型。
    """
    c = gf.Component()
    waveguide_length= 2*width
    waveguide_width= width/3
    x1= gf.get_cross_section(cross_section, width=width)
    wg_center = c << gf.components.straight(length=length, cross_section=x1)
    wg_center.dcenter = (0, 0)
    x2= gf.get_cross_section(cross_section, width=waveguide_length)
    wg_ = gf.components.straight(length=waveguide_width,cross_section=x2)
    for i in range(num_wg):
        delta_y= (length)/(num_wg+1)
        x_start= - length/2 + delta_y
        x = x_start + i * delta_y
        wg = c << wg_
        wg.dcenter = (0, 0)
        wg.dmove((x,0))
    c.add_port(f"o1", port=wg_center.ports["o1"])
    c.add_port(f"o2",port=wg_center.ports["o2"])
    c.flatten()
    return c
#生成器件mmi
from __future__ import annotations
from gdsfactory.typings import CrossSectionSpec
import gdsfactory as gf
from gdsfactory.component import Component
@gf.cell
def mmi(
    inputs: float = 6,
    outputs:  float = 6,
    width_wg: float = 2,
    length_wg: float = 5.0,
    length_mmi: float = 60,
    width_mmi: float = 40.0,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""
    Args:
        inputs:输入波导数量（分布均匀）。
        outputs:输出波导数量（分布均匀）。
        width_wg: 输入输出波导与mmi接触部分的长度，即输入输出波导x方向上的长度。
        length_wg:输入输出波导y方向上的长度。
        length_mmi:x方向上的长度。
        width_mmi:y方向上的长度。
        cross_section:横截面类型，一般无需修改。
    .. code::
                   length_mmi
                    <------>
                    ________
                   |        |
                __/          \__
     signal_in  __            __  I_out1
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                  |          \__
                  |           __  Q_out1
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                __/          \__
        LO_in   __            __  Q_out2
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                  |          \__
                  |           __  I_out2
                  |          /
                  | ________|
    """
    inputs = int(inputs)
    outputs = int(outputs)
    c = gf.Component()
    gap_mmi_in=(width_mmi-width_wg*inputs)/inputs
    gap_mmi_out=(width_mmi-width_wg*outputs)/outputs
    w_mmi = width_mmi
    wg1=gf.components.straight(width=width_wg,length=length_wg, cross_section=cross_section)
    x = gf.get_cross_section(cross_section)
    _ = c << gf.components.straight(
        length=length_mmi,
        width=w_mmi,
        cross_section=cross_section,
    )
    y_signal_in_list = [
        - (width_mmi/2) + (gap_mmi_in / 2) + (width_wg / 2) + i * gap_mmi_in + i * width_wg
        for i in range(inputs)
    ]
    y_signal_out_list = [
        (width_mmi / 2) - (gap_mmi_out / 2) - (width_wg / 2) - i * gap_mmi_out - i * width_wg
        for i in range(outputs)
    ]
    ports = []
    for i, y in enumerate(y_signal_in_list):
        port_name = f"in_{i+1}"
        ports.append(
            gf.Port(
                name=port_name,
                orientation=180,
                center=(0, y),
                width=width_wg,
                cross_section=cross_section,
            )
        )
    for i, y in enumerate(y_signal_out_list):
        port_name = f"out_{i+1}"
        ports.append(
            gf.Port(
                name=port_name,
                orientation=0,
                center=(length_mmi, y),
                width=width_wg,
                cross_section=cross_section,
            )
        )
    for port in ports:
        wg_ref = c << wg1
        wg_ref.connect(port="o2", other=port)
        c.add_port(name=port.name, port=wg_ref.ports["o1"])
    c.flatten()
    x.add_bbox(c)
    return c
#生成器件ring_coupler
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec
@gf.cell
def ring_coupler(
    gap: float = 0.2,
    radius: float = 5.0,
    width: float = 1.5,
    layer: LayerSpec = "WG",
    cross_section: ComponentSpec = "strip",
) -> Component:
    r"""生成环形耦合器
    Args:
        gap: 环形和直波导之间的间隙。
        radius: 环形外环的半径。
        width: 直波导（y方向）和环形的宽度。
        layer:层类型（层号，层类型）,可以改变环形的层类型,一般无需修改。
        cross_section:横截面类型，一般无需修改。
    .. code::
        o2    length_x   o3
           ---=========---   gap
            /           \
           |             |
            \           /
             \         /
           ---=========---   gap
        o1    length_x   o4
    """
    c = gf.Component()
    width_wg = width
    length_wg = 3*radius
    x1 = gf.get_cross_section(cross_section, width=width_wg)
    wg_bottom = c << gf.components.straight(length=length_wg,cross_section=x1)
    wg_top = c << gf.components.straight(length=length_wg,cross_section=x1)
    wg_bottom.dcenter = (0, 0)
    wg_top.dcenter = (0, 0)
    gap_=gap+radius+width/2
    wg_bottom.movey(-gap_)
    wg_top.movey(gap_)
    circle_outer=  gf.components.circle(radius=radius,layer=layer)
    circle_inner=  gf.components.circle(radius=radius-width,layer=layer)
    ring= gf.boolean(circle_outer, circle_inner, operation="xor", layer=layer)
    c << ring
    c.add_port(f"o1", port=wg_bottom.ports["o1"])
    c.add_port(f"o2", port=wg_top.ports["o1"])
    c.add_port(f"o3",port=wg_top.ports["o2"])
    c.add_port(f"o4",port=wg_bottom.ports["o2"])
    c.flatten()
    return c
##生成器件ring_resonator
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec
@gf.cell
def ring_resonator(
    gap: float = 0.3,
    radius: float = 5.0,
    width: float = 1.5,
    layer: LayerSpec = "WG",
    cross_section: ComponentSpec = "strip",
) -> Component:
    r"""生成环形谐振器
    Args:
        gap: 环形和直波导之间的间隙。
        radius: 环形外环的半径。
        width: 直波导（y方向）和环形的宽度。
        layer:层类型（层号，层类型）,可以改变环形的层类型,一般无需修改。
        cross_section:横截面类型，一般无需修改。
    .. code::
             ------------
            /           \
           |             |
            \           /
             \         /
           ---=========--- gap
        o1    length_x   o2
    """
    c = gf.Component()
    width_wg = width
    length_wg = 3 * radius
    x1 = gf.get_cross_section(cross_section, width=width_wg)
    wg_bottom = c << gf.components.straight(length=length_wg, cross_section=x1)
    wg_bottom.dcenter = (0, 0)
    gap_=-gap-radius-width/2
    wg_bottom.movey(gap_)
    circle_outer=  gf.components.circle(radius=radius,layer=layer)
    circle_inner=  gf.components.circle(radius=radius-width,layer=layer)
    ring= gf.boolean(circle_outer, circle_inner, operation="xor", layer=layer)
    c << ring
    c.add_port(f"o1", port=wg_bottom.ports["o1"])
    c.add_port(f"o2",port=wg_bottom.ports["o2"])
    c.flatten()
    return c
#生成器件Sbend
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s
@gf.cell
def Sbend(
    width: float = 0.5,
    dy: Delta = 4.0,
    dx: Delta = 10.0,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""生成s型弯曲波导
    Args:
        width:弯曲波导的宽度。
        dy:波导到波导y方向上的距离。
        dx:弯曲波导x方向上的长度。
        cross_section:横截面类型，一般无需修改。
    .. code::
                    dx
               |----------|
                       ___ o3 (width)
                      /       |
             o2 _____/        |dy
    """
    c = Component()
    x = gf.get_cross_section(cross_section,width=width)
    width1 = x.width
    dy = (dy - width1)
    bend_component = gf.get_component(
        bend_s,
        size=(dx, dy),
        cross_section=x,
    )
    top_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name
    c.add_port("o1", port=top_bend[bend_port1_name])
    c.add_port("o2", port=top_bend[bend_port2_name])
    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]
    return c
#生成器件star_coupler
import gdsfactory as gf
from gdsfactory.component import Component
from csufactory.generic_tech.layer_map import CSULAYER as LAYER
from gdsfactory.boolean import boolean
from gdsfactory.typings import CrossSectionSpec
import numpy as np
@gf.cell
def star_coupler(
    num_ports: int = 10,  # 波导数量
    body_size: tuple[float, float] = (2.5, 4),  # 椭圆主耦合区域 a和b轴
    waveguide_length: float = 3,  # 波导的长度
    waveguide_width: float = 0.5,  # 波导的宽度
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """生成一个星型耦合器（star coupler），采用从中心发散的波导。
    Args:
        num_ports: 波导的数量。必须为偶数!
        body_size: 中心区域（圆形）的半径。
        waveguide_length: 波导的长度。
        waveguide_width: 波导的宽度。
        cross_section: 横截面类型，不建议修改。
    """
    layer=LAYER.WG
    c = gf.Component()
    body1 = gf.components.ellipse(radii=body_size, layer=layer)
    body2 = gf.components.ellipse(radii=(body_size[0] + 1, body_size[1] + 1), layer=layer)
    temp = gf.Component()
    num_2 = num_ports / 2
    if num_ports <= 2:
        angles = [0, 180]
    elif 2 < num_ports and num_2 % 2 == 0:
        angles = []
        nums = num_ports // 2
        for i in range(nums):
            angle_offset = 180 / nums
            angle_0=0 + (0.5+nums/2-1) * angle_offset
            angle_180 = 180 - (0.5+nums/2-1) * angle_offset
            angles.append(angle_0 - angle_offset * i)
            angles.append(angle_180 + angle_offset * i)
    else:
        angles = [0, 180]
        nums = num_ports // 4
        for i in range(1, nums + 1):
            angle_offset = 160 / (num_ports // 2) * i
            angles.append(0 + angle_offset)
            angles.append(0 - angle_offset)
            angles.append(180 + angle_offset)
            angles.append(180 - angle_offset)
    angles = [angle % 360 for angle in angles]
    angles = sorted(list(set(angles)))
    for i, angle in enumerate(angles):
        angle_rad = np.radians(angle)
        x_start = body_size[0] / 2 * np.cos(angle_rad)
        y_start = body_size[1] / 2 * np.sin(angle_rad)
        x_end = (body_size[0] / 2 + waveguide_length) * np.cos(angle_rad)
        y_end = (body_size[1] / 2 + waveguide_length) * np.sin(angle_rad)
        x = gf.get_cross_section(cross_section, width=waveguide_width)
        wg = temp << gf.components.straight(
            length=waveguide_length,
            cross_section=x,
        )
        wg.dmove((x_start, y_start))
        wg.drotate(angle, center=(x_start, y_start))
        temp.add_port(
            name=f"o{i+1}",
            center=(x_end, y_end),
            width=waveguide_width,
            orientation=angle,
            layer=layer,
        )
    merged = boolean(temp, body1, operation="or", layer=layer)
    final = boolean(merged, body2, operation="and", layer=layer)
    c << final
    c.flatten()
    c.add_port(
        name=f"o1",
        center=(-body_size[0] - 1+0.005, 0),
        width=waveguide_width,
        orientation=180,
        layer=layer,
    )
    c.add_port(
        name=f"o2",
        center=(body_size[0] + 1-0.005, 0),
        width=waveguide_width,
        orientation=0,
        layer=layer,
    )
    print(f"最终角度分布: {angles}")
    return c
#生成器件wg_arc
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec
from gdsfactory.components.bend_circular import _bend_circular
@gf.cell
def wg_arc(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: gf.typings.LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
) -> Component:
    """生成圆弧。
    Args:
        radius: 半径，默认为圆环横截面类型的半径。
        angle: 圆弧旋转的角度.
        npoints: 点的数量，调整精度的一般无需修改.
        layer: 层，一般无需修改，默认为横截面类型对应的层“WG”。
        width: 圆弧波导的宽度，外环半径与内环半径的插值，默认为横截面类型的宽度。
        cross_section:横截面类型，一般无需修改。
        allow_min_radius_violation: 如果为True,则允许半径小于横截面类型对应的半径，一般无需修改。
    """
    # 强制类型转换和验证
    try:
        radius = float(radius) if radius is not None else None
        angle = float(angle) if angle is not None else 90.0
        if width is not None:
            width = float(width)
    except (ValueError, TypeError) as e:
        raise ValueError(f"参数类型错误: {str(e)}") from e
    # 参数验证
    if radius is not None and radius <= 0:
        raise ValueError(f"半径必须是正数，当前为 {radius}")
    return _bend_circular(
        radius=radius,
        angle=angle,
        npoints=npoints,
        layer=layer,
        width=width,
        cross_section=cross_section,
        allow_min_radius_violation=allow_min_radius_violation,
        all_angle=False,
    )
#生成器件ybranch
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s
@gf.cell
def ybranch(
    width: float = 1,
    length: float = 10,
    gap: float = 0,
    dy: Delta = 10,
    dx: Delta = 20,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""生成y_branch.
    Args:
        gap:y分支间隙（um），不建议修改。
        width:起始段直波导y方向上的长度。
        length:起始段直波导x方向上的长度。
        dy:o2-o3两个端口之间y方向上的距离。
        dx:y分支在x方向上的长度。
        cross_section: 横截面类型，不建议修改。
    .. code::
                       dx
                 /--------------|
                            ___ o2
           length         /       |
（ width）o1_____o4_______/        |dy
                         \        |
                          \___    |
                                   o3
    """
    c = Component()
    width1=width/2
    x = gf.get_cross_section(cross_section, width=width1)
    dy_ = (dy - gap - width1) / 2
    bend_component=bend_s(size=(dx, dy_),cross_section=x,)
    top_bend = c << bend_component
    bot_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name
    w = bend_component[bend_port1_name].dwidth
    y = w + gap
    y /= 2
    bot_bend.dmirror_y()
    top_bend.dmovey(+y)
    bot_bend.dmovey(-y)
    port1=bot_bend[bend_port1_name]
    port2=top_bend[bend_port1_name]
    x_new = (port1.center[0] + port2.center[0]) / 2
    y_new = (port1.center[1] + port2.center[1]) / 2
    c.add_port(
        name="o4",
        center=(x_new, y_new),
        orientation=port1.orientation,
        width=2*w,
        layer=port1.layer
    )
    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]
    x_straight = gf.get_cross_section(cross_section, width=width)
    wg_input = c << gf.components.straight(length=length, cross_section=x_straight)
    wg_input.connect("o1", c.ports["o4"])
    c.add_port("o1", port=wg_input.ports["o2"])
    c.add_port("o2", port=top_bend[bend_port2_name])
    c.add_port("o3", port=bot_bend[bend_port2_name])
    c.flatten()
    return c
#生成器件Ybranch_1x2
from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec
@gf.cell(check_instances=False)
def Ybranch_1x2(
    length1: float = 8,
    length2: float = 7,
    length3: float = 1,
    bend_radius: float = 10,
    width: float = 0.5,
    angle1: float = 30,
    angle2: float = 30,
    cross_section: CrossSectionSpec = "strip",  # 这里是直接使用字符串来表示交叉截面
    allow_min_radius_violation: bool = False,
) -> Component:
    r"""生成y分支.
    Args:
        length1: 第一段输入波导在x方向上的长度.
        length2: 中间段波导在x方向上的长度.
        length3: 输出波导在x向上的长度.
        bend_radius:第一段弯曲波导的半径.
        width:波导的宽度（x）。
        angle1: 第一段分支的角度.
        angle2: 第二段分支的角度.
        cross_section: 横截面类型，不建议修改。
        allow_min_radius_violation: 如果为TRUE,则不检查最小半径，无需修改.
    .. code::
                                                 length3
                                               ______ o2
                                              /
                                 length1     /
                         o1 -----------------  (width)
                                      length2\
                                              \_______ o3
    """
    c = gf.Component()
    wg_input = c << gf.components.straight(length=length1, width=width,cross_section=cross_section)
    bend_left1 = c << gf.components.bend_euler(angle=angle1, radius=bend_radius, width=width,cross_section=cross_section)
    bend_right1 = c << gf.components.bend_euler(angle=-angle1, radius=bend_radius, width=width,cross_section=cross_section)
    wg_left1 = c << gf.components.straight(length=length2, width=width,cross_section=cross_section)
    wg_right1 = c << gf.components.straight(length=length2, width=width,cross_section=cross_section)
    bend_left2 = c << gf.components.bend_euler(angle=-angle2, radius=bend_radius, width=width,cross_section=cross_section)
    bend_right2 = c << gf.components.bend_euler(angle=angle2, radius=bend_radius, width=width,cross_section=cross_section)
    wg_left2 = c << gf.components.straight(length=length3, width=width,cross_section=cross_section)
    wg_right2 = c << gf.components.straight(length=length3, width=width,cross_section=cross_section)
    bend_left1.connect("o1", wg_input.ports["o2"])
    bend_right1.connect("o1", wg_input.ports["o2"])
    wg_left1.connect("o1", bend_left1.ports["o2"])
    wg_right1.connect("o1", bend_right1.ports["o2"])
    bend_left2.connect("o1", wg_left1.ports["o2"])
    bend_right2.connect("o1", wg_right1.ports["o2"])
    wg_left2.connect("o1", bend_left2.ports["o2"])
    wg_right2.connect("o1", bend_right2.ports["o2"])
    c.add_port("o1", port=wg_input.ports["o1"])
    c.add_port("o2", port=wg_left2.ports["o2"])
    c.add_port("o3", port=wg_right2.ports["o2"])
    c.auto_rename_ports()
    x = gf.get_cross_section(cross_section)
    x.add_bbox(c)
    c.flatten()
    if not allow_min_radius_violation:
        x.validate_radius(x.radius)
    return c
#定义工艺参数
nm = 1e-3
class LayerStackParameters:
    """用于层栈和工艺"""
    wafer_diameter: float = 150000
    thickness_substrate_Si: float = 625
    thickness_substrate_Quartz: float = 1000
    thickness_bottom_clad: float = 15
    thickness_wg_zp45: float = 6.5
    thickness_wg_zp75: float = 6
    thickness_wg_150: float = 4.5
    sidewall_angle_wg: float = 0
    thickness_wgn: float = 6.5
    sidewall_angle_wgn: float = 0
    thickness_slab_deep_etch: float = 90 * nm
    thickness_slab_shallow_etch: float = 150 * nm
    thickness_top_clad: float = 20
    thickness_full_etch = thickness_wg_zp45 + 1
    thickness_deep_etch = thickness_wg_zp45 - thickness_slab_deep_etch
    thickness_shallow_etch = thickness_wg_zp45 - thickness_slab_shallow_etch
    thickness_metal_TiN: float = round(200 * nm, 10)
    thickness_heater_clad: float = 2
    thickness_metal_Ti: float = round(1400 * nm, 10)
    thickness_metal_Al: float = round(700 * nm, 10)
    thickness_SiN: float = round(300 * nm, 10)
#定义层
import gdsfactory as gf
Layer = tuple[int, int]
class CSULAYER(gf.LayerEnum):
    """ CSUPDK层映射定义 """
    layout = gf.constant(gf.kcl.layout)
    Si_Sub: Layer = (88, 0)
    SiO_Bottom_Clad: Layer = (87, 0)
    WG: Layer = (200, 0)
    WGN: Layer = (201, 0)
    Full_Etch: Layer = (1, 2)
    SLAB90: Layer = (2, 1)
    Deep_Etch: Layer = (2, 2)
    SLAB150: Layer = (3, 1)
    Shallow_Etch: Layer = (3, 2)
    Wet_Etch_Heater: Layer = (5, 2)
    Dry_Etch_Heater_Clad: Layer = (6, 2)
    Wet_Etch_Electrode: Layer = (7, 2)
    Full_Etch_SiN: Layer = (8, 2)
    SiO_ToP_Clad: Layer = (4, 0)
    Metal_TiN: Layer = (10, 0)
    SiO_Oxide_1: Layer = (11, 0)
    Metal_Ti: Layer = (12, 0)
    Metal_Al: Layer = (13, 0)
    SiN: Layer = (20, 0)
    NWD: Layer = (30, 0)
    PWD: Layer = (31, 0)
    ND1: Layer = (32, 0)
    PD1: Layer = (33, 0)
    ND2: Layer = (34, 0)
    PD2: Layer = (35, 0)
    ND_Ohmic: Layer = (36, 0)
    PD_Ohmic: Layer = (37, 0)
    Label_Optical_IO: Layer = (95, 0)
    Label_Settings: Layer = (96, 0)
    TXT: Layer = (97, 0)
    DA: Layer = (98, 0)
    DecRec: Layer = (99, 0)
    TE: Layer = (203, 0)
    TM: Layer = (204, 0)
    PORT: Layer = (140, 10)
    PORTE: Layer = (140, 11)
#定义层栈
import gdsfactory as gf
import datetime
from functools import partial
from csufactory.generic_tech.layer_map import CSULAYER as LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from csufactory.generic_tech.layer_stack import LayerStackParameters as Para
from csufactory.components.awg import free_propagation_region
from csufactory.components.awg import awg
nm = 1e-3
#定义器件
c = gf.Component()
Si_Sub = c << gf.components.rectangle(size=(100, 100), layer=(88, 0))
BOX = c << gf.components.rectangle(size=(100, 100), layer=(87, 0))
SiO_ToP_Clad = c << gf.components.rectangle(size=(100, 100), layer=(4, 0))
Metal_Ti = c << gf.components.rectangle(size=(100, 100), layer=(12, 0))
csu_awg= c << awg(
    inputs= 1,
    arms= 9,
    outputs= 3,
    free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
    free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
    fpr_spacing= 50.0,
    arm_spacing= 1.0,
)
csu_awg.movex(25)
csu_awg.movey(35)
heater_etch_1 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_1.movex(20)
heater_etch_2 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_2.movex(47.5)
heater_etch_3 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_3.movex(75)
heater_clad_etch_1 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_1.movex(25)
heater_clad_etch_2 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_2.movex(30+45/2)
wet_etch_electrode = c << gf.components.rectangle(size=(8, 100), layer=(7, 2))
wet_etch_electrode.movex(88)
full_etch_SiN = c << gf.components.rectangle(size=(5, 100), layer=(8, 2))
full_etch_SiN.movex(89.5)
#定义层
layer_Si_Sub = LogicalLayer(layer=LAYER.Si_Sub)
layer_box = LogicalLayer(layer=LAYER.SiO_Bottom_Clad)
layer_core = LogicalLayer(layer=LAYER.WG)
layer_full_etch = LogicalLayer(layer=LAYER.Full_Etch)
layer_top_clad = LogicalLayer(layer=LAYER.SiO_ToP_Clad)
layer_metal_TiN = LogicalLayer(layer=LAYER.Metal_TiN)
layer_wet_etch_heater = LogicalLayer(layer=LAYER.Wet_Etch_Heater)
layer_heater_clad = LogicalLayer(layer=LAYER.SiO_Oxide_1)
layer_dry_etch_heater_clad = LogicalLayer(layer=LAYER.Dry_Etch_Heater_Clad)
layer_metal_Ti = LogicalLayer(layer=LAYER.Metal_Ti)
layer_metal_Al = LogicalLayer(layer=LAYER.Metal_Al)
layer_wet_etch_electrode = LogicalLayer(layer=LAYER.Wet_Etch_Electrode)
layer_SiN = LogicalLayer(layer=LAYER.SiN)
layer_full_etch_SiN = LogicalLayer(layer=LAYER.Full_Etch_SiN)
#定义层栈
Si_zp45_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence":2.00E-04,
                "PDL": 0.2,
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 15,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp45,
            thickness_tolerance=2,
            zmin=0,
            material="sio2",
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
Quartz_zp45_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Quartz,
            zmin=-Para.thickness_substrate_Quartz-Para.thickness_bottom_clad,
            material="Quartz",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence":2.00E-04,
                "PDL": 0.2,
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 15,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp45,
            thickness_tolerance=2,
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
zp45_GDS= LayerStack(
        layers={
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
    }
)
Si_zp75_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "PDL": 0.3,
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp75,
            thickness_tolerance=2,
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
Quartz_zp75_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Quartz,
            zmin=-Para.thickness_substrate_Quartz-Para.thickness_bottom_clad,
            material="Quartz",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "PDL": 0.3,
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp75,
            thickness_tolerance=2,
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
zp75_GDS= LayerStack(
        layers={
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
    }
)
Si_150_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence_max":1.5e-4,
                "Birefringence_min":3e-5,
                "PDL": 0.4,
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.5,
                "CD_bias_tolerance": 0.2,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=10,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_150,
            thickness_tolerance=0.3,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":5.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.467,
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness= 15 + Para.thickness_wg_zp75,
            thickness_tolerance=3,
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 1.5,
            }
        ),
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
z150_GDS= LayerStack(
        layers={
         "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_150,
            thickness_tolerance=0.3,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":5.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.467,
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,
                    "solver": "FDTD"
                }
        }
        ),
    }
)
import os
def export_layer_stack_info(
        layer_stack_name: str = "Si_zp45_LayerStack",
        output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",
        percent: float = 0.45,
        file_prefix: str = "LayerStack"
) -> None:
    """
    导出层栈信息到文本文件
    参数:
        layer_stack_name: 层栈变量名 (默认: "Si_zp45_LayerStack")
        output_dir: 输出目录路径 (默认: CSU_PDK参数目录)
        percent: 折射率变化百分比 (默认: 0.45)
        file_prefix: 输出文件名前缀 (默认: "LayerStack")
    返回:
        None (结果直接保存到文件)
    """
    # 动态获取层栈对象
    layer_stack = globals().get(layer_stack_name)
    if layer_stack is None:
        raise ValueError(f"未找到层栈定义: {layer_stack_name}")
    # 构建输出文件路径
    output_filename = f"{file_prefix}_{percent * 100:.0f}percent.txt"
    output_path = os.path.join(output_dir, output_filename)
    # 创建输出目录(如果不存在)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        # 写入文件头
        print(f"将{layer_stack_name}中的主要参数，保存至下方文件内")
        f.write(f"Design Rules for {percent * 100:.2f}% Delta N index (um)\n")
        f.write("\t\tParameter\n")
        # 写入基底(substrate)信息
        if 'substrate' in layer_stack.layers:
            for key, value in layer_stack.layers['substrate'].info.items():
                f.write(f"{key}: {value}\n")
        # 写入各层信息
        f.write("\nlayer_stack_parameter\n")
        for layer_name, layer in layer_stack.layers.items():
            f.write(f"\nLayerName: {layer_name}:\n")
            f.write(f"\tThickness: {layer.thickness},\n")
            f.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
            f.write(f"\tMaterial: {layer.material},\n")
            f.write(f"\tZmin: {layer.zmin},\n")
            f.write(f"\tDerivedLayer: {layer.derived_layer}\n")
            if layer_name != "substrate" and layer.info:
                        f.write("\tInfo:\n")
                        for key, value in layer.info.items():
                            f.write(f"\t\t{key}: {value}\n")
        print(f"TXT文件已保存至: {output_path}")
import datetime
def save_gds(component,
             component_name:str=None,
             output_gds_path=None,
             ):
    """保存组件到GDS文件"""
    if component_name is None:
        component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        component_name = component_name
    if output_gds_path is None:
        output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    else:
        output_gds_path = output_gds_path
    component.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
#测试layer_map
from csufactory.generic_tech.layer_map import CSULAYER
def test_layer_map():
    assert CSULAYER.get_layer("WG") == (200, 0)
    assert CSULAYER.get_layer("Metal_Al") == (13, 0)
    assert CSULAYER.get_layer("MOPT") is None  # 不存在的层应返回 None
if __name__ == "__main__":
    test_layer_map()
    print("LayerMap 测试通过！")
if __name__ == "__main__":
    # 生成layer.lyp和tech.lyt文件，用于klayout中层的显示。
    from gdsfactory.technology import LayerViews
    layer_views_path = "C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml"
    layer_lyp_path = "C:\Windows\System32\CSU_PDK\csufactory\generic_tech\klayout\salt\layer.lyp"
    LAYER_VIEWS = LayerViews(filepath=layer_views_path)
    print(f"已从{layer_views_path}中获取层信息")
    LAYER_VIEWS.to_lyp(filepath=layer_lyp_path)
    print(f"将层信息转为lyp文件保存至{layer_lyp_path}")
    #生成每层的预览图
    c = LAYER_VIEWS.preview_layerset()
    c.show()
if __name__ == "__main__":
    #运行用户交互函数
    from csufactory.dialoge import run
    run()
from csufactory.generic_tech.layer_map import CSULAYER
def test_layer_map():
    assert CSULAYER.get_layer("WG") == (200, 0)
    assert CSULAYER.get_layer("Metal_Al") == (13, 0)
    assert CSULAYER.get_layer("MOPT") is None  # 不存在的层应返回 None
if __name__ == "__main__":
    test_layer_map()
    print("LayerMap 测试通过！")



# #定义layer_view的.yaml文件,用于生成.lyp和.lyt文件。
# LayerViews:
#   Si_Sub:
#     layer: [88, 0]
#     layer_in_name: true
#     hatch_pattern: coarsely dotted
#     width: 1
#     color: "cyan"
#   SiO_Bottom_Clad:
#     layer: [87, 0]
#     layer_in_name: true
#     hatch_pattern: strongly right-hatched dense
#     transparent: true
#     width: 1
#     color: "springgreen"
#   WG:
#     layer: [200, 0]
#     layer_in_name: true
#     hatch_pattern: strongly left-hatched sparse
#     transparent: true
#     width: 1
#     color: "#ff9d9d"
#   WGN:
#     layer: [201, 0]
#     layer_in_name: true
#     hatch_pattern: lightly left-hatched
#     transparent: true
#     width: 1
#     color: "royalblue"
#   Full_Etch:
#     layer: [1, 2]
#     layer_in_name: true
#     hatch_pattern: hollow
#     transparent: true
#     width: 1
#     color: "deeppink"
#   SLAB90:
#     layer: [2, 1]
#     layer_in_name: true
#     hatch_pattern: dotted
#     width: 1
#     color: "dodgerblue"
#   Deep_Etch:
#     layer: [2, 2]
#     layer_in_name: true
#     hatch_pattern: hollow
#     transparent: true
#     width: 1
#     color: "dodgerblue"
#   SLAB150:
#     layer: [3, 1]
#     layer_in_name: true
#     hatch_pattern: dotted
#     width: 1
#     color: "gold"
#   Shallow_Etch:
#     layer: [3, 2]
#     layer_in_name: true
#     hatch_pattern: hollow
#     transparent: true
#     width: 1
#     color: "gold"
#   SiO_ToP_Clad:
#     layer: [4, 0]
#     layer_in_name: true
#     hatch_pattern: coarsely dotted
#     width: 1
#     color: "lightcoral"
#   Wet_Etch_Heater:
#     layer: [5, 2]
#     layer_in_name: true
#     hatch_pattern: vertical dense
#     width: 1
#     color: "thistle"
#   Metal_TiN:
#     layer: [10, 0]
#     layer_in_name: true
#     hatch_pattern: solid
#     transparent: true
#     width: 1
#     color: "yellow"
#   Dry_Etch_Heater_Clad:
#     layer: [6, 2]
#     layer_in_name: true
#     hatch_pattern: vertical dense
#     width: 1
#     color: "teal"
#   SiO_Oxide_1:
#     layer: [11, 0]
#     layer_in_name: true
#     hatch_pattern: left-hatched
#     color: "#cc0000"
#   Wet_Etch_Electrode:
#     layer: [7, 2]
#     layer_in_name: true
#     hatch_pattern: vertical dense
#     width: 1
#     color: "greenyellow"
#   Metal_Al:
#     layer: [12, 0]
#     layer_in_name: true
#     hatch_pattern: solid
#     width: 1
#     color: "lightsteelblue"
#   Metal_Ti:
#     layer: [13, 0]
#     layer_in_name: true
#     hatch_pattern: solid
#     width: 1
#     color: "#e1ffff"
#   Full_Etch_SiN:
#     layer: [8, 2]
#     layer_in_name: true
#     hatch_pattern: vertical dense
#     width: 1
#     color: "#ee1490"
#   SiN:
#     layer: [20, 0]
#     layer_in_name: true
#     hatch_pattern: turned pyramids
#     width: 1
#     color: "magenta"
#   Doping:
#     group_members:
#       NWD:
#         layer: [30, 0]
#         layer_in_name: true
#         frame_color: "red"
#         fill_color: "red"
#         hatch_pattern: lightly left-hatched
#         width: 1
#       PWD:
#         layer: [31, 0]
#         layer_in_name: true
#         frame_color: "blue"
#         fill_color: "blue"
#         hatch_pattern: lightly left-hatched
#         transparent: true
#         width: 1
#       ND1:
#         layer: [32, 0]
#         layer_in_name: true
#         frame_color: "red"
#         fill_color: "red"
#         hatch_pattern: strongly right-hatched dense
#         width: 1
#       PD1:
#         layer: [33, 0]
#         layer_in_name: true
#         frame_color: "blue"
#         fill_color: "blue"
#         hatch_pattern: strongly right-hatched dense
#         width: 1
#       ND2:
#         layer: [34, 0]
#         layer_in_name: true
#         frame_color: "red"
#         fill_color: "red"
#         hatch_pattern: coarsely dotted
#         width: 1
#       PD2:
#         layer: [35, 0]
#         layer_in_name: true
#         frame_color: "blue"
#         fill_color: "blue"
#         hatch_pattern: coarsely dotted
#         width: 1
#       ND_Ohmic:
#         layer: [36, 0]
#         layer_in_name: true
#         frame_color: "khaki"
#         fill_color: "khaki"
#         hatch_pattern: plus
#         width: 1
#       PD_Ohmic:
#         layer: [37, 0]
#         layer_in_name: true
#         frame_color: "sandybrown"
#         fill_color: "sandybrown"
#         hatch_pattern: plus
#         width: 1
#   TE:
#     layer: [203, 0]
#     layer_in_name: true
#     transparent: true
#     width: 1
#     color: "blue"
#   TM:
#     layer: [204, 0]
#     layer_in_name: true
#     width: 1
#     color: "red"
#   PORT:
#     layer: [140, 10]
#     layer_in_name: true
#     transparent: true
#     width: 1
#     color: "magenta"
#   PORTE:
#     layer: [140, 11]
#     layer_in_name: true
#     width: 1
#     color: "#cc4c00"
#   Label_Optical_IO:
#     layer: [95, 0]
#     layer_in_name: true
#     hatch_pattern: hollow
#     width: 1
#     color: "blue"
#   Label_Settings:
#     layer: [96, 0]
#     layer_in_name: true
#     hatch_pattern: hollow
#     width: 1
#     color: "magenta"
#   TXT:
#     layer: [97, 0]
#     layer_in_name: true
#     hatch_pattern: hollow
#     width: 1
#     color: "grey"
#   DA:
#     layer: [98, 0]
#     layer_in_name: true
#     hatch_pattern: coarsely dotted
#     width: 1
#     color: "#01ff6b"
#     brightness: -16
#   DevRec:
#     layer: [99, 0]
#     layer_in_name: true
#     hatch_pattern: hollow
#     visible: false
#     transparent: true
#     width: 1
#     color: "#004080"
#   Errors:
#     layer: [69, 0]
#     layer_in_name: true
#     hatch_pattern: hollow
#     width: 1
#     color: "grey"
#   DRC_MARKER:
#     layer: [205, 0]
#     layer_in_name: true
#     transparent: true
#     width: 3
#     color: "red"
#   MOPT:
#     layer: [9999, 0]
#     layer_in_name: true
#     hatch_pattern: strongly right-hatched dense
#     transparent: true
#     width: 1
#     color: "#8400ff"