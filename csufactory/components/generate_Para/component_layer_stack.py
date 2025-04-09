import gdsfactory as gf
import datetime
from functools import partial

from botocore.utils import percent_encode_sequence

from csufactory.generic_tech.layer_map import CSULAYER as LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from csufactory.technology.get_klayout_3d_script import get_klayout_3d_script
from csufactory.generic_tech.layer_stack import LayerStackParameters as Para
from csufactory.components.awg import free_propagation_region
from csufactory.components.awg import awg
from csufactory.components.mmi import mmi
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
            material="Quartz",
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
            material="Quartz",
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
    import os
    from typing import Dict, Any
    import csufactory
    from gdsfactory.technology import LayerViews
    def export_layer_stacks(
            CSU_LayerStacks: Dict[str, Any] = {
                "0.45%": "Si_zp45_LayerStack",
                "0.75%": "Si_zp75_LayerStack",
                "1.5%": "Si_150_LayerStack"
            },
            output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",
            combined_filename: str = "CSU_LayerStack.txt"
    ) -> None:
        """
        导出层栈信息（自动判断输出单独文件或合并文件）

        参数:
            CSU_LayerStacks: 层栈字典 {百分比: 层栈变量名}
            output_dir: 输出目录路径
            combined_filename: 合并文件名（仅在多个层栈时生成）
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 判断是否为单个层栈
        is_single = len(CSU_LayerStacks) == 1

        if is_single:
            # 单个层栈模式：只生成单独文件
            percent_str, layer_stack_name = next(iter(CSU_LayerStacks.items()))
            layer_stack = globals().get(layer_stack_name)

            if not layer_stack:
                print(f"错误: 未找到层栈定义 {layer_stack_name}")
                return

            # 生成单独文件名
            single_filename = f"LayerStack_{percent_str.replace('%', 'percent')}.txt"
            single_path = os.path.join(output_dir, single_filename)

            with open(single_path, "w", encoding="utf-8") as single_file:
                # 写入文件头
                print(f"将{layer_stack_name}中的主要参数，保存至下方文件内")
                single_file.write(f"Design Rules for {percent_str} Delta N index (um)\n")
                single_file.write("\t\tParameter\n")

                # 写入基底信息
                if 'substrate' in getattr(layer_stack, 'layers', {}):
                    substrate = layer_stack.layers['substrate']
                    if hasattr(substrate, 'info'):
                        for key, value in substrate.info.items():
                            single_file.write(f"{key}: {value}\n")

                # 写入各层信息
                for layer_name, layer in layer_stack.layers.items():
                    single_file.write(f"\nLayerName: {layer_name}:\n")
                    single_file.write(f"\tThickness: {layer.thickness},\n")
                    single_file.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
                    single_file.write(f"\tMaterial: {layer.material},\n")
                    single_file.write(f"\tZmin: {layer.zmin},\n")
                    single_file.write(f"\tDerivedLayer: {layer.derived_layer}\n")

                    if layer_name != "substrate" and getattr(layer, 'info', None):
                        single_file.write("\tInfo:\n")
                        for key, value in layer.info.items():
                            single_file.write(f"\t\t{key}: {value}\n")

            print(f"TXT文件已保存至: {single_path}")

        else:
            # 多个层栈模式：生成合并文件和单独文件
            combined_path = os.path.join(output_dir, combined_filename)
            with open(combined_path, "w", encoding="utf-8") as combined_file:
                print("将CSU_LayerStack中的主要参数，保存至下方文件内")

                for percent_str, layer_stack_name in CSU_LayerStacks.items():
                    layer_stack = globals().get(layer_stack_name)
                    if not layer_stack:
                        print(f"警告: 未找到层栈定义 {layer_stack_name}，跳过")
                        continue

                    # 写入合并文件
                    combined_file.write(f"\n===== {percent_str} =====\n")
                    combined_file.write(f"Design Rules for {percent_str} Delta N index (um)\n")
                    combined_file.write("\t\tParameter\n")

                    # 生成单独文件
                    single_filename = f"LayerStack_{percent_str.replace('%', 'percent')}.txt"
                    single_path = os.path.join(output_dir, single_filename)

                    with open(single_path, "w", encoding="utf-8") as single_file:
                        # 写入单独文件头
                        single_file.write(f"Design Rules for {percent_str} Delta N index (um)\n")
                        single_file.write("\t\tParameter\n")

                        # 处理公共内容
                        for file in [combined_file, single_file]:
                            # 写入基底信息
                            if 'substrate' in getattr(layer_stack, 'layers', {}):
                                substrate = layer_stack.layers['substrate']
                                if hasattr(substrate, 'info'):
                                    for key, value in substrate.info.items():
                                        file.write(f"{key}: {value}\n")

                            # 写入各层信息
                            for layer_name, layer in layer_stack.layers.items():
                                file.write(f"\nLayerName: {layer_name}:\n")
                                file.write(f"\tThickness: {layer.thickness},\n")
                                file.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
                                file.write(f"\tMaterial: {layer.material},\n")
                                file.write(f"\tZmin: {layer.zmin},\n")
                                file.write(f"\tDerivedLayer: {layer.derived_layer}\n")

                                if layer_name != "substrate" and getattr(layer, 'info', None):
                                    file.write("\tInfo:\n")
                                    for key, value in layer.info.items():
                                        file.write(f"\t\t{key}: {value}\n")

                    print(f"已生成单独文件: {single_filename}")

            print(f"\n合并文件已保存至: {combined_path}")

    export_layer_stacks()


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
    #
    # #生成仅有awg的3d预览图：
    # #用新的变量可以改变器件的参数s
    # # c = awg(
    # #     inputs= 1,
    # #     arms= 9,                                      #阵列波导数量
    # #     outputs= 1,
    # #     free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
    # #     free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
    # #     fpr_spacing= 50.0,                            #输入/输出FPR的间距
    # #     arm_spacing= 1.0,                             #阵列波导间距
    # # )
    s =c.to_3d(layer_stack=zp45_GDS)
    s.show()

    # 定义保存路径和文件名
    output_file = fr"C:\Windows\System32\CSU_PDK/csufactory/all_output_files/parameter/klayout_3d_script(Si_zp45_LayerStack).txt"
    # 打开文件进行写入
    with open(output_file, "w") as file:
        file.write(get_klayout_3d_script(Si_zp45_LayerStack))

    print(f"GDS 文件已保存至: {output_file}")


    #合并打印一个文件版：
    # import os
    # from typing import Dict, Any
    #
    # def export_combined_layer_stack_info(
    #         CSU_LayerStacks: Dict[str, Any] = {
    #             "0.45%": "Si_zp45_LayerStack",
    #             "0.75%": "Si_zp75_LayerStack",
    #             "1.5%": "Si_150_LayerStack"
    #         },
    #         output_file: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter\CSU_LayerStack.txt"
    # ) -> None:
    #     """
    #     将多个层栈信息合并导出到一个文本文件中
    #
    #     参数:
    #         CSU_LayerStacks: 层栈字典 {百分比: 层栈变量名}
    #         output_file: 输出文件完整路径
    #
    #     返回:
    #         None (结果直接保存到文件)
    #     """
    #     # 创建输出目录(如果不存在)
    #     os.makedirs(os.path.dirname(output_file), exist_ok=True)
    #
    #     with open(output_file, "w", encoding="utf-8") as f:
    #         print("将CSU_LayerStack中的主要参数，保存至下方文件内")
    #
    #         for percent_str, layer_stack_name in CSU_LayerStacks.items():
    #             try:
    #                 # 动态获取层栈对象
    #                 layer_stack = globals().get(layer_stack_name)
    #                 if layer_stack is None:
    #                     print(f"警告: 未找到层栈定义 {layer_stack_name}，跳过")
    #                     continue
    #
    #                 # 写入层栈标题
    #                 f.write(f"\n===== {percent_str} =====\n")
    #                 f.write(f"Design Rules for {percent_str} Delta N index (um)\n")
    #                 f.write("\t\tParameter\n")
    #
    #                 # 写入基底(substrate)信息
    #                 if hasattr(layer_stack, 'layers') and 'substrate' in layer_stack.layers:
    #                     substrate = layer_stack.layers['substrate']
    #                     if hasattr(substrate, 'info'):
    #                         for key, value in substrate.info.items():
    #                             f.write(f"{key}: {value}\n")
    #
    #                 # 写入各层信息
    #                 for layer_name, layer in layer_stack.layers.items():
    #
    #                     f.write(f"\nLayerName: {layer_name}:\n")
    #                     f.write(f"\tThickness: {layer.thickness},\n")
    #                     f.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
    #                     f.write(f"\tMaterial: {layer.material},\n")
    #                     f.write(f"\tZmin: {layer.zmin},\n")
    #                     f.write(f"\tDerivedLayer: {layer.derived_layer}\n")
    #
    #                     if layer_name != "substrate" and layer.info:
    #                         f.write("\tInfo:\n")
    #                         for key, value in layer.info.items():
    #                             f.write(f"\t\t{key}: {value}\n")  #每个 info 参数换行
    #
    #             except Exception as e:
    #                 print(f"处理 {layer_stack_name} 时出错: {str(e)}")
    #                 continue
    #
    #     print(f"TXT文件已保存至: {output_file}")


    #第一版
    # import os
    # def export_layer_stack_info(
    #         layer_stack_name: str = "Si_zp45_LayerStack",
    #         output_dir: str = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter",
    #         percent: float = 0.45,
    #         file_prefix: str = "LayerStack"
    # ) -> None:
    #     """
    #     导出层栈信息到文本文件
    #
    #     参数:
    #         layer_stack_name: 层栈变量名 (默认: "Si_zp45_LayerStack")
    #         output_dir: 输出目录路径 (默认: CSU_PDK参数目录)
    #         percent: 折射率变化百分比 (默认: 0.45)
    #         file_prefix: 输出文件名前缀 (默认: "LayerStack")
    #
    #     返回:
    #         None (结果直接保存到文件)
    #     """
    #     # 动态获取层栈对象
    #     layer_stack = globals().get(layer_stack_name)
    #     if layer_stack is None:
    #         raise ValueError(f"未找到层栈定义: {layer_stack_name}")
    #
    #     # 构建输出文件路径
    #     output_filename = f"{file_prefix}_{percent * 100:.0f}percent.txt"
    #     output_path = os.path.join(output_dir, output_filename)
    #
    #     # 创建输出目录(如果不存在)
    #     os.makedirs(output_dir, exist_ok=True)
    #     with open(output_path, "w", encoding="utf-8") as f:
    #         # 写入文件头
    #         print(f"将{layer_stack_name}中的主要参数，保存至下方文件内")
    #         f.write(f"Design Rules for {percent * 100:.2f}% Delta N index (um)\n")
    #         f.write("\t\tParameter\n")
    #
    #         # 写入基底(substrate)信息
    #         if 'substrate' in layer_stack.layers:
    #             for key, value in layer_stack.layers['substrate'].info.items():
    #                 f.write(f"{key}: {value}\n")
    #
    #         # 写入各层信息
    #         f.write("\nlayer_stack_parameter\n")
    #         for layer_name, layer in layer_stack.layers.items():
    #
    #             f.write(f"\nLayerName: {layer_name}:\n")
    #             f.write(f"\tThickness: {layer.thickness},\n")
    #             f.write(f"\tThickness_tolerance: {layer.thickness_tolerance},\n")
    #             f.write(f"\tMaterial: {layer.material},\n")
    #             f.write(f"\tZmin: {layer.zmin},\n")
    #             f.write(f"\tDerivedLayer: {layer.derived_layer}\n")
    #
    #             if layer_name != "substrate" and layer.info:
    #                         f.write("\tInfo:\n")
    #                         for key, value in layer.info.items():
    #                             f.write(f"\t\t{key}: {value}\n")  #每个 info 参数换行
    #             print(f"TXT文件已保存至: {output_path}")


