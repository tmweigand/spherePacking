import numpy as np


class Domain:
    """
    Specifications for the Domain
    """

    def __init__(self, spheres, porosity) -> None:
        self.spheres = spheres
        self.porosity = porosity
        self.length = np.zeros(3)

    def gen_min_cube(self, eps=0.0):
        """
        Generate the minimum size cube to fit all spheres
        """
        vol_domain = -self.spheres.volume / (self.porosity - 1.0)
        self.length[:] = np.cbrt(vol_domain) + eps

    def gen_non_cube(self, dim, factor):
        """
        Generate a box that is longer in `dim` by `factor`, sized so that
        after `convert_to_ellipsoids` compresses `dim` by `1/factor` (for
        both the sphere radii/positions and the domain length), the
        resulting domain is a cube with the target porosity.

        Compressing one axis by the same factor in both the solid volume
        and the domain volume preserves whatever porosity existed
        beforehand. So instead of stretching a target-porosity cube (which
        would inflate the pre-generation domain volume and understate the
        final porosity), the cube side length is computed here for the
        eventual (post-compression) cube volume, then `dim` is stretched by
        `factor` to build the pre-generation packing box.
        """
        vol_domain = -self.spheres.volume / (self.porosity - 1.0)
        cube_length = np.cbrt(vol_domain / factor)
        self.length[:] = cube_length
        self.length[dim] *= factor

    def print_stats(self):
        """
        Print the domain statistics
        """
        print(f"Domain Length: {self.length}")
