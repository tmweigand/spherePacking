import numpy as np
import subprocess
import pygmsh

from .sphere_pack import SpherePack
from .spheres import Spheres
from .ellipsoids import Ellipsoids
from . import utils


class SpherePackIO:
    """
    Class for IO to the sphere pack code
    """

    def __init__(
        self, domain, media_type, run_folder, out_folder, dim=None, factor=None
    ) -> None:
        self.domain = domain
        self.media_type = media_type
        self.dim = dim
        self.factor = factor
        self.run_folder = run_folder
        self.out_folder = out_folder
        utils.check_folder_path(self.run_folder)
        utils.check_folder_path(self.out_folder)
        

    def generate_sphere_pack(self, seed, periodic=False):
        """
        Wrap IO to sphere_pack
        """
        self.gen_input(seed)
        self.run_pack()
        sp = self.read_pack()
        if periodic:
            sp.gen_periodic_objects()
        return sp

    def gen_input(self, seed, contraction_rate=1.328910e-3):
        """
        Generate 'generation.conf' for the sphere packing code
        """

        out_file = open(self.run_folder + '/' + "generation.conf", "w", encoding="utf-8")
        out_file.write(f"Particles count: {self.domain.spheres.n}\n")
        out_file.write(
            f"Packing size: {self.domain.length[0]} {self.domain.length[1]} {self.domain.length[2]}\n"
        )
        out_file.write("Generation start: 1\n")
        out_file.write(f"Seed: {seed}\n")
        out_file.write("Steps to write: 0\n")
        out_file.write("Boundaries mode: 1\n")
        out_file.write(f"Contraction rate: {contraction_rate} \n")
        out_file.write("Generation mode: 1\n")
        out_file.close()

    def run_pack(self, output=False):
        """
        Run the sphere pack code
        """
        if not output:
            subprocess.run(
                args=["./PackingGeneration.exe", "-fba"],
                check=False,
            )
        else:
            subprocess.run(
                args=["./PackingGeneration.exe", "-fba"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

    def read_pack(self):
        """
        Read the results of the sphere pack
        """

        with open(self.run_folder + "/" + "packing.nfo") as nfo_file:
            head = [next(nfo_file) for x in range(5)]

        n_spheres = int(head[0].split(":")[1])

        length = np.zeros(3)
        split = head[1].split(":")[1].split(" ")
        for n, dim in enumerate([1, 2, 3]):
            length[n] = float(split[dim])

        theory_poro = float(head[2].split(":")[1])
        act_poro = float(head[3].split(":")[1].split(" ")[1])
        scale_fac = pow((1.0 - act_poro) / (1.0 - theory_poro), 1.0 / 3.0)

        sphere_data = np.fromfile(self.run_folder + "/" + "packing.xyzd")

        x = np.zeros([n_spheres, 3])
        r = np.zeros(n_spheres)
        for n, i in enumerate(range(0, n_spheres * 4, 4)):
            x[n, 0] = sphere_data[i]
            x[n, 1] = sphere_data[i + 1]
            x[n, 2] = sphere_data[i + 2]
            r[n] = sphere_data[i + 3] * scale_fac / 2

        if self.media_type == "Spheres":
            media = Spheres(r, x)

        if self.media_type == "Ellipsoids":

            radii = np.zeros([n_spheres, 3])
            for n in range(n_spheres):
                for d in [0, 1, 2]:
                    if d == self.dim:
                        radii[n, d] = r[n] / self.factor
                        x[n, d] = x[n, d] / self.factor
                    else:
                        radii[n, d] = r[n]

            media = Ellipsoids(radii, x)

        return SpherePack(self.domain, media, length, n_spheres)

    def print_stats(self, sp):
        """
        Print the statistics
        """
        print(f"Length {sp.length}")
        print(f"Sphere Volume: {sp.media.volume}")
        print(f"Domain Volume: {np.prod(sp.length)}")
        print(f"Porosity: {sp.porosity}")

    def save_domain_txt(self, sp, file_name):
        """
        Save the domain info as a txt file
        """
        out_file = open(self.out_folder + '/' + file_name + "_domain.txt", "w", encoding="utf-8")

        out_file.write(f"Length {sp.length[0]} {sp.length[1]} {sp.length[2]}\n")
        out_file.write(f"Domain Volume: {np.prod(sp.length)}\n")
        out_file.write(f"Sphere Volume: {sp.media.volume}\n")
        out_file.write(f"Porosity: {sp.porosity}\n")
        out_file.write(f"Sphere Area: {sp.media.area}\n")
        out_file.write(f"Point in Pore Space: {sp.pore_point}\n")
        out_file.close()

    def save_domain_stl(self, sp, file_name):
        """
        Save the domain as vtk for viz
        """
        min_length = np.min(sp.length)
        with pygmsh.geo.Geometry() as geom:
            geom.add_box(
                0.0,
                sp.length[0],
                0.0,
                sp.length[1],
                0.0,
                sp.length[2],
                mesh_size=0.5 * min_length,
            )
            mesh = geom.generate_mesh()
            mesh.write(self.out_folder + '/' + file_name + "_domain.stl")

    def save_pack_stl(self, sp, file_name):
        """
        Save the pack as a stl
        """
        self.save_domain_stl(sp, file_name)

        if self.media_type == "Spheres":
            with pygmsh.geo.Geometry() as geom:
                for n in range(sp.n_spheres + sp.n_b_p_spheres):
                    geom.add_ball(
                        [sp.media.x[n, 0], sp.media.x[n, 1], sp.media.x[n, 2]],
                        sp.media.radii[n],
                        mesh_size=sp.media.radii[n] * 0.1,
                    )
                mesh = geom.generate_mesh()
                mesh.write(self.out_folder + '/' + file_name + ".stl")

        elif self.media_type == "Ellipsoids":
            with pygmsh.geo.Geometry() as geom:
                for n in range(sp.n_spheres):
                    geom.add_ellipsoid(
                        [sp.media.x[n, 0], sp.media.x[n, 1], sp.media.x[n, 2]],
                        [
                            sp.media.radii[n, 0],
                            sp.media.radii[n, 1],
                            sp.media.radii[n, 2],
                        ],
                        mesh_size=0.5,
                    )
                mesh = geom.generate_mesh()
                mesh.write(self.out_folder + '/' + file_name + ".stl")

    def save_pack_txt(self, sp, file_name):
        """
        Save the pack as a csv
        """
        self.save_domain_txt(sp, file_name)

        out_file = open(self.out_folder + "/" + file_name + ".csv", "w", encoding="utf-8")

        for n in range(sp.n_spheres + sp.n_b_p_spheres):
            x = sp.media.x[n]
            r = sp.media.radii[n]
            out_file.write(f"{x[0]},{x[1]},{x[2]},{r}\n")

        out_file.close()

    def save_openfoam(self, sp, file_name):
        """
        Save files in a format for openfoam
        """
        self.save_pack_stl(sp, file_name)
        sp.find_point_in_pore()
        self.save_domain_txt(sp, file_name)
