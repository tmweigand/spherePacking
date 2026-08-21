import numpy as np

import spherepacking


def build_ellipsoid_domain(n=20, radius=1.0, target_porosity=0.3, dim=2, factor=2.0):
    """
    Mirror the ellipsoid workflow: radii treated as (n, 3) "spherical"
    ellipsoids, domain sized via gen_non_cube for a stretched packing box.
    """
    radii = np.full([n, 3], radius)
    spheres = spherepacking.Ellipsoids(radii)

    domain = spherepacking.Domain(spheres=spheres, porosity=target_porosity)
    domain.gen_non_cube(dim=dim, factor=factor)
    return domain, spheres


def fabricate_sphere_pack(domain, spheres, n):
    """
    Stand in for what read_pack() would produce: a set of (scalar-radius)
    spheres placed inside `domain`, with the SAME total volume as the
    "ellipsoids" used to size the domain (so this mimics an ideal packing
    run that achieves the theoretical porosity for the given box).
    """
    x = np.tile(
        domain.length / 2.0, (n, 1)
    )  # positions irrelevant to volume-based porosity
    r = spheres.radii[:, 0].copy()  # scalar radius per sphere
    media = spherepacking.Spheres(r, x)
    sp = spherepacking.SpherePack(domain, media, domain.length.copy(), n)
    return sp


def test_gen_non_cube_preserves_domain_volume():
    n, radius, target_porosity, factor = 20, 1.0, 0.3, 2.0

    radii = np.full(n, radius)
    spheres_cube = spherepacking.Spheres(radii, np.zeros([n, 3]))
    cube_domain = spherepacking.Domain(spheres=spheres_cube, porosity=target_porosity)
    cube_domain.gen_min_cube()

    radii_ell = np.full([n, 3], radius)
    spheres_ell = spherepacking.Ellipsoids(radii_ell)
    stretched_domain = spherepacking.Domain(
        spheres=spheres_ell, porosity=target_porosity
    )
    stretched_domain.gen_non_cube(dim=2, factor=factor)

    assert np.isclose(np.prod(cube_domain.length), np.prod(stretched_domain.length))


def test_stretch_then_squish_achieves_target_porosity(tmp_path):
    n, radius, target_porosity, dim, factor = 20, 1.0, 0.3, 2, 2.0

    domain, spheres = build_ellipsoid_domain(
        n=n, radius=radius, target_porosity=target_porosity, dim=dim, factor=factor
    )
    sp = fabricate_sphere_pack(domain, spheres, n)

    # Pre-squish porosity of the stretched box should already equal target.
    assert np.isclose(sp.porosity, target_porosity)

    pack_io = spherepacking.SpherePackIO(
        sp.domain,
        media_type="Ellipsoids",
        run_folder=str(tmp_path / "run"),
        out_folder=str(tmp_path / "out"),
        dim=dim,
        factor=factor,
    )

    ellipsoid_sp = pack_io.convert_to_ellipsoids(sp)

    assert np.isclose(ellipsoid_sp.porosity, target_porosity)

    # Final domain must be a cube (all three side lengths equal).
    assert np.allclose(ellipsoid_sp.length, ellipsoid_sp.length[0])
    assert np.allclose(domain.length, domain.length[0])


if __name__ == "__main__":
    import tempfile
    import pathlib

    test_gen_non_cube_preserves_domain_volume()
    with tempfile.TemporaryDirectory() as tmp:
        test_stretch_then_squish_achieves_target_porosity(pathlib.Path(tmp))
    print("OK")
