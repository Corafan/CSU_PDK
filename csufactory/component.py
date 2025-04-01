import gdstk
import subprocess
import os
import socket
import json
import datetime
import numpy as np
import math
from typing import List, Literal
from csufactory.generic_tech.layer_map_csu import CSULAYER

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
        # print(f"移动前: {[polygon.points for polygon in self.cell.polygons]}")
        # 平移所有多边形
        for polygon in self.cell.polygons:
            polygon.translate(dx, dy)

        # 平移所有端口
        for port_name, port_data in self.ports.items():
            x, y = port_data["position"]
            port_data["position"] = (x + dx, y + dy)
        # print(f"移动后: {[polygon.points for polygon in self.cell.polygons]}")

    def move_to(
            self,
            destination: tuple,
            current_position: tuple
    ):
        """
        将组件移动到指定位置(以组件原点为基准)

        参数:
            position: 新的原点位置 (x, y)
        """
        # 计算需要移动的量
        dx = destination[0] - current_position[0]
        dy = destination[1] - current_position[1]

        print(f"当前坐标: {current_position}, 目标坐标: {destination}, 平移量: ({dx}, {dy})")
        # 调用平移方法
        self.move(dx,dy)

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

    def connect(self, port1_name: str, component2, port2_name: str, connection_length: float = None):
        """
        连接两个组件的端口

        参数:
            port1_name: 当前组件的端口名
            component2: 要连接的另一个组件
            port2_name: 另一个组件的端口名
            connection_length: 可选，指定连接波导的长度
                            None表示直接连接(端口对齐)
        """
        # 获取端口信息
        port1 = self.ports.get(port1_name)
        port2 = component2.ports.get(port2_name)

        if not port1 or not port2:
            raise ValueError("指定的端口不存在")

        # 提取端口位置和方向
        x1, y1 = port1["position"]
        x2, y2 = port2["position"]
        angle1 = port1["orientation"]
        angle2 = port2["orientation"]

        # 检查端口方向是否匹配(相差180度)
        if (angle1 - angle2) % 180 != 0:
            print(f"警告: 端口方向不匹配 ({angle1}° 和 {angle2}°)")

        # 计算连接类型
        if connection_length is None:
            # 直接连接 - 移动component2使其端口对齐
            if angle1 == 0:  # 向右
                dx = x1 - x2
                dy = y1 - y2
            elif angle1 == 180:  # 向左
                dx = x1 - x2
                dy = y1 - y2
            elif angle1 == 90:  # 向下
                dx = x1 - x2
                dy = y1 - y2
            elif angle1 == 270:  # 向上
                dx = x1 - x2
                dy = y1 - y2
            component2.move(dx, dy)
        else:
            # 使用指定长度的波导连接
            if angle1 == 0:  # 向右
                start_point = (x1, y1)
                end_point = (x1 + connection_length, y1)
            elif angle1 == 180:  # 向左
                start_point = (x1, y1)
                end_point = (x1 - connection_length, y1)
            elif angle1 == 90:  # 向下
                start_point = (x1, y1)
                end_point = (x1, y1 - connection_length)
            elif angle1 == 270:  # 向上
                start_point = (x1, y1)
                end_point = (x1, y1 + connection_length)

            # 添加连接波导
            width = port1["width"]
            self.add_polygon([
                (start_point[0], start_point[1] - width / 2),
                (end_point[0], end_point[1] - width / 2),
                (end_point[0], end_point[1] + width / 2),
                (start_point[0], start_point[1] + width / 2)
            ], layer=port1["layer"])

            # 移动component2使端口对齐
            if angle1 == 0:  # 向右
                dx = end_point[0] - x2
                dy = end_point[1] - y2
            elif angle1 == 180:  # 向左
                dx = end_point[0] - x2
                dy = end_point[1] - y2
            elif angle1 == 90:  # 向下
                dx = end_point[0] - x2
                dy = end_point[1] - y2
            elif angle1 == 270:  # 向上
                dx = end_point[0] - x2
                dy = end_point[1] - y2
            component2.move(dx, dy)

    def boolean_operation(self, other, operation="union", layer=None):
        """
        执行布尔操作(并集、交集、差集)

        参数:
            other: 另一个Component对象
            operation: "union"(并集), "intersection"(交集), "difference"(差集)
            layer: 结果多边形的层，None表示使用第一个多边形的层
        """
        # 获取所有多边形
        polygons1 = self.cell.polygons
        polygons2 = other.cell.polygons

        if not polygons1 or not polygons2:
            raise ValueError("至少有一个组件没有多边形")

        # 确定结果层
        result_layer = layer if layer is not None else polygons1[0].layer

        # 收集所有多边形
        all_polygons1 = [poly for poly in polygons1]
        all_polygons2 = [poly for poly in polygons2]

        # 执行布尔操作
        if operation == "union":
            result = gdstk.boolean(all_polygons1, all_polygons2, "or")
        elif operation == "intersection":
            result = gdstk.boolean(all_polygons1, all_polygons2, "and")
        elif operation == "difference":
            result = gdstk.boolean(all_polygons1, all_polygons2, "not")
        else:
            raise ValueError(f"未知的布尔操作: {operation}")

        # 清除原有多边形并添加结果
        self.cell.polygons.clear()
        for poly in result:
            if isinstance(poly, gdstk.Polygon):
                self.add_polygon(poly.points, layer=result_layer)
            else:
                # 处理其他可能的返回类型
                for p in poly:
                    self.add_polygon(p.points, layer=result_layer)

        return self

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


if __name__ == "__main__":

    # c = Component(name="waveguide_with_ports")
    # c.add_polygon([(0, 0), (0.5, 0), (0.5, 10), (0, 10)], layer=CSULAYER.WG)
    #
    # # 添加端口并生成三角形
    # c.add_ports("input", position=(0.25, 0), width=0.5, orientation=90)  # 端口朝向左
    # c.add_ports("output", position=(0.25, 10), width=0.5, orientation=270)  # 端口朝向右
    #
    # # 导出并查看 GDS 文件
    # c.show()

    # # 创建两个组件
    # c1 = Component(name="waveguide1")
    # c1.add_polygon([(0, 0), (10, 0), (10, 5), (0, 5)], layer=CSULAYER.WG)
    # c1.add_polygon([(5, 2), (15, 2), (15, 7), (5, 7)])
    # c1.show()

    # 创建两个组件
    comp1 = Component("component1")
    comp2 = Component("component2")

    # 添加一些多边形
    comp1.add_polygon([(0, 0), (10, 0), (10, 5), (0, 5)], layer=CSULAYER.WG)
    comp2.add_polygon([(5, 2), (15, 2), (15, 7), (5, 7)], layer=CSULAYER.WG)

    # 2. 布尔操作示例
    result = comp1.boolean_operation(comp2,"union")  # 并集
    # 或者:
    # result = comp1.difference(comp2)  # 差集
    # result = comp1.intersection(comp2)  # 交集

    # 显示结果
    result.show()