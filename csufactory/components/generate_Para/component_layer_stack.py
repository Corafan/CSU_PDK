import gdsfactory as gf
import datetime
from functools import partial

from csufactory.generic_tech.layer_map import CSULAYER as LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from csufactory.technology.get_klayout_3d_script import get_klayout_3d_script
from csufactory.generic_tech.layer_stack import LayerStackParameters as Para
from csufactory.components.awg import free_propagation_region
from csufactory.components.awg import awg
from csufactory.components.MMI import mmi
nm = 1e-3


c = gf.Component()

#阵列波导光栅AWG（0.45%，Si基板）：
Si_Sub = c << gf.components.rectangle(size=(100, 100), layer=(88, 0))
BOX = c << gf.components.rectangle(size=(100, 100), layer=(87, 0))
SiO_ToP_Clad = c << gf.components.rectangle(size=(100, 100), layer=(4, 0))
Metal_Ti = c << gf.components.rectangle(size=(100, 100), layer=(12, 0))

#芯层:
#芯层AWG
csu_awg= c << awg(
    inputs= 1,
    arms= 9,                                       #阵列波导数量
    outputs= 3,
    free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
    free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
    fpr_spacing= 50.0,                            #输入/输出FPR的间距
    arm_spacing= 1.0,                             #阵列波导间距
)
#这部分LayerSpec是WG，所以层数为（200，0）=layer_core
csu_awg.movex(25)
csu_awg.movey(35)

#芯层MMI
# csu_mmi= c << mmi()
# csu_mmi.movex(25)
# csu_mmi.movey(50)


#刻蚀层
heater_etch_1 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_1.movex(20)
heater_etch_2 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_2.movex(47.5)
heater_etch_3 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_3.movex(75)
heater_clad_etch_1 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_1.movex(25)
heater_clad_etch_2 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_2.movex(30+45/2)
wet_etch_electrode = c << gf.components.rectangle(size=(8, 100), layer=(7, 2))
wet_etch_electrode.movex(88)
full_etch_SiN = c << gf.components.rectangle(size=(5, 100), layer=(8, 2))
full_etch_SiN.movex(89.5)

#定义所需各层：
layer_Si_Sub = LogicalLayer(layer=LAYER.Si_Sub)                                         
layer_box = LogicalLayer(layer=LAYER.SiO_Bottom_Clad)                                 
layer_core = LogicalLayer(layer=LAYER.WG)              #这部分实际对应的是器件的形状 
layer_full_etch = LogicalLayer(layer=LAYER.Full_Etch)  #全刻蚀形状还是COUPLER，只不过最后派生成了FullEtch  
layer_top_clad = LogicalLayer(layer=LAYER.SiO_ToP_Clad)                                          
layer_metal_TiN = LogicalLayer(layer=LAYER.Metal_TiN)
layer_wet_etch_heater = LogicalLayer(layer=LAYER.Wet_Etch_Heater)   
layer_heater_clad = LogicalLayer(layer=LAYER.SiO_Oxide_1)       
layer_dry_etch_heater_clad = LogicalLayer(layer=LAYER.Dry_Etch_Heater_Clad) 
layer_metal_Ti = LogicalLayer(layer=LAYER.Metal_Ti) 
layer_metal_Al = LogicalLayer(layer=LAYER.Metal_Al) 
layer_wet_etch_electrode = LogicalLayer(layer=LAYER.Wet_Etch_Electrode) 
layer_SiN = LogicalLayer(layer=LAYER.SiN) 
layer_full_etch_SiN = LogicalLayer(layer=LAYER.Full_Etch_SiN) 

