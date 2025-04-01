from csufactory.component import Component
from csufactory.generic_tech.layer_map_csu import CSULAYER

def waveguide(
        length: float = 0.5,
        width: float =10,
        layer= CSULAYER.WG,
        center: tuple = (0, 0),
    )-> Component:
    """ 创建一个简单的波导组件
    参数:
        length: 浮点数,长度,横着的.
        width:浮点数,宽度,竖着的.
        layer:元组,层,
    """
    c = Component(name="waveguide")
    # 添加波导结构
    x=center[0]
    y=center[1]
    points = [(x-length/2, y-width/2), (x-length/2, y+width/2), (x+length/2, y+width/2), (x+length/2, y-width/2)]
    c.add_polygon(points, layer=layer)
    # 添加端口
    if length > width:
        c.add_ports("input", position=(x-length/2, y), width=width, orientation=180)
        c.add_ports("output", position=(x+length/2,y), width=width, orientation=0)
    elif length < width:
        c.add_ports("input", position=(x, y-width/2), width=length, orientation=90)
        c.add_ports("output", position=(x, y+width/2), width=length, orientation=270)
    return c

if __name__ == "__main__":
    c = waveguide(width=10,length=0.5)
    c.rotate(90)
    c.move(8,8)
    c.rotate(-90,center=(8,8))
    # c.movex(2)
    # c.movey(2)
    c.move_to((0,0),(8,8))
    c.show()
    print(c.ports)

