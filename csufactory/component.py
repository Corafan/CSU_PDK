import gdstk
import subprocess
import os
import socket
import json
import datetime
import numpy as np
import math
from csufactory.generic_tech.layer_map_csu import CSULAYER

class Port:
    """ 端口类：定义器件的光学端口，包括位置、方向、层等信息 """

    def __init__(self, name, position, width, orientation, layer=CSULAYER.PORT):
        self.name = name
        self.position = np.array(position)  # 端口坐标
        self.width = width  # 波导宽度
        self.orientation = orientation  # 角度 (0: 右, 90: 上, 180: 左, 270: 下)
        self.layer = layer  # 端口层信息

    def __repr__(self):
        return f"Port(name={self.name}, pos={self.position}, width={self.width}, orient={self.orientation})"

class Component:
    def __init__(self, name="default"):
        self.name = name
        self.cell = gdstk.Cell(name)
        self.ports = {}  # 添加 ports 变量，用于存储端口信息

    # 输出gds文件到指定文件夹
    def export_gds(
            self,
            filename="output.gds",
            filepath=None,
    ):
        """导出并保存 GDS 文件，支持自定义路径"""
        if filepath is None:
            filepath = "C:/Windows/System32/CSU_PDK/csufactory/all_output_files/gds"
            # **确保 filepath 是目录**
        if os.path.isfile(filepath):
            raise ValueError(f"错误: `{filepath}` 是一个文件，而不是目录！")

        os.makedirs(filepath, exist_ok=True)  # 确保目录存在
        file_path = os.path.join(filepath, filename)  # 生成完整的文件路径
        lib = gdstk.Library()  # 创建 GDS 库
        # 如果使用 gdspy，这里改成 gdspy.Library()
        lib.add(self.cell)  # 添加 GDS 结构
        lib.write_gds(file_path)  # 保存 GDS 文件
        print(f"GDSII 文件存于: {file_path}")
        return file_path  # 返回文件路径，方便 `show()` 直接调用

    # 将gds文件同步到klayout
    def show(
            self,
            gdspath=None,
            keep_position=True
    ):
        """写入GDS文件并用klayout展示出来"""
        if gdspath is None:
            gdspath = "C:/Windows/System32/CSU_PDK/csufactory/all_output_files/gds"
            # **确保 gdspath 是目录**
        if os.path.isfile(gdspath):
            gdspath = os.path.dirname(gdspath)  # 只取目录部分

        os.makedirs(gdspath, exist_ok=True)  # 确保目录存在
        file_path = os.path.join(gdspath, f"{self.name}.gds")  # 生成 GDS 文件路径
        self.export_gds(filename=f"{self.name}.gds", filepath=gdspath)  # 先导出 GDS
        # 确保 `file_path` 是文件
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"无法找到 GDS 文件: {file_path}")

        if self is None:
            raise ValueError(
                "Component is None, make sure that your function returns the component"
            )
        # 时间戳：
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if not os.path.isfile(file_path):
            raise ValueError("{} does not exist".format(file_path))
        data = {
            "gds": os.path.abspath(file_path),
            "keep_position": keep_position,
        }
        data = json.dumps(data)
        try:
            conn = socket.create_connection(("127.0.0.1", 8082), timeout=0.5)
            data = data + "\n"
            data = data.encode() if hasattr(data, "encode") else data
            conn.sendall(data)
            conn.close()
            print(f"时间:{timestamp} |INFO|show:8814-klive : 加载文件: {file_path}")
        except socket.error:
            print("warning, could not connect to the klive server")
            pass

    def add_polygon(self, points, layer=CSULAYER.WG):

        """ 添加多边形到 GDS 结构，支持 (layer, datatype) """

        if isinstance(layer, tuple):  # 确保 layer 传入了 (层号, 数据类型)
            layer, datatype = layer
        else:
            datatype = 0              # 默认 datatype 为 0
        self.cell.add(gdstk.Polygon(points, layer=layer,datatype=datatype))

    def add_ports(
            self,
            name:str,
            position:tuple,
            width:float,
            orientation:float,
            layer=CSULAYER.PORT
    ):
        """ 添加端口，同时生成一个朝向的三角形 """
        self.ports[name] = {
            "position": position,
            "width": width,
            "orientation": orientation,
            "layer": layer
        }

        # 提取层号 (layer_number) 和数据类型 (datatype)
        layer_number, datatype = layer if isinstance(layer, tuple) else (layer, 0)


        # 基本参数：三角形的大小，基于端口宽度进行调整
        triangle_size = width*0.5  # 设置三角形大小（宽度的一部分）
        x , y = position

        width=width * 0.5
        # 计算三角形的位置和对齐方式
        if orientation == 0:  # 向右
            points = [(x + width, y), (x, y + triangle_size),
                      (x , y - triangle_size)]
        elif orientation == 180:  # 向左
            points = [(x - width, y), (x, y + triangle_size ),
                      (x, y - triangle_size )]
        elif orientation == 90:  # 向下
            points = [(x, y - width), (x - triangle_size , y ),
                      (x + triangle_size , y )]
        elif orientation == 270:  # 向上
            points = [(x, y + width), (x - triangle_size , y ),
                      (x + triangle_size , y )]

        # 添加三角形到 GDS
        self.add_polygon(points, layer=(layer_number, datatype))

    def move(self, dx: float, dy: float):
        """
        平移整个组件及其所有元素

        参数:
            dx: x方向的平移量
            dy: y方向的平移量
        """
        # 平移所有多边形
        for polygon in self.cell.polygons:
            polygon.translate(dx, dy)

        # 平移所有端口
        for port_name, port_data in self.ports.items():
            x, y = port_data["position"]
            port_data["position"] = (x + dx, y + dy)
    def movex(self, dx: float):
        """
        x方向平移整个组件及其所有元素

        参数:
            dx: x方向的平移量
        """
        # 平移所有多边形
        for polygon in self.cell.polygons:
            polygon.translate(dx,0)

        # 平移所有端口
        for port_name, port_data in self.ports.items():
            x, y = port_data["position"]
            port_data["position"] = (x + dx, y)

    def movey(self, dy: float):
        """
        y方向平移整个组件及其所有元素

        参数:
            dy: y方向的平移量
        """
        # 平移所有多边形
        for polygon in self.cell.polygons:
            polygon.translate(0,dy)

        # 平移所有端口
        for port_name, port_data in self.ports.items():
            x, y = port_data["position"]
            port_data["position"] = (x , y + dy)

    def rotate(self, angle: float, center=(0, 0)):
        """
        旋转整个组件及其所有元素

        参数:
            angle: 旋转角度(度)
            center: 旋转中心点 (x, y)
        """
        # 将角度转换为弧度
        angle_rad = math.radians(angle)

        # 旋转所有多边形
        for polygon in self.cell.polygons:
            polygon.rotate(angle_rad, center)

        # 旋转所有端口
        for port_name, port_data in self.ports.items():
            x, y = port_data["position"]
            # 计算相对于旋转中心的坐标
            x_rel = x - center[0]
            y_rel = y - center[1]
            # 应用旋转矩阵
            new_x = x_rel * math.cos(angle_rad) - y_rel * math.sin(angle_rad)
            new_y = x_rel * math.sin(angle_rad) + y_rel * math.cos(angle_rad)
            # 更新端口位置
            port_data["position"] = (new_x + center[0], new_y + center[1])
            # 更新端口方向
            port_data["orientation"] = (port_data["orientation"] + angle) % 360

    # def move_to(self, position: tuple):
    #     """
    #     将组件移动到指定位置(以组件原点为基准)
    #
    #     参数:
    #         position: 新的原点位置 (x, y)
    #     """
    #     # 计算当前原点(假设初始在(0,0))
    #     current_origin = (0, 0)
    #     # 计算需要移动的量
    #     dx = position[0] - current_origin[0]
    #     dy = position[1] - current_origin[1]
    #     # 调用平移方法
    #     self.move(dx,dy)

    def add_ref(self, component):
        """ 引用其他组件（嵌套） """
        ref = gdstk.Reference(component.cell)
        self.cell.add(ref)
        self.references.append(ref)

    def bbox(self):
        """ 计算器件边界框 (Bounding Box) """
        if not self.cell.polygons:
            return None
        all_points = np.vstack([poly.points for poly in self.cell.polygons])
        return np.min(all_points, axis=0), np.max(all_points, axis=0)


if __name__ == "__main__":
    c = Component(name="waveguide_with_ports")
    c.add_polygon([(0, 0), (0.5, 0), (0.5, 10), (0, 10)], layer=CSULAYER.WG)

    # 添加端口并生成三角形
    c.add_ports("input", position=(0.25, 0), width=0.5, orientation=90)  # 端口朝向左
    c.add_ports("output", position=(0.25, 10), width=0.5, orientation=270)  # 端口朝向右

    # 导出并查看 GDS 文件
    c.show()

