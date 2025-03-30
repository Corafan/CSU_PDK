import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec

@gf.cell
def waveguide(
    length: float = 10.0,
    width: float = 0.5,
    layer: LayerSpec = "WG",
) -> Component:
    """创建一个波导"""
    return gf.components.straight(length=length, width=width, layer=layer)

if __name__ == "__main__":
    c = waveguide()
    c.show()


@gf.cell
def bend(radius: float = 5.0, width: float = 0.5, layer: LayerSpec = "WG") -> Component:
    """创建一个弯曲波导"""
    return gf.components.bend_euler(radius=radius, width=width, layer=layer)

if __name__ == "__main__":
    c = bend()
    c.show()
