import numpy as np

class Ellipsoids:
    """
    Spheres
    """

    def __init__(self, radii, x=None) -> None:
        self.x = x
        self.radii = radii
        self.n = len(radii)
        self.volume = 0
        self.area = 0
        self.gen_volume()
        self.gen_surface_area()


    def gen_volume(self):
        """
        Generate the volume of the spheres
        """
        for r in self.radii:
            self.volume += 4.0 / 3.0 * np.pi *  r[0] * r[1] * r[2]

    def gen_surface_area(self):
        """
        Generate the surface area of the ellipsoids - NOT EXACT
        """
        for r in self.radii:
            self.area += 4*np.pi/3.0*( (r[0]*r[1])**1.6 + (r[0]*r[2])**1.6 + (r[1]*r[2])**1.6 )**(1/1.6)

    def print_stats(self):
        """
        Print stats of ellipsoids
        """
        print(f"Volume: {self.volume}")

    def add_spheres(self,x,radii):
        """
        Append to the spheres
        """
        self.x = np.append(self.x,x,axis=0)
        print(radii,self.radii)
        self.radii = np.append(self.radii,radii,axis=0)