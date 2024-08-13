import numpy as np

import spherepacking


x = np.array([
    [0.5,0.5,0.5]
])

N = x.shape[0]
radii = np.ones(N)

spheres = spherepacking.Spheres(radii,x)

domain = spherepacking.Domain(
    spheres=spheres,
    porosity=0)

domain.length[:] = 10.

sp  = spherepacking.SpherePack(
    domain,
    spheres,
    domain.length,
    N
)

print(sp.find_point_in_pore(5000))

