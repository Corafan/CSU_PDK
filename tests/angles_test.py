#最初
    # 2. 计算波导的角度（均匀分布）
    # angles = [i * (360 / num_ports) for i in range(num_ports)]  # 均匀分布的角度

    #第二种（这不行）
    # # 2. 计算波导的角度（确保左右对称，并剔除 90° ±15° 和 270° ±15° 的区域）
    # base_angles = np.linspace(0, 180, num_ports // 2 + 1, endpoint=False)  # 生成一半角度，包括0°
    # angles = np.concatenate([base_angles, 360 - base_angles])  # 生成对称角度
    #
    # # 过滤掉最上 (90° ±15°) 和 最下 (270° ±15°) 角度范围
    # angles = [angle for angle in angles if not (75 <= angle <= 105 or 255 <= angle <= 285)]
    # angles = angles[:num_ports]  # 确保最终数量符合 num_ports
    # angles.sort()  # 确保角度有



    # #第三种：
    # # 2. 计算对称角度（避开90°±15°和270°±15°）
    # if num_ports % 2 != 0:
    #     raise ValueError("num_ports必须是偶数以确保对称性")
    #
    # # 生成基础角度（仅右半部分，0°到180°）
    # # 不剔除 0° 和 180°
    # base_angles_right = np.linspace(0, 180, num_ports // 2+1, endpoint=False)
    #
    # # 过滤掉顶部附近的角度（75°~105°）
    # # 生成包含 0° 和 180° 的角度（慎用！）
    # base_angles_right = np.linspace(0, 180, num_ports // 2+1, endpoint=False)
    # angles = []
    # for angle in base_angles_right:
    #     angles.append(angle)
    #     if angle != 0 and angle != 180:  # 避免重复添加 360° 和 -180°
    #         angles.append(180 + angle)
    #
    # angles = angles[:num_ports]  # 确保数量正确
    # angles.sort()  # 按角度排序

    #    90
    # 180     0
    #    270

    # if num_ports <=2:
    #     angles=[0,180]
    # if 2< num_ports <=4:
    #     nums= num_ports / 2 + 2
    #     for i in range(nums):
    #         angle=[ 0 + i * 180 / ( num_ports / 2 )]



num_ports=10

#    90
# 180     0
#    270
num_2 = num_ports/2
if num_ports <= 2:
    angles = [0, 180]
# elif 2 < num_ports <= 4:
#     stat_angles = 360/num_ports
#     angles = []
#     for i in range(num_ports):
#         angles.append(stat_angles + i * stat_angles)
# elif 4 < num_ports and num_2 % 2 == 0:
#     angles= [0, 180]
#     nums= num_ports // 4
#     for i in range(1, nums+1):
#         angle_offset = 160 / (num_ports // 2) * i
#         angles.append(0 + angle_offset)
#         angles.append(0 - angle_offset)
#         angles.append(180 + angle_offset)
#         angles.append(180 - angle_offset)
elif 2 < num_ports and num_2 % 2 == 0:
    angles = []
    nums = num_ports // 4
    for i in range( nums + 1):
        angle_offset = 180 / (num_ports // 2)
        angles.append(angle_offset + angle_offset * i)
        angles.append(angle_offset - angle_offset * (i+1))
        angles.append( 180 + 0.5* angle_offset * (i+1))
        angles.append( 180 - 0.5* angle_offset * (i+1))
else:
    angles = []
    nums = num_ports // 4
    for i in range(1, nums + 1):
        angle_offset = 160 / (num_ports // 2) * i
        angles.append(0 + angle_offset)
        angles.append(0 - angle_offset)
        angles.append(180 + angle_offset)
        angles.append(180 - angle_offset)

# 规范化角度到0-360度范围
angles = [angle % 360 for angle in angles]
angles = sorted(list(set(angles)))  # 去重并排序

print(angles)




