from csufactory.csupdk.layer_map import CSULAYER as LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from csufactory.technology.processes import (
    Anneal,
    Etch,
    Grow,
    ImplantPhysical,
    Planarize,
    ProcessStep,
)

nm = 1e-3

class LayerStackParameters:
    """values used by get_layer_stack and get_process."""
    """用于层栈和工艺"""

    #0.45%,Si衬底。后续核对(问号表示待定)：
    thickness_substrate: float = 625                   #基板厚度um
    thickness_bottom_clad: float = 15                  #下包层——镀层厚度um
    thickness_wg: float = 6.5                          #波导层厚度(core)
    sidewall_angle_wg: float = 0                       #侧壁倾斜角度
    thickness_wgn: float = 6.5                         #非线性波导层厚度(core)？这个目前不需要
    sidewall_angle_wgn: float = 0                      #侧壁倾斜角度
    thickness_slab_deep_etch: float = 90 * nm          #深刻蚀，刻蚀深度130nm？
    thickness_slab_shallow_etch: float = 150 * nm      #浅刻蚀，刻蚀深度70nm？
    thickness_top_clad: float = 20                     #上包层——镀层厚度um

    thickness_full_etch = thickness_wg + 1                                #全刻蚀深度
    thickness_deep_etch = thickness_wg - thickness_slab_deep_etch         #深刻蚀深度？
    thickness_shallow_etch = thickness_wg - thickness_slab_shallow_etch   #浅刻蚀深度？

    thickness_metal_TiN: float = round(200 * nm, 10)   #TiN加热层厚度
    #zmin_heater: float = 1.1                          #位置?
    thickness_heater_clad: float = 2                   #加热层TiN的氧化层um
    thickness_metal_Ti: float = round(1400 * nm, 10)   #间隔层厚度
    #zmin_metal_Ti: float = 1.1                        #位置?
    thickness_metal_Al: float = round(700 * nm, 10)    #电极层Al的厚度：？
    #zmin_metal_Al: float = 2.3                        #位置?
    thickness_SiN: float = round(300 * nm, 10)         #保护层SiN厚度


