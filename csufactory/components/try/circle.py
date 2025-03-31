import numpy as np
from numpy import cos, sin, pi

from csufactory.component import Component
from csufactory.generic_tech.layer_map_csu import CSULAYER


def circle(
        radius: float =10, 
        angle_resolution: float = 2.5, 
        layer=CSULAYER.WG,
    )-> Component:
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
    c.show()