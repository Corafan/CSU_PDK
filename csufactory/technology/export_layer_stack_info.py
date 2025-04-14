# import os
# def export_layer_stack_info(
#         layer_stack_name: str = "Si_zp45_LayerStack",
#         output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",
#         percent: float = 0.45,
#         file_prefix: str = "LayerStack"
# ) -> None:
#     """
#     导出层栈信息到文本文件
#     参数:
#         layer_stack_name: 层栈变量名 (默认: "Si_zp45_LayerStack")
#         output_dir: 输出目录路径 (默认: CSU_PDK参数目录)
#         percent: 折射率变化百分比 (默认: 0.45)
#         file_prefix: 输出文件名前缀 (默认: "LayerStack")
#     返回:
#         None (结果直接保存到文件)
#     """
#     # 动态获取层栈对象
#     layer_stack = globals().get(layer_stack_name)
#     if layer_stack is None:
#         raise ValueError(f"未找到层栈定义: {layer_stack_name}")
#     # 构建输出文件路径
#     output_filename = f"{file_prefix}_{percent * 100:.0f}percent.txt"
#     output_path = os.path.join(output_dir, output_filename)
#     # 创建输出目录(如果不存在)
#     os.makedirs(output_dir, exist_ok=True)
#     with open(output_path, "w", encoding="utf-8") as f:
#         # 写入文件头
#         print(f"将{layer_stack_name}中的主要参数，保存至下方文件内")
#         f.write(f"Design Rules for {percent * 100:.2f}% Delta N index (um)\n")
#         f.write("\t\tParameter\n")
#         # 写入基底(substrate)信息
#         if 'substrate' in layer_stack.layers:
#             for key, value in layer_stack.layers['substrate'].info.items():
#                 f.write(f"{key}: {value}\n")
#         # 写入各层信息
#         f.write("\nlayer_stack_parameter\n")
#         for layer_name, layer in layer_stack.layers.items():
#             f.write(f"\nLayerName: {layer_name}:\n")
#             f.write(f"\tThickness: {layer.thickness},\n")
#             f.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
#             f.write(f"\tMaterial: {layer.material},\n")
#             f.write(f"\tZmin: {layer.zmin},\n")
#             f.write(f"\tDerivedLayer: {layer.derived_layer}\n")
#             if layer_name != "substrate" and layer.info:
#                         f.write("\tInfo:\n")
#                         for key, value in layer.info.items():
#                             f.write(f"\t\t{key}: {value}\n")  #每个 info 参数换行
#         print(f"TXT文件已保存至: {output_path}")
# from csufactory.components.generate_Para.component_layer_stack import Si_zp75_LayerStack
# export_layer_stack_info("Si_zp475_LayerStack")

import os
from gdsfactory.pdk import LayerStack
def export_layer_stack_info(
        layer_stack: LayerStack,
        output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",#这里csu_pdk换成PLCPDK?
        percent: float = 0.45,
        file_prefix: str = "LayerStack"
) -> None:
    """
    导出层栈信息到文本文件
    参数:
        layer_stack: LayerStack 对象
        output_dir: 输出目录路径
        percent: 折射率变化百分比 (默认: 0.45)
        file_prefix: 输出文件名前缀 (默认: "LayerStack")
    返回:
        None (结果直接保存到文件)
    """
    # 构建输出文件路径
    output_filename = f"{file_prefix}_{percent * 100:.0f}percent.txt"
    output_path = os.path.join(output_dir, output_filename)
    # 创建输出目录(如果不存在)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        # 写入文件头
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
from csufactory.components.generate_Para.component_layer_stack import Si_zp75_LayerStack
if __name__ == "__main__":
    export_layer_stack_info(Si_zp75_LayerStack)