#层栈：存储多个 LayerLevel，形成整个芯片的 3D 层叠结构，包含每层属性
def get_layer_stack(
    thickness_substrate: float = LayerStackParameters.thickness_substrate,
    thickness_bottom_clad: float = LayerStackParameters.thickness_bottom_clad,    
    thickness_wg: float = LayerStackParameters.thickness_wg,
    sidewall_angle_wg: float = LayerStackParameters.sidewall_angle_wg,
    thickness_wgn: float = LayerStackParameters.thickness_wgn,
    sidewall_angle_wgn: float = LayerStackParameters.sidewall_angle_wgn,
    thickness_slab_deep_etch: float = LayerStackParameters.thickness_slab_deep_etch,
    thickness_slab_shallow_etch: float = LayerStackParameters.thickness_slab_shallow_etch,
    thickness_top_clad: float = LayerStackParameters.thickness_top_clad,  
    thickness_metal_TiN: float = LayerStackParameters.thickness_metal_TiN,
    #zmin_heater: float = LayerStackParameters.zmin_heater,
    thickness_heater_clad: float = LayerStackParameters.thickness_heater_clad,
    #zmin_metal_Ti: float = LayerStackParameters.zmin_metal_Ti,
    thickness_metal_Ti: float = LayerStackParameters.thickness_metal_Ti,
    #zmin_metal_Al: float = LayerStackParameters.zmin_metal_Al,
    thickness_metal_Al: float = LayerStackParameters.thickness_metal_Al,
    thickness_SiN: float = LayerStackParameters.thickness_SiN,

    thickness_full_etch: float = LayerStackParameters.thickness_full_etch,
    thickness_deep_etch: float = LayerStackParameters.thickness_deep_etch,
    thickness_shallow_etch: float = LayerStackParameters.thickness_shallow_etch,

    layer_Si_Sub: LogicalLayer = LogicalLayer(layer=LAYER.Si_Sub), 
    layer_box: LogicalLayer = LogicalLayer(layer=LAYER.SiO_Bottom_Clad), 
    layer_core: LogicalLayer = LogicalLayer(layer=LAYER.WG), 
    layer_core_wgn: LogicalLayer = LogicalLayer(layer=LAYER.WGN), 
    layer_full_etch: LogicalLayer = LogicalLayer(layer=LAYER.Full_Etch), 
    layer_slab_shallow_etch: LogicalLayer = LogicalLayer(layer=LAYER.SLAB150),
    layer_shallow_etch: LogicalLayer = LogicalLayer(layer=LAYER.Shallow_Etch),
    layer_slab_deep_etch: LogicalLayer = LogicalLayer(layer=LAYER.SLAB90),
    layer_deep_etch: LogicalLayer = LogicalLayer(layer=LAYER.Deep_Etch), 
    layer_wet_etch_heater: LogicalLayer = LogicalLayer(layer=LAYER.Wet_Etch_Heater),
    layer_dry_etch_heater_clad: LogicalLayer = LogicalLayer(layer=LAYER.Dry_Etch_Heater_Clad),
    layer_wet_etch_electrode: LogicalLayer = LogicalLayer(layer=LAYER.Wet_Etch_Electrode),
    layer_full_etch_SiN: LogicalLayer = LogicalLayer(layer=LAYER.Full_Etch_SiN),
    layer_top_clad: LogicalLayer = LogicalLayer(layer=LAYER.SiO_ToP_Clad),
    layer_metal_TiN: LogicalLayer = LogicalLayer(layer=LAYER.Metal_TiN),
    layer_heater_clad: LogicalLayer = LogicalLayer(layer=LAYER.SiO_Oxide_1),
    layer_metal_Ti: LogicalLayer = LogicalLayer(layer=LAYER.Metal_Ti),
    layer_metal_Al: LogicalLayer = LogicalLayer(layer=LAYER.Metal_Al),
    layer_SiN: LogicalLayer = LogicalLayer(layer=LAYER.SiN),
) -> LayerStack:
    """Returns generic LayerStack.

    based on paper https://www.degruyter.com/document/doi/10.1515/nanoph-2013-0034/html

    Args:
        thickness_substrate: substrate thickness in um.
        thickness_bottom_clad: bottom cladding thickness in um.
        thickness_wg: waveguide thickness in um.
        thickness_wng: waveguide thickness in um.
        
    
        thickness_slab_deep_etch: slab thickness after deep etch in um. equal to thickness of trench.
        thickness_slab_shallow_etch: slab thickness after shallow etch in um.
        thickness_top_clad: top cladding thickness in um.
        thickness_metal_TiN: metal TiN thickness.
        zmin_heater: TiN heater.
        thickness_heater_clad: heater cladding thickness in um.
        zmin_metal_Ti: metal Ti.
        thickness_metal_Ti: metal Ti thickness.
        zmin_metal_Al: metal Al.
        thickness_metal_Al: metal Al thickness.
        thickness_SiN: SiN thickness.

        layer_Si_Sub: substrate layer.
        layer_bottom_clad: SiO2 bottom cladding layer.
        layer_core: waveguide layer.
        layer_core_wng: waveguide layer. 
        layer_full_etch: full etch layer.
        layer_slab_deep_etch: deep etch slab layer.        
        layer_deep_etch: deep etch layer.      
        layer_slab_shallow_etch: shallow etch slab layer.
        layer_shallow_etch: shallow etch layer.
        layer_top_clad: SiO2 top cladding layer.
        layer_metal_TiN: heater TiN layer.
        layer_heater_clad: SiO2 heater cladding layer.
        layer_metal_Ti: metal Ti layer.
        layer_metal_Al: metal Al layer.
        layer_SiN: SiN layer for protection.
    """
    
    layers = dict(
        substrate=LayerLevel(
            layer=layer_Si_Sub,
            thickness=thickness_substrate,
            zmin=-thickness_substrate-thickness_bottom_clad,      
            material="silicon",
            mesh_order=101,                   #网格划分，数字小的优先，用于数值仿真
        ),
        box=LayerLevel(
            layer=layer_box,
            thickness=thickness_bottom_clad,  
            zmin=-thickness_bottom_clad,                          
            material="sio2",
            mesh_order=9,
            info={
                "refractive_index": 1.444,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
            }
        ),        
        core=LayerLevel(
            layer=layer_core - layer_full_etch - layer_deep_etch - layer_shallow_etch,
            #这层是由多个 GDS 层组合而成的物理派生层，通过计算得出最终层。第一层是核心层。
            thickness=thickness_wg,
            zmin=0,
            material="silicon",
            mesh_order=2,
            sidewall_angle=sidewall_angle_wg,
            width_to_z=0.5,
            derived_layer=LogicalLayer(layer=LAYER.WG),            #最终计算出来的层，映射到GDS的WG层
            info={
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
        core_wgn=LayerLevel(
            layer=layer_core_wgn - layer_full_etch - layer_deep_etch - layer_shallow_etch,
            thickness=thickness_wgn,
            zmin=0,
            material="silicon",
            mesh_order=2,
            sidewall_angle=sidewall_angle_wgn,
            width_to_z=0.5,
            derived_layer=LogicalLayer(layer=LAYER.WGN),
        ),
        shallow_etch=LayerLevel(
            layer=layer_shallow_etch & layer_core,    
            thickness=thickness_shallow_etch,
            zmin=0,
            material="silicon",
            mesh_order=1,
            derived_layer=LogicalLayer(layer=LAYER.SLAB150),
            #这部分，意思是core和shallow etch的重叠部分，最后由SLAB150从z=0长出来Si,相当于也是芯层。
        ),
        deep_etch=LayerLevel(
            layer=layer_deep_etch & layer_core, 
            thickness=thickness_deep_etch,
            zmin=0,
            material="silicon",
            mesh_order=1,
            derived_layer=LogicalLayer(layer=LAYER.SLAB90), 
        ),
        full_etch=LayerLevel(
            layer=layer_full_etch,
            thickness=thickness_full_etch,
            zmin=0,
            material="silicon",
            mesh_order=1,
        ),
        slab_shallow_etch=LayerLevel(              #slab150
            layer=layer_slab_shallow_etch,
            thickness=thickness_shallow_etch,
            zmin=0,
            material="silicon",
            mesh_order=2,
        ),
        slab_deep_etch=LayerLevel(                  #slab90
            layer=layer_slab_deep_etch,
            thickness=thickness_slab_deep_etch,
            zmin=0,
            material="silicon",
            mesh_order=3,
        ),
        wet_etch_heater=LayerLevel(                  
            layer=layer_wet_etch_heater,
            thickness=thickness_metal_TiN,
            zmin=thickness_wg + thickness_top_clad,
            material="TiN",
            mesh_order=4,
        ),
        dry_etch_heater_clad=LayerLevel(                  
            layer=layer_dry_etch_heater_clad,
            thickness=thickness_heater_clad,
            zmin=thickness_wg + thickness_top_clad,
            material="sio2",
            mesh_order=4,
        ),
        wet_etch_electrode=LayerLevel(                  
            layer=layer_wet_etch_electrode,
            thickness=thickness_metal_Al,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_metal_Ti,
            material="Aluminum",
            mesh_order=4,
        ),
        full_etch_SiN=LayerLevel(                  
            layer=layer_full_etch_SiN,
            thickness=thickness_SiN,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_heater_clad + thickness_metal_Ti,
            material="SiN",
            mesh_order=4,
        ),
        top_clad=LayerLevel(
            layer=layer_top_clad,                    
            zmin=0,                                        #？这部分还有待考量，分不同情况，看怎么安排
            material="sio2",
            thickness=thickness_top_clad,                  #+ thickness_wg？#同上
            mesh_order=10,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,                    # 单位 um
                    "solver": "FDTD"
                }
            }
        ),
        TiN=LayerLevel(                        
            layer=layer_metal_TiN,
            thickness=thickness_metal_TiN,                 
            zmin=thickness_wg + thickness_top_clad,
            material="TiN",
            mesh_order=2,
        ),
        heater_clad=LayerLevel(
            layer=layer_heater_clad,               
            zmin=thickness_wg + thickness_top_clad,       #因为这里只有一种情况，全刻蚀            
            material="sio2",
            thickness=thickness_heater_clad,              
            mesh_order=2,
        ),
        Ti=LayerLevel(
            layer=layer_metal_Ti,
            thickness=thickness_metal_Ti,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
        ),
        Al=LayerLevel(
            layer=layer_metal_Al,
            thickness=thickness_metal_Al,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_metal_Ti,          
            material="Aluminum",
            mesh_order=2,
        ),
        SiN=LayerLevel(
            layer=layer_SiN,
            thickness=thickness_SiN,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_heater_clad + thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
        ),
    )

    return LayerStack(layers=layers)


