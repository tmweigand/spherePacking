import numpy as np

import spherepacking


x = np.array([
    # [0.5,5.5,5.5],
    # [9.5,5.5,5.5],
    # [9.5,9.5,9.5]
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

sp.get_boundary_spheres()
# print(sp.boundary_spheres)

# for n in np.arange(0,N):
#     perm = sp.get_boundary_permutations(n)
#     print(perm)
#     new = spherepacking.sphere_pack.add_boundary_location(x[n], perm, domain,radii[n])
#     print(new)

print(sp.add_periodic_objects())
