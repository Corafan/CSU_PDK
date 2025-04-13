from csufactory.components.awg import awg
from csufactory.technology.save_gds import save_gds
c=awg(inputs=1,arms=5,outputs=1)
c.show()
save_gds(c,1111)