#Si基板，0.45%，layerStack:
Si_zp45_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence":2.00E-04,
                "PDL": 0.2,  # 偏振损耗
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 15,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,  
            zmin=-Para.thickness_bottom_clad,                          
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ), 
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
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
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp45,   # + thickness_wg_zp45？#同上
            thickness_tolerance=2,
            zmin=0,
            material="sio2",
            mesh_order=10,
            # derived_layer=layer_top_clad,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            } 
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(                        
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,                 
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,       #因为这里只有一种情况，全刻蚀
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        #这部分是否要再加 布尔操作???
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            # derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)

#Quartz基板，0.45%，layerStack:
Quartz_zp45_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Quartz,
            zmin=-Para.thickness_substrate_Quartz-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence":2.00E-04,
                "PDL": 0.2,  # 偏振损耗
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 15,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
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
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp45,         #+ thickness_wg_zp45？#同上
            thickness_tolerance=2,
            mesh_order=10,
            # derived_layer=layer_top_clad,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad,       #因为这里只有一种情况，全刻蚀
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        #这部分是否要再加 布尔操作???
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            # derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp45 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)

#直波导，不加电极：
zp45_GDS= LayerStack(
        layers={
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp45,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch": 7.5,
                "core_etch_tolerance": -0.5,
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
    }
)

#Si基板，0.75%，layerStack:
Si_zp75_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "PDL": 0.3,  # 偏振损耗
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp75,         #+ thickness_wg_zp45？#同上
            thickness_tolerance=2,
            mesh_order=10,
            # derived_layer=layer_top_clad,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,       #因为这里只有一种情况，全刻蚀
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        #这部分是否要再加 布尔操作???
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            # derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)

#Quartz基板，0.75%，layerStack:
Quartz_zp75_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Quartz,
            zmin=-Para.thickness_substrate_Quartz-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "PDL": 0.3,  # 偏振损耗
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.4,
                "CD_bias_tolerance": 0.1,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=Para.thickness_bottom_clad,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness=Para.thickness_top_clad + Para.thickness_wg_zp75,         #+ thickness_wg_zp45？#同上
            thickness_tolerance=2,
            mesh_order=10,
            # derived_layer=layer_top_clad,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
            }
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,       #因为这里只有一种情况，全刻蚀
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        #这部分是否要再加 布尔操作???
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            # derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)

#直波导，不加电极：
zp75_GDS= LayerStack(
        layers={
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_zp75,
            thickness_tolerance=0.5,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":7.0,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.4,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
    }
)

#Si基板，1.5%，layerStack:
Si_150_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=Para.thickness_substrate_Si,
            zmin=-Para.thickness_substrate_Si-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=101,
            info={
                "wafer_diameter": Para.wafer_diameter,
                "Birefringence_max":1.5e-4,   #3.0e-5~1.5e-4(取中间值)
                "Birefringence_min":3e-5,
                "PDL": 0.4,  # 偏振损耗
                "Min_line_width": 1.5,
                "Min_spacing": 1.5,
                "CD_bias": 0.5,
                "CD_bias_tolerance": 0.2,
                "Min_bend_radius": 12,
            }
        ),
        "box":LayerLevel(
            layer=layer_box,
            thickness=10,
            zmin=-Para.thickness_bottom_clad,
            material="silicon",
            mesh_order=9,
            # derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
            }
        ),
        "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_150,
            thickness_tolerance=0.3,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":5.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.467,
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
        "top_clad":LayerLevel(
            layer=layer_top_clad,
            zmin=0,
            material="sio2",
            thickness= 15 + Para.thickness_wg_zp75,         #+ thickness_wg_zp45？#同上
            thickness_tolerance=3,
            mesh_order=10,
            # derived_layer=layer_top_clad,
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 1.5,
            }
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=Para.thickness_metal_TiN,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad,       #因为这里只有一种情况，全刻蚀
            material="sio2",
            thickness=Para.thickness_heater_clad + Para.thickness_metal_TiN,
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        #这部分是否要再加 布尔操作???
        "Ti":LayerLevel(
            layer=layer_metal_Ti,
            thickness=Para.thickness_metal_Ti + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            # derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode,
            thickness=Para.thickness_metal_Al + Para.thickness_heater_clad,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_metal_Ti,
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=Para.thickness_SiN + Para.thickness_metal_Al,
            zmin=Para.thickness_wg_zp75 + Para.thickness_top_clad + Para.thickness_metal_TiN + Para.thickness_heater_clad + Para.thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)
#直波导，不加电极：
z150_GDS= LayerStack(
        layers={
         "core":LayerLevel(
            layer=layer_core,
            thickness=Para.thickness_wg_150,
            thickness_tolerance=0.3,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "core_etch":5.5,
                "core_etch_tolerance": -0.5,
                "refractive_index": 1.467,
                "uniformity_of_index": 0.0015,
                "uniformity_of_thickness": 0.15,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ),
    }
)

CSU_LayerStacks = {
    "0.45": Si_zp45_LayerStack,
    "0.75%": Si_zp75_LayerStack,
    "1.5%": Si_150_LayerStack,
}

