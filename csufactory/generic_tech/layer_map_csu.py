Layer = tuple[int, int]

class CSULAYER():              #gf.LayerEnum
    """ CSUPDK 层映射定义 """

    # 关于工艺流程的层，如下：
    Si_Sub: Layer = (88, 0)               #基板都是这一层,无论是Quartz还是Silicon
    SiO_Bottom_Clad: Layer = (87, 0)

    WG: Layer = (200, 0)  # 波导waveguide，材料是Si
    WGN: Layer = (201, 0)  # 非线性波导Waveguide Nonlinear

    # #备选部分
    # Slab_Full_Etch: Layer = (1,1)     #全刻蚀部分
    # Slab_Deep_Etch: Layer = (1,2)     #深刻蚀部分
    # Slab_Shallow_Etch: Layer = (1,3)  #浅刻蚀部分

    # #需要考虑这部分是否只留一个Clad，又称Core、芯层、镀层
    Full_Etch: Layer = (1, 2)  # 全刻蚀部分full
    SLAB90: Layer = (2, 1)  # 深刻蚀完剩余部分,slab90
    Deep_Etch: Layer = (2, 2)  # 深刻蚀部分deep
    SLAB150: Layer = (3, 1)  # 浅刻蚀完剩余部分,slab150
    Shallow_Etch: Layer = (3, 2)  # 浅刻蚀部分shallow

    Wet_Etch_Heater: Layer = (5, 2)
    Dry_Etch_Heater_Clad: Layer = (6, 2)
    Wet_Etch_Electrode: Layer = (7, 2)
    Full_Etch_SiN: Layer = (8, 2)

    SiO_ToP_Clad: Layer = (4, 0)
    Metal_TiN: Layer = (10, 0)  # Heater!
    SiO_Oxide_1: Layer = (11, 0)
    Metal_Ti: Layer = (12, 0)  # Metal1
    Metal_Al: Layer = (13, 0)  # Metal2
    SiN: Layer = (20, 0)

    # Dopping：
    NWD: Layer = (30, 0)
    PWD: Layer = (31, 0)
    ND1: Layer = (32, 0)
    PD1: Layer = (33, 0)
    ND2: Layer = (34, 0)
    PD2: Layer = (35, 0)
    ND_Ohmic: Layer = (36, 0)
    PD_Ohmic: Layer = (37, 0)

    # 中间还可以任意添加层

    # 注释部分：
    Label_Optical_IO: Layer = (95, 0)
    Label_Settings: Layer = (96, 0)
    TXT: Layer = (97, 0)
    DA: Layer = (98, 0)
    DecRec: Layer = (99, 0)

    # 延续前一部分的（用于generic_tech.__init__部分）：
    TE: Layer = (203, 0)
    TM: Layer = (204, 0)
    PORT: Layer = (140, 10)  # 表示一般的光学输入/输出端口，通常用于光信号的连接。
    # 如，一个光波导的起点和终点，或者一个分光器的输入和输出端口。
    PORTE: Layer = (140, 11)  # 表示电气端口，主要用于电信号的传输，通常与电气控制器件相连接。
    # 如用于控制光调制器、加热器或其他需要电信号驱动的光学元件。
    # 不确定部分，via通孔(层数未修改)：
    # VIAC: Layer = (40, 0)
    # VIA1: Layer = (44, 0)
    #
    # # 用于（components.die_with_pads）：
    # FLOORPLAN: Layer = (64, 0)
    #
    # MTOP: Layer = (9999, 0)  # ?



    # classmethod 是一个类型注解丰富的类，模拟了 Python 内置的 classmethod 装饰器的行为。
    # 它通过泛型和类型注解提供了更详细的类型信息，使得在使用时可以获得更好的类型检查和代码提示。
    @classmethod
    def get_layer(cls, name):
        """ 获取层定义 """
        return getattr(cls, name, None)

