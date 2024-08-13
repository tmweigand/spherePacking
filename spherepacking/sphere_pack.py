import numpy as np
import itertools

from .spheres import Spheres
class SpherePack:
    """
    Class for running the sphere pack code
    """

    def __init__(self, domain, media, length, n_objects) -> None:
        self.domain = domain
        self.media = media
        self.length = length
        self.n_spheres = n_objects
        self.n_b_spheres = 0
        self.n_b_p_spheres = 0
        self.boundary_spheres = None
        self.pore_point = None
        self.porosity = self.get_porosity()


    def get_porosity(self):
        """
        Generate the porosity before adding boundary spheres - bad code
        """
        return 1 - self.media.volume / np.prod(self.length)

    def gen_periodic_objects(self):
        """
        Add periodic boundary spheres
        """
        self.get_boundary_spheres()
        x,r = self.add_periodic_objects()
        self.media.add_spheres(x,r)

    def get_boundary_spheres(self):
        """
        Determine if a sphere hangs over boundary edges
            0: x-   1: x+
            2: y-   3: y+
            4: z-   5: z+
        """
        boundary_spheres = {}
        for n in range(self.n_spheres):
            boundary_spheres[n] = []
            x = self.media.x[n]
            r = self.media.radii[n]
            for dim in [0, 1, 2]:
                if x[dim] - r < 0.0:
                    boundary_spheres[n].append(dim * 2)
                if x[dim] + r > self.length[dim]:
                    boundary_spheres[n].append(dim * 2 + 1)

            if len(boundary_spheres[n]) == 0:
                del boundary_spheres[n]

        self.n_b_spheres = len(boundary_spheres)
        self.boundary_spheres = boundary_spheres

        print("TIMMMMMM",self.n_b_spheres)

    def add_periodic_objects(self):
        """
        Sphere packing code does not explicitly include periodic spheres that
        do not have their centroid located within the domain
        """
        add_spheres = []
        for sphere in self.boundary_spheres:
            x = self.media.x[sphere]
            r = self.media.radii[sphere]
            perms = self.get_boundary_permutations(sphere)
            x_new = add_boundary_location(x, perms, self.domain,r)
            add_spheres.extend(x_new)

        self.n_b_p_spheres = len(add_spheres)
        add_spheres = np.array(add_spheres)
        return add_spheres[:,0:3],add_spheres[:,3]

    def get_boundary_permutations(self,ID):
        """
        Generate a list of all boundary faces for a boundary sphere
        """
        perms = {}
        for n in [1, 2, 3]:
            perms[n] = list(
                itertools.combinations(self.boundary_spheres[ID], n)
                )

        return perms

    def point_in_pore(self,x):
        """
        Determine if point is in solid or pore space
        """
        in_pore = True
        n = 0
        while in_pore and n < (self.n_spheres +  self.n_b_p_spheres):
            distance = 0
            for dim in [0,1,2]:
                print(dim,self.media.x[n][dim] , x[dim],self.media.radii[n])
                distance += (self.media.x[n][dim] - x[dim])*(self.media.x[n][dim] - x[dim])

            # print(distance,self.media.radii[n])
            if distance < self.media.radii[n]*self.media.radii[n]:
                in_pore = False
            
            n += 1
        return in_pore

    def find_point_in_pore(self,N=1000):
        """
        For some software, a point within the pore space is needed.
        """
        eps = 1.e-3
        x = np.linspace(0,self.length[0],N)
        for _x in x:
            print(_x)
            if self.point_in_pore([_x,eps,eps]):
                break

        self.pore_point = (_x,eps,eps)


def add_boundary_location(x, perms, domain,r):
    """
    From indices determine where to add boundary spheres
    """
    x = np.append(x,r)
    boundary_spheres = []
    for (_,faces) in perms.items():
        for face_list in faces:
            x_new = x.tolist()
            for bound in face_list:
                if bound % 2 == 0:
                    dim = int(bound / 2)
                    x_new[dim] = domain.length[dim] + x[dim]
                else:
                    dim = int((bound - 1) / 2)
                    x_new[dim] = x[dim] - domain.length[dim]
            boundary_spheres.append(x_new)
                
    return boundary_spheres