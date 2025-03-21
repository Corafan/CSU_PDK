Layer = tuple[int, int]

class CSULAYER:
    """ CSUPDK 层映射定义 """\
    
    Si_Sub = (88, 0)
    SiO_Bottom_Clad = (87,0)

    WG = (200,0)             #波导waveguide，材料是Si
    WGN = (201, 0)           #非线性波导Waveguide Nonlinear 
    
    #第二种表达方式：WG: Layer= (200,0)    

    # #备选部分
    # Slab_Full_Etch = (1,1)     #全刻蚀部分
    # Slab_Deep_Etch = (1,2)     #深刻蚀部分
    # Slab_Shallow_Etch = (1,3)  #浅刻蚀部分

    # #需要考虑这部分是否只留一个Clad，又称Core、芯层、镀层
    Full_Etch = (1,2)        #全刻蚀部分full
    SLAB90 = (2,1)           #深刻蚀完剩余部分,slab90
    Deep_Etch = (2,2)        #深刻蚀部分deep
    SLAB150 = (3,1)          #浅刻蚀完剩余部分,slab150
    Shallow_Etch = (3,2)     #浅刻蚀部分shallow

    Wet_Etch_Heater = (5,2) 
    Dry_Etch_Heater_Clad = (6,2) 
    Wet_Etch_Electrode = (7,2) 
    Full_Etch_SiN = (8,2) 

    SiO_ToP_Clad = (4,0)
    Metal_TiN = (10,0)       #Heater!
    SiO_Oxide_1 = (11,0)
    Metal_Ti = (12,0)        #Metal1
    Metal_Al = (13,0)        #Metal2
    SiN = (20,0)


    #Dopping：
    NWD = (30,0)
    PWD = (31,0)
    ND1 = (32,0)
    PD1 = (33,0)
    ND2 = (34,0)
    PD2 = (35,0)
    ND_Ohmic = (36,0)
    PD_Ohmic = (37,0)

    #中间还可以任意添加层
    PORT = (1, 10)       #表示一般的光学输入/输出端口，通常用于光信号的连接。
                                #如，一个光波导的起点和终点，或者一个分光器的输入和输出端口。
    PORTE = (1, 11)      #表示电气端口，主要用于电信号的传输，通常与电气控制器件相连接。
                                #如用于控制光调制器、加热器或其他需要电信号驱动的光学元件。
    #注释部分：
    Label_Optical_IO = (95,0)
    Label_Settings = (96,0)
    TXT = (97,0)
    DA = (98,0)
    DecRec = (99,0)

    # classmethod 是一个类型注解丰富的类，模拟了 Python 内置的 classmethod 装饰器的行为。
    # 它通过泛型和类型注解提供了更详细的类型信息，使得在使用时可以获得更好的类型检查和代码提示。
    @classmethod
    def get_layer(cls, name):
        """ 获取层定义 """
        return getattr(cls, name, None)

