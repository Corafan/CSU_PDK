if __name__ == "__main__":
    from csufactory.dialoge import run
    run()




































































#
    # from csufactory.dialoge import export_layer_stacks
    # export_layer_stacks()
#
# import os
# from typing import Dict, Any
#
#
# def export_layer_stacks(
#         layer_stacks: Dict[str, Any] = None,
#         output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",
#         combined_filename: str = "CSU_LayerStack.txt"
# ) -> None:
#     """
#     导出层栈信息到文件
#
#     参数:
#         layer_stacks: 字典 {百分比字符串: 层栈对象}
#                      例: {"0.45%": Si_zp45_LayerStack}
#         output_dir: 输出目录路径
#         combined_filename: 合并文件名
#     """
#     # 设置默认层栈
#     if layer_stacks is None:
#         try:
#             from csufactory.components.generate_Para.component_layer_stack import (
#                 Si_zp45_LayerStack,
#                 Si_zp75_LayerStack,
#                 Si_150_LayerStack
#             )
#             layer_stacks = {
#                 "0.45%": Si_zp45_LayerStack,
#                 "0.75%": Si_zp75_LayerStack,
#                 "1.5%": Si_150_LayerStack
#             }
#         except ImportError as e:
#             print(f"错误: 无法导入默认层栈 - {str(e)}")
#             return
#
#     # 确保输出目录存在
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 判断是否为单个层栈
#     if len(layer_stacks) == 1:
#         # 单个层栈处理
#         percent_str, stack = next(iter(layer_stacks.items()))
#         _export_single_stack(percent_str, stack, output_dir)
#     else:
#         # 多个层栈处理
#         _export_multiple_stacks(layer_stacks, output_dir, combined_filename)
#
#
# def _export_single_stack(percent_str: str, stack: Any, output_dir: str):
#     """导出单个层栈"""
#     filename = f"LayerStack_{percent_str.replace('%', 'percent')}.txt"
#     path = os.path.join(output_dir, filename)
#
#     with open(path, "w", encoding="utf-8") as f:
#         _write_stack_content(f, percent_str, stack)
#
#     print(f"TXT文件已保存至: {path}")
#
#
# def _export_multiple_stacks(layer_stacks: Dict[str, Any], output_dir: str, combined_filename: str):
#     """导出多个层栈"""
#     combined_path = os.path.join(output_dir, combined_filename)
#
#     with open(combined_path, "w", encoding="utf-8") as combined_file:
#         print("将CSU_LayerStack中的主要参数，保存至下方文件内")
#
#         for percent_str, stack in layer_stacks.items():
#             # 写入合并文件
#             _write_stack_content(combined_file, percent_str, stack)
#
#             # 生成单独文件
#             _export_single_stack(percent_str, stack, output_dir)
#
#     print(f"\n合并文件已保存至: {combined_path}")
#
#
# def _write_stack_content(file_obj, percent_str: str, stack: Any):
#     """将层栈内容写入文件对象"""
#     file_obj.write(f"\n===== {percent_str} =====\n")
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
#
# export_layer_stacks()

#单个or全部单独导出：
# def export_single_layer_stack(
#         layer_stack: Any,
#         percent_str: str,
#         output_dir: str,
#         file_prefix: str = "LayerStack"
# ) -> str:
#     """导出单个层栈到文本文件"""
#     filename = f"{file_prefix}_{percent_str.replace('%', 'percent')}.txt"
#     filepath = os.path.join(output_dir, filename)
#
#     with open(filepath, "w", encoding="utf-8") as f:
#         # 写入文件头
#         f.write(f"Design Rules for {percent_str} Delta N index (um)\n")
#         f.write("\t\tParameter\n")
#
#         # 写入基底(substrate)信息
#         if hasattr(layer_stack, 'layers') and 'substrate' in layer_stack.layers:
#             substrate = layer_stack.layers['substrate']
#             if hasattr(substrate, 'info'):
#                 for key, value in substrate.info.items():
#                     f.write(f"{key}: {value}\n")
#
#         # 写入各层信息
#         for layer_name, layer in layer_stack.layers.items():
#             f.write(f"\nLayerName: {layer_name}:\n")
#             f.write(f"\tThickness: {layer.thickness},\n")
#             f.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
#             f.write(f"\tMaterial: {layer.material},\n")
#             f.write(f"\tZmin: {layer.zmin},\n")
#             f.write(f"\tDerivedLayer: {layer.derived_layer}\n")
#
#             # 写入额外info信息
#             if layer_name != "substrate" and getattr(layer, 'info', None):
#                 f.write("\tInfo:\n")
#                 for key, value in layer.info.items():
#                     f.write(f"\t\t{key}: {value}\n")
#     print(f"层栈文件已保存至: {filepath}")
#     return filepath

# if choice == "L":  # 导出层栈
#     try:
#         from csufactory.components.generate_Para.component_layer_stack import (
#             Si_zp45_LayerStack,
#             Si_zp75_LayerStack,
#             Si_150_LayerStack
#         )
#
#         # 定义可导出的层栈
#         available_stacks = {
#             "0.45%": Si_zp45_LayerStack,
#             "0.75%": Si_zp75_LayerStack,
#             "1.5%": Si_150_LayerStack
#         }
#
#         # 让用户选择要导出的层栈
#         print("\n可选层栈列表:")
#         for i, (percent, _) in enumerate(available_stacks.items(), 1):
#             print(f"{i}. {percent}")
#         print("A. 导出全部")
#
#         stack_choice = input("请选择要导出的层栈(数字或A): ").strip().upper()
#
#         output_dir = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter"
#         os.makedirs(output_dir, exist_ok=True)
#
#         if stack_choice == "A":
#             for percent, stack in available_stacks.items():
#                 export_single_layer_stack(stack, percent, output_dir)
#         elif stack_choice.isdigit() and 0 < int(stack_choice) <= len(available_stacks):
#             percent = list(available_stacks.keys())[int(stack_choice) - 1]
#             export_single_layer_stack(available_stacks[percent], percent, output_dir)
#         else:
#             print("无效选择")
#
#     except ImportError as e:
#         print(f"无法导入层栈: {str(e)}")
#
#     continue  # 返回操作菜单

