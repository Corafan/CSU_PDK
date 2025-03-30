#第一种：
from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s

@gf.cell
def Sbend(
    width: float = 0.5,
    dy: Delta = 4.0,
    dx: Delta = 10.0,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""generate an s_bends.

    Args:
        width: width of bend.
        dy: port to port vertical spacing.
        dx: bend length in x direction.
        cross_section: section.

    .. code::

                       dx
                    |-----|
                       ___ o3
                      /       |
             o2 _____/        |dy


    """
    c = Component()
    x = gf.get_cross_section(cross_section,width=width)
    width1 = x.width
    dy = (dy - width1)

    bend_component = gf.get_component(
        bend_s,
        size=(dx, dy),
        cross_section=x,
    )
    top_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name

    c.add_port("o1", port=top_bend[bend_port1_name])
    c.add_port("o2", port=top_bend[bend_port2_name])


    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]
    return c


#第二种：
# from __future__ import annotations
#
# import numpy as np
# from numpy import ndarray
#
# import gdsfactory as gf
# from gdsfactory.component import Component
# from gdsfactory.config import ErrorType
# from gdsfactory.functions import  curvature, snap_angle
# from gdsfactory.typings import  Coordinates, CrossSectionSpec
#
#
# def bezier_curve(t: ndarray, control_points: Coordinates) -> ndarray:
#     """Returns bezier coordinates.
#
#     Args:
#         t: 1D array of points varying between 0 and 1.
#         control_points: for the bezier curve.
#     """
#     from scipy.special import binom
#
#     xs = 0.0
#     ys = 0.0
#     n = len(control_points) - 1
#     for k in range(n + 1):
#         ank = binom(n, k) * (1 - t) ** (n - k) * t**k
#         xs += ank * control_points[k][0]
#         ys += ank * control_points[k][1]
#
#     return np.column_stack([xs, ys])
#
# @gf.cell
# def Sbend(
#     control_points: Coordinates = ((0.0, 0.0), (5.0, 0.0), (5.0, 1.8), (10.0, 1.8)),
#     npoints: int = 201,
#     width: float = 0.5,
#     with_manhattan_facing_angles: bool = True,
#     start_angle: int | None = None,
#     end_angle: int | None = None,
#     cross_section: CrossSectionSpec = "strip",
#     bend_radius_error_type: ErrorType | None = None,
#     allow_min_radius_violation: bool = False,
# ) -> Component:
#     """Returns S bend.
#
#     Args:
#         control_points: list of points.
#         npoints: number of points varying between 0 and 1.
#         width: width of the bend.
#         with_manhattan_facing_angles: bool.
#         start_angle: optional start angle in deg.
#         end_angle: optional end angle in deg.
#         cross_section: spec.
#         bend_radius_error_type: error type.
#         allow_min_radius_violation: bool.
#     """
#     xs = gf.get_cross_section(cross_section,width=width)
#     t = np.linspace(0, 1, npoints)
#     path_points = bezier_curve(t, control_points)
#     path = gf.Path(path_points)
#
#     if with_manhattan_facing_angles:
#         path.start_angle = start_angle or snap_angle(path.start_angle)
#         path.end_angle = end_angle or snap_angle(path.end_angle)
#
#     c = path.extrude(xs)
#     curv = curvature(path_points, t)
#     length = path.length()
#     if max(np.abs(curv)) == 0:
#         min_bend_radius = np.inf
#     else:
#         min_bend_radius = float(gf.snap.snap_to_grid(1 / max(np.abs(curv))))
#
#     c.info["length"] = length
#     c.info["min_bend_radius"] = min_bend_radius
#     c.info["start_angle"] = float(path.start_angle)
#     c.info["end_angle"] = float(path.end_angle)
#     c.add_route_info(
#         cross_section=xs,
#         length=c.info["length"],
#         n_bend_s=1,
#         min_bend_radius=min_bend_radius,
#     )
#
#     if not allow_min_radius_violation:
#         xs.validate_radius(min_bend_radius, bend_radius_error_type)
#
#     xs.add_bbox(c)
#     return c



if __name__ == "__main__":
    c=Sbend(width=1,dx=20,dy=8)
    # c = Sbend()
    component_name = "sbend"
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
    c.show()