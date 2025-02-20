import numpy as np


class SphereRadii:
    """
    Specifications for spheres to be generated
    """

    def __init__(
        self,
        n,
        distribution,
        mean,
        stdev,
        run_folder,
        media_type,
        uniform_parameters=False,
    ) -> None:
        self.n = n
        self.distribution = distribution
        self.mean = mean
        self.stdev = stdev
        self.radii = None
        self.run_folder = run_folder
        self.media_type = media_type

        self.gen_radii(uniform_parameters)
        self.print_diameters()
        if media_type == "ellipsoids":
            self.set_ellipsoids()

    def gen_radii(self, uniform_params=False):
        """
        Generate the radii from the distribution.

        Note: The default np.random.lognormal expects that the mean and
        standard deviation are not the values for the distribution itself,
        but of the underlying normal distribution it is derived from.

        Set uniform_params to True to use lognormal parameters.

        """
        if self.distribution == "lognormal":
            if not uniform_params:
                self.radii = np.random.lognormal(self.mean, self.stdev, self.n)
            else:
                log_mean = np.log(self.mean**2 / np.sqrt(self.mean**2 + self.stdev**2))
                log_stdev = np.sqrt(np.log(1 + self.stdev**2 / (self.mean**2)))
                self.radii = np.random.lognormal(log_mean, log_stdev, self.n)

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
            _radii = np.zeros([self.radii.shape[0], 3])
            _radii[:, 0] = self.radii
            _radii[:, 1] = self.radii
            _radii[:, 2] = self.radii
            self.radii = _radii
