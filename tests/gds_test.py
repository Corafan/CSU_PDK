from csufactory.show_gds import show
from csufactory.show_gds import export_gds
from csufactory.components.waveguide import waveguide
from csufactory.components.awg import awg

# from csufactory.klayout.export import Output
c = waveguide(length=20, width=0.5)
gds_path = export_gds(c, filename="waveguide.gds") # 生成 GDS 文件
show(gds_path)

#test_awg
s=awg()
s.show()