LAYER_STACK = get_layer_stack()

WAFER_STACK = LayerStack(
    layers={
        k: get_layer_stack().layers[k]
        for k in (
            "substrate",
            "box",
            "core",
            "top_clad",
            "TiN",
            "wet_etch_heater",
            "heater_clad",
            "Ti",
            "Al",
            "SiN",
        )
    }
)

#这部分前半段按照工艺流程的顺序来，后面是工艺类型的补充：
def get_process() -> tuple[ProcessStep, ...]:
    """Returns generic process to generate LayerStack.

    Represents processing steps that will result in the GenericLayerStack, starting from the waferstack LayerStack.

    """
    return (
        Grow(
            name="deposit_bottom_cladding",
            layer=LAYER.SiO_Bottom_Clad,
            thickness=LayerStackParameters.thickness_bottom_clad,
            material="SiO2_Oxide",
            type="isotropic",                                       #各向同性？有待商榷
            #rate= 0.1                                               #nm/s
        ),
        Grow(
            name="deposit_core_layer",
            layer=LAYER.WG,
            thickness=LayerStackParameters.thickness_wg,
            material="silicon",
            type="isotropic",                                       #各向同性？有待商榷
            #rate= 0.1                                               #nm/s
        ),
        #应分三段退火，时间未知
        Anneal(
            name="high_temperature_annealing",
            time=24,
            temperature=1200,
        ), 
        #掺杂工艺气体(掺杂部分放在后面了)
        #三层掩膜（Cr\SiO2\光刻胶）
        #刻蚀掩膜
        #去光刻胶

        #刻蚀芯层：这部分刻蚀应该分多种情况，目前只选全刻蚀（按照工艺流程图所示）
        Etch(
            name="full_etch_corelayer",                             #全刻蚀芯层
            layer=LAYER.WG,                                         #工艺作用在哪一层
            layers_and=[LAYER.Full_Etch],                           #（and交集）曝光区域（重合的地方）
            depth=LayerStackParameters.thickness_wg + 1,            #slight overetch for numerics 轻微刻深一点
            material="silicon",
            resist_thickness=1.0,                                   #光刻胶厚度？
            positive_tone=True,                                     #true代表正胶，曝光区域被刻蚀
            #rate= 0.1                                               #nm/s
        ),
        #去两层硬掩模
        Grow(
            name="deposit_top_cladding",
            layer=LAYER.SiO_ToP_Clad,
            thickness=LayerStackParameters.thickness_top_clad,
            material="SiO2_Oxide",
            type="anisotropic",
        ),
        #退火工艺未知
        Anneal(
            name="high_temperature_annealing",
            time=12,
            temperature=1000,
        ), 
        Grow(
            name="magnetron_sputtering_TiN",                         #磁控溅射，TiN
            layer=LAYER.Metal_TiN,
            thickness=LayerStackParameters.thickness_metal_TiN,
            material="Titanium_Nitride",
            type="anisotropic",
        ), 
        Etch(
            name="wet_etch_heater", 
            layer=LAYER.Metal_TiN,
            layers_and=[LAYER.Wet_Etch_Heater],
            depth=LayerStackParameters.thickness_metal_TiN,
            material="Titanium_Nitride",
            resist_thickness=1.0,
        ),
        Anneal(
            name="low_temperature_annealing",
            time=0.5,
            temperature=500,                                        #低温退火，致密化，温度待定？
        ), 
        Grow(
            name="PE_CVD_sputtering_heater_cladding", 
            layer=LAYER.SiO_Oxide_1,
            thickness=LayerStackParameters.thickness_heater_clad,
            material="SiO2_Oxide",
            type="anisotropic",
        ),
        Etch(
            name="dry_etch_heater_cladding", 
            layer=LAYER.SiO_Oxide_1,
            layers_and=[LAYER.Dry_Etch_Heater_Clad],     
            depth=LayerStackParameters.thickness_heater_clad,
            material="SiO2_Oxide",
            resist_thickness=1.0,
        ),  
        Grow(
            name="sputtering_Ti",                                    #金属化，Ti,种子层
            layer=LAYER.Metal_Ti,
            thickness=LayerStackParameters.thickness_metal_Ti,
            material="Titanium",
            type="anisotropic",
        ), 
        Grow(
            name="sputtering_Al",                                     #金属化，Al
            layer=LAYER.Metal_Al,
            thickness=LayerStackParameters.thickness_metal_Al,
            material="Aluminum",
            type="anisotropic",
        ),    
        Etch(
            name="wet_etch_electrode",
            layer=LAYER.Metal_Al,
            layers_and=[LAYER.Wet_Etch_Electrode],
            depth=LayerStackParameters.thickness_metal_Al,
            material="Aluminum",
            resist_thickness=1.0,
        ),
        Grow(
            name="PE_CVD_sputtering_SiN",
            layer=LAYER.SiN,
            thickness=LayerStackParameters.thickness_SiN,
            material="Silicon Nitride",
            type="anisotropic",
        ),   
        Etch(
            name="pad_openning",
            layer=LAYER.SiN,
            layers_and=[LAYER.Full_Etch_SiN],
            depth=LayerStackParameters.thickness_SiN,
            material="Silicon Nitride",
            resist_thickness=1.0,
        ),


        #芯层刻蚀补充：
        Etch(
            name="deep_etch_corelayer", 
            layer=LAYER.WG, 
            layers_and=[LAYER.SLAB150],  
            depth=LayerStackParameters.thickness_wg - LayerStackParameters.thickness_slab_deep_etch,
            material="silicon",
            resist_thickness=1.0,
            positive_tone=True, 
            #rate= 0.1                                               #nm/s
        ),
        Etch(
            name="shallow_etch_corelayer", 
            layer=LAYER.WG, 
            layers_and=[LAYER.SLAB90],  
            depth=LayerStackParameters.thickness_wg - LayerStackParameters.thickness_slab_shallow_etch,
            material="silicon",
            resist_thickness=1.0,
            positive_tone=True, 
            #rate= 0.1                                               #nm/s
        ),


        #掺杂部分,物理植入过程。将特定的离子（如磷离子）注入到硅等材料中，以改变材料的电学性质。
        #注意区分轻中重掺杂！！
        # See gplugins.process.implant tables for ballpark numbers
        # Adjust to your process

        #量子阱，轻掺
        ImplantPhysical(
            name="deep_NWD_implant",
            layer=LAYER.NWD,
            energy=100,                                 #指定离子的能量，单位通常是电子伏特（eV）
            ion="P",                                    #注入的离子种类，用于N型掺杂，"As",表示注入的是砷离子。
                                                        #"P",表示注入的是磷离子（Phosphorus）。磷离子通常用于掺杂硅以调节其导电性。
            dose=1e12,
                                                        #dose 参数表示注入的离子数量，单位通常是每单位面积的离子数量。这里设置为 1e12，即每单位面积注入 10的12次方个离子。
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="shallow_NWD_implant",
            layer=LAYER.NWD,
            energy=50,
            ion="P",
            dose=1e12,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="deep_PWD_implant",
            layer=LAYER.PWD,
            energy=50,
            ion="B",                                     #用于P型掺杂，"B",表示硼离子
                                                         #"Al",铝离子也可以用于P型掺杂
            dose=1e12,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="shallow_PWD_implant",
            layer=LAYER.PWD,
            energy=15,
            ion="B",
            dose=1e12,
            resist_thickness=1.0,
        ),

        #PN结，中掺
        ImplantPhysical(
            name="PD1_implant",
            layer=LAYER.PD1,
            energy=15,
            ion="B",
            dose=5e12,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="ND1_implant",
            layer=LAYER.ND1,
            energy=50,
            ion="P",
            dose=5e12,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="PD2_implant",
            layer=LAYER.PD2,
            energy=15,
            ion="B",
            dose=1e15,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="ND2_implant",
            layer=LAYER.ND2,
            energy=100,
            ion="As",
            dose=1e15,
            resist_thickness=1.0,
        ),

        #欧姆接触，重掺
            ImplantPhysical(
            name="PD_Ohmic_implant",
            layer=LAYER.ND_Ohmic,
            energy=15,
            ion="B",
            dose=1e15,
            resist_thickness=1.0,
        ),
        ImplantPhysical(
            name="ND_Ohmic_implant",
            layer=LAYER.PD_Ohmic,
            energy=100,
            ion="As",
            dose=1e15,
            resist_thickness=1.0,
        ),

        Planarize(
            name="planarization",
            height=LayerStackParameters.thickness_top_clad - LayerStackParameters.thickness_slab_deep_etch,
        ),
    )

if __name__ == "__main__":
    ls = get_layer_stack(thickness_substrate=50.0)
    ls = get_layer_stack()
    script = ls.get_klayout_3d_script()
    print(script)
    print(ls.get_layer_to_material())
    print(ls.get_layer_to_thickness())

    for layername, layer in WAFER_STACK.layers.items():
        print(layername, layer.thickness,layer.material,layer.info.get("refractive_index", "none"))
    
    process_steps = get_process()  # 获取制造步骤

    for step in process_steps:
        print(f"Processing step: {step.name}")


