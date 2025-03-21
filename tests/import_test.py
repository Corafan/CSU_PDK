#测试layer_stack.py是否能被正常导入，这个是其中的某个函数：

from csufactory.generic_tech.layer_stack import get_process

process_steps = get_process()  # 获取制造步骤

for step in process_steps:
    print(f"Processing step: {step.name}")

#可以正常运行