#     output_file = fr"C:\Windows\System32\CSU_PDK/csufactory/all_output_files/parameter/Si_zp45_LayerStack.txt"
#     #打印一个层栈信息并保存：
#     #定义保存路径和文件名
#     #打开文件进行写入
#     with open(output_file, "w") as file:
#         # 遍历层信息并将输出写入文件
#         print(f"将{layer_stack_name}中的主要参数，保存至下方文件内")
#         file.write("Design Rules for {percent}% Delta N index (um)\n"
#                    "\t\tParameter\n")
#         for key, value in Si_zp45_LayerStack.layers['substrate'].info.items():
#             file.write(f"{key}: {value}\n")
#         file.write("\nlayer_stack_parameter")
#         for layername, layer in Si_zp45_LayerStack.layers.items():
#             file.write(
#                 f"\nLayerName: {layername}:\n "
#                 f"\tThickness: {layer.thickness},\n"
#                 f"\tThickness_tolerance: {layer.thickness_tolerance}, \n"
#                 f"\tMaterial: {layer.material}, \n"
#                 f"\tZmin: {layer.zmin}, \n"
#                 f"\tDerivedLayer: {layer.derived_layer}\n"
#             )
#             #除去substrate的info
#             if layername != "substrate" and layer.info:
#                 file.write("\tInfo:\n")
#                 for key, value in layer.info.items():
#                     file.write(f"\t\t{key}: {value}\n")  #每个 info 参数换行
#             # #打印所有info
#             # if hasattr(layer, "info") and isinstance(layer.info, dict):
#             #     file.write("\tInfo:\n")  # 添加 Info 标题
#             #     for key, value in layer.info.items():
#             #         file.write(f"\t\t{key}: {value}\n")  # 每个键值对占一行
#     print(f"TXT文件已保存至: {output_file}")
#

