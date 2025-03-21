import numpy as np
from numpy import cos, sin, pi

from csufactory.component import Component
from csufactory.csupdk.layer_map import CSULAYER 
from csufactory.show_gds import show
from csufactory.show_gds import export_gds


def circle(
        radius: float =10, 
        angle_resolution: float = 2.5, 
        layer=CSULAYER.WG,):
    """ 生成一个简单的圆.

    参数:
        radius: 浮点数, 圆的半径。
        angle_resolution: 浮点数，环的曲线分辨率（每个点的度数）。
    """

    c = Component(name="circle")
    t = np.linspace(0, 360, int(360 / angle_resolution) + 1) * pi / 180
    xpts = radius * cos(t)
    ypts = radius * sin(t)
    # 将 xpts 和 ypts 组合成 (x, y) 对的列表
    points = list(zip(xpts, ypts))

    c.add_polygon(points=points, layer=layer)
    return c


if __name__ == "__main__":
    c = circle()
    gds_path = export_gds(c, filename="circle.gds") 
    show(gds_path)