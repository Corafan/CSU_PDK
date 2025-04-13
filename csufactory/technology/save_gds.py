import datetime
def save_gds(component,
             component_name:str=None,
             output_gds_path=None,
             ):
    """保存组件到GDS文件"""
    # 文件名：
    if component_name is None:
        component_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        component_name = component_name
    # 文件保存地址：
    if output_gds_path is None:
        # 无时间戳：
        output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
        # # 有时间戳：
        # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    else:
        output_gds_path = output_gds_path
    component.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")