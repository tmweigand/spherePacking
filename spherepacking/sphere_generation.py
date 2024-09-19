import numpy as np

class SphereRadii:
    """
    Specifications for spheres to be generated 
    """

    def __init__(self, n, distribution, mean, stdev, run_folder, media_type) -> None:
        self.n = n
        self.distribution = distribution
        self.mean = mean
        self.stdev = stdev
        self.radii = None
        self.run_folder = run_folder
        self.media_type = media_type

        self.gen_radii()
        self.print_diameters()
        if media_type == 'ellipsoids':
            self.set_ellipsoids()


    def gen_radii(self):
        """
        Generate the radii from the distribution
        """
        if self.distribution == "lognormal":
            self.radii = np.random.lognormal(self.mean, self.stdev, self.n)

        if self.distribution == "normal":
            self.radii = np.random.normal(self.mean, self.stdev, self.n)

    def gen_pdf(self):
        """
        Generate probability density function plot
        """
        # count, bins, ignored = plt.hist(
        #     self.radii,
        #     100,
        #     density=True,
        #     align='mid'
        #     )
        # x = np.linspace(min(bins), max(bins), 10000)
        # pdf = (np.exp(-(np.log(x) - self.mean)**2 / (2 * self.stdev**2))/(x * self.stdev * np.sqrt(2 * np.pi)))
        # plt.plot(x, pdf, linewidth=2, color='r')
        # plt.axis('tight')
        # plt.show()

    def print_diameters(self):
        """
        Create and write to 'diameters.txt'
        """
        out_file = open(self.run_folder + "/diameters.txt", "w", encoding="utf-8")
        for r in self.radii:
            d = r * 2.0
            out_file.write("%lf \n" % d)
        out_file.close()

    def set_ellipsoids(self):
        """
        Convert sphere radii to ellipsoids
        """
        if self.media_type == "ellipsoids":
            _radii = np.zeros([self.radii.shape[0],3])
            _radii[:,0] = self.radii
            _radii[:,1] = self.radii
            _radii[:,2] = self.radii
            self.radii = _radii
