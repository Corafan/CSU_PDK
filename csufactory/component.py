import gdstk
import subprocess
import os
from csufactory.csupdk.layer_map import CSULAYER

class Component:
    def __init__(self, name="default"):
        self.name = name
        self.cell = gdstk.Cell(name)
    
    def add_polygon(self, points, layer=CSULAYER.WG):

        """ 添加多边形到 GDS 结构，支持 (layer, datatype) """

        if isinstance(layer, tuple):  # 确保 layer 传入了 (层号, 数据类型)
            layer, datatype = layer
        else:
            datatype = 0              # 默认 datatype 为 0
        self.cell.add(gdstk.Polygon(points, layer=layer,datatype=datatype))

    
    #之前是把export_gds放于component.py下面，后面改成show_gds.py了
    # #输出gds文件到指定文件夹
    # def export_gds(
    #         self, 
    #         filename="output.gds", 
    #         directory="C:\Windows\System32\csufactory\output_gds"
    #     ):
    #     """导出并保存 GDS 文件，支持自定义路径"""
    #     # 确保目录存在
    #     os.makedirs(directory, exist_ok=True)
    #     # 生成完整的文件路径
    #     file_path = os.path.join(directory, filename)
    #     # 创建 GDS 库
    #     lib = gdstk.Library()  
    #     # 如果使用 gdspy，这里改成 gdspy.Library()
    #     # 添加 GDS 结构
    #     lib.add(self.cell)
    #     # 保存 GDS 文件
    #     lib.write_gds(file_path)
    #     print(f"GDSII file saved at: {file_path}")

    #     # #这一步是想要联合klayout，但是失败了，后续再看
    #     # # 打开 KLayout 显示 GDS
    #     # try:
    #     #     subprocess.run(["klayout", file_path], check=True)
    #     # except FileNotFoundError:
    #     #     print("Error: KLayout is not installed or not in PATH.")           



