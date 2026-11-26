import math
from dataclasses import dataclass
from cadquery import func as cf

@dataclass
class CellSpec:
    r_cell: float
    h_cell: float

def tray(spec, n=3, clearance=0.3, wall=4.0,
         thickness=6.0, depth=3.0, mount_d=4.0):

    pocket_r = spec.r_cell + clearance
    pitch = 2 * pocket_r + wall

    mount_r = mount_d / 2

    # Extra width to accommodate two mounting holes
    tray_width = 2 * (pocket_r + 2 * wall + 2 * mount_r)
    tray_length = n * pitch + wall

    plate = cf.box(tray_length, tray_width, thickness)

    # Battery pockets
    pocket = cf.cylinder(
        d=2 * pocket_r,
        h=depth + 1
    ).moved(z=thickness - depth)

    for i in range(n):
        x = (i - (n - 1) / 2) * pitch
        plate = plate - pocket.moved(x=x)

    # Two mirrored mounting holes
    mount_hole = cf.cylinder(
        d=mount_d,
        h=thickness + 1
    ).moved(z=-0.5)

    mount_y = pocket_r + wall + mount_r

    for y in [-mount_y, mount_y]:
        plate = plate - mount_hole.moved(y=y)

    return plate


cells = {
    "18650": CellSpec(9.0, 65.0),
    "21700": CellSpec(10.5, 70.0),
    "4680": CellSpec(23.0, 80.0),
}

if __name__ == "__main__":
    for name, spec in cells.items():
        t = tray(spec)

        # Expected volume after adding mounting holes
        pocket_r = spec.r_cell + 0.3
        pitch = 2 * pocket_r + 4.0
        mount_r = 2.0
        tray_width = 2 * (pocket_r + 2 * 4.0 + 2 * mount_r)
        tray_length = 3 * pitch + 4.0

        expected = (
            tray_length * tray_width * 6.0
            - 3 * math.pi * pocket_r**2 * 3.0
            - 2 * math.pi * mount_r**2 * 6.0
        )

        assert t.isValid()
        assert abs(t.Volume() - expected) < 0.5

        print(name, t.isValid(), round(t.Volume(), 1))
        t.exportStl(f"tray_{name}.stl")
