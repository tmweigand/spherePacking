import numpy as np

import spherepacking


def build_sphere_pack():
    """
    Build a small sphere pack with one sphere near a corner (so it generates
    periodic boundary copies) and one interior sphere (no periodic copies).
    """
    x = np.array(
        [
            [0.5, 0.5, 0.5],
            [5.0, 5.0, 5.0],
        ]
    )
    radii = np.array([1.0, 1.0])

    spheres = spherepacking.Spheres(radii, x)
    domain = spherepacking.Domain(spheres=spheres, porosity=0)
    domain.length[:] = 10.0

    # Use a copy of domain.length, mirroring how read_pack() builds a SpherePack
    # with its own independent `length` array rather than aliasing domain.length.
    sp = spherepacking.SpherePack(domain, spheres, domain.length.copy(), x.shape[0])
    return sp


def test_convert_to_ellipsoids_preserves_porosity(tmp_path):
    sp = build_sphere_pack()
    original_porosity = sp.porosity
    original_n_spheres = sp.n_spheres

    sp.gen_periodic_objects()
    # Sanity check: the corner sphere should have generated periodic copies.
    assert sp.n_b_p_spheres > 0

    pack_io = spherepacking.SpherePackIO(
        sp.domain,
        media_type="Ellipsoids",
        run_folder=str(tmp_path / "run"),
        out_folder=str(tmp_path / "out"),
        dim=0,
        factor=2.0,
    )

    ellipsoid_sp = pack_io.convert_to_ellipsoids(sp)

    # Original (unique) sphere count and periodic copy count must be preserved.
    assert ellipsoid_sp.n_spheres == original_n_spheres
    assert ellipsoid_sp.n_b_p_spheres == sp.n_b_p_spheres
    assert ellipsoid_sp.media.x.shape[0] == original_n_spheres + sp.n_b_p_spheres

    # The key regression check: porosity must not change just because periodic
    # boundary copies exist (previously their volume was double-counted).
    assert np.isclose(ellipsoid_sp.porosity, original_porosity)


if __name__ == "__main__":
    import tempfile
    import pathlib

    with tempfile.TemporaryDirectory() as tmp:
        test_convert_to_ellipsoids_preserves_porosity(pathlib.Path(tmp))
    print("OK")
