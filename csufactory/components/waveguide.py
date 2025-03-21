import gdstk
from csufactory.component import Component
from csufactory.csupdk.layer_map import CSULAYER
from csufactory.show_gds import show
from csufactory.show_gds import export_gds



def waveguide(
        length: float = 10, 
        width: float = 0.5, 
        layer= CSULAYER.WG,
    ):
    """ 创建一个简单的波导组件 """
    c = Component(name="waveguide")
    points = [(0, 0), (length, 0), (length, width), (0, width)]
    c.add_polygon(points, layer=layer)
    return c

if __name__ == "__main__":
    c = waveguide()
    gds_path = export_gds(c, filename="waveguide.gds") 
    show(gds_path)