if __name__ == "__main__":
    #打印一个层栈信息并保存：
    #定义保存路径和文件名
    output_file = fr"C:\Windows\System32\CSU_PDK/csufactory/all_output_files/parameter/Si_zp45_LayerStack.txt"
    #打开文件进行写入
    with open(output_file, "w") as file:
        # 遍历层信息并将输出写入文件
        print("将Si_zp45_LayerStack中的主要参数，保存至下方文件内")
        file.write("Design Rules for 0.45% Delta N index (um)\n"
                   "\t\tParameter\n")
        for key, value in Si_zp45_LayerStack.layers['substrate'].info.items():
            file.write(f"{key}: {value}\n")
        file.write("\nlayer_stack_parameter")
        for layername, layer in Si_zp45_LayerStack.layers.items():
            file.write(
                f"\nLayerName: {layername}:\n "
                f"\tThickness: {layer.thickness},\n"
                f"\tThickness_tolerance: {layer.thickness_tolerance}, \n"
                f"\tMaterial: {layer.material}, \n"
                f"\tZmin: {layer.zmin}, \n"
                f"\tDerivedLayer: {layer.derived_layer}\n"
            )
            #除去substrate的info
            if layername != "substrate" and layer.info:
                file.write("\tInfo:\n")
                for key, value in layer.info.items():
                    file.write(f"\t\t{key}: {value}\n")  #每个 info 参数换行
            # #打印所有info
            # if hasattr(layer, "info") and isinstance(layer.info, dict):
            #     file.write("\tInfo:\n")  # 添加 Info 标题
            #     for key, value in layer.info.items():
            #         file.write(f"\t\t{key}: {value}\n")  # 每个键值对占一行
    print(f"TXT文件已保存至: {output_file}")


####打印三个不同的layer_stack:
    output_file2 = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter\CSU_LayerStack.txt"
    #打开文件进行写入
    with open(output_file2, "w") as file:
        # 遍历层信息并将输出写入文件
        print("将CSU_LayerStack中的主要参数，保存至下方文件内")
        for stack_name, layer_stack in CSU_LayerStacks.items():
            file.write(f"\n===== {stack_name} =====\n")
            file.write(f"Design Rules for {stack_name} Delta N index (um)\n"
                       "\t\tParameter\n")
            for key, value in layer_stack.layers['substrate'].info.items():
                file.write(f"{key}: {value}\n")
            for layername, layer in layer_stack.layers.items():
                file.write(
                    f"\nLayerName: {layername}:\n "
                    f"\tThickness: {layer.thickness},\n"
                    f"\tThickness_tolerance: {layer.thickness_tolerance}, \n"
                    f"\tMaterial: {layer.material}, \n"
                    # f"\tinfo: {layer.info}, \n"
                    f"\tZmin: {layer.zmin}, \n"
                    f"\tDerivedLayer: {layer.derived_layer}\n"
                )
                # 修改 info 的存储方式
                if layername != "substrate" and layer.info:
                    file.write("\tInfo:\n")
                    for key, value in layer.info.items():
                        file.write(f"\t\t{key}: {value}\n")  # 每个 info 参数换行

    print(f"TXT文件已保存至: {output_file2}")


    #输出仅有awg的gds文件，并命名、保存：
    z = gf.technology.layer_stack.get_component_with_derived_layers(c,zp45_GDS)
    component_name = "awg_1_1"
    #将Si_zp45_GDS修改为Si_zp45_LayerStack，可以输出多层的
    # z = gf.technology.layer_stack.get_component_with_derived_layers(c, Si_zp45_LayerStack)
    # component_name = "awg_1_2"
    #无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    #有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    z.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
    z.show()

    #生成有每个层的3d预览图：
    #这里的c包含上述的所有component
    s =c.to_3d(layer_stack=Si_zp45_LayerStack)
    s.show()


    #生成仅有awg的3d预览图：
    #用新的变量可以改变器件的参数s
    # c = awg(
    #     inputs= 1,
    #     arms= 9,                                      #阵列波导数量
    #     outputs= 1,
    #     free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
    #     free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
    #     fpr_spacing= 50.0,                            #输入/输出FPR的间距
    #     arm_spacing= 1.0,                             #阵列波导间距
    # )
    s =c.to_3d(layer_stack=zp45_GDS)
    s.show()

    # 定义保存路径和文件名
    output_file = fr"C:\Windows\System32\CSU_PDK/csufactory/all_output_files/parameter/klayout_3d_script(Si_zp45_LayerStack).txt"
    # 打开文件进行写入
    with open(output_file, "w") as file:
        file.write(get_klayout_3d_script(Si_zp45_LayerStack))

    print(f"GDS 文件已保存至: {output_file}")
