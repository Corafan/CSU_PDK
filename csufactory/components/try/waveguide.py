from csufactory.component import Component
from csufactory.generic_tech.layer_map_csu import CSULAYER

def waveguide(
        length: float = 0.5,
        width: float =10,
        layer= CSULAYER.WG,
    )-> Component:
    """ 创建一个简单的波导组件
    参数:
        length: 浮点数,长度,横着的.
        width:浮点数,宽度,竖着的.
        layer:元组,层,
    """
    c = Component(name="waveguide")
    # 添加波导结构
    points = [(0, 0), (length, 0), (length, width), (0, width)]
    c.add_polygon(points, layer=layer)
    center = (length / 2, width / 2)
    # 添加端口
    if length > width:
        c.add_ports("input", position=(0, width / 2), width=width, orientation=180)
        c.add_ports("output", position=(length, width / 2), width=width, orientation=0)
    elif length < width:
        c.add_ports("input", position=(length / 2, 0), width=length, orientation=90)
        c.add_ports("output", position=(length / 2, width), width=length, orientation=270)
    return c

if __name__ == "__main__":
    c = waveguide(width=5,length=20)
    c.rotate(90)
    # c.move(8,8)
    # c.movex(2)
    c.show()
    print(c.ports)