# ####打印三个不同的layer_stack:
#     output_file2 = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\parameter\CSU_LayerStack.txt"
#     #打开文件进行写入
#     with open(output_file2, "w") as file:
#         # 遍历层信息并将输出写入文件
#         print("将CSU_LayerStack中的主要参数，保存至下方文件内")
#         for stack_name, layer_stack in CSU_LayerStacks.items():
#             file.write(f"\n===== {stack_name} =====\n")
#             file.write(f"Design Rules for {stack_name} Delta N index (um)\n"
#                        "\t\tParameter\n")
#             for key, value in layer_stack.layers['substrate'].info.items():
#                 file.write(f"{key}: {value}\n")
#             for layername, layer in layer_stack.layers.items():
#                 file.write(
#                     f"\nLayerName: {layername}:\n "
#                     f"\tThickness: {layer.thickness},\n"
#                     f"\tThickness_tolerance: {layer.thickness_tolerance}, \n"
#                     f"\tMaterial: {layer.material}, \n"
#                     # f"\tinfo: {layer.info}, \n"
#                     f"\tZmin: {layer.zmin}, \n"
#                     f"\tDerivedLayer: {layer.derived_layer}\n"
#                 )
#                 # 修改 info 的存储方式
#                 if layername != "substrate" and layer.info:
#                     file.write("\tInfo:\n")
#                     for key, value in layer.info.items():
#                         file.write(f"\t\t{key}: {value}\n")  # 每个 info 参数换行
#
#     print(f"TXT文件已保存至: {output_file2}")
#