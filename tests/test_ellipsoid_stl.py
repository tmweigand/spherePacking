import numpy as np
from unittest.mock import patch, MagicMock

import spherepacking
from spherepacking.sphere_pack_io import SpherePackIO


def build_periodic_ellipsoid_pack(tmp_path, dim=0, factor=2.0):
    """
    Build an ellipsoid SpherePack that includes periodic boundary copies
    (a sphere near the corner of the domain generates several).
    """
    x = np.array([[0.5, 0.5, 0.5], [5.0, 5.0, 5.0]])
    radii = np.array([1.0, 1.0])
    spheres = spherepacking.Spheres(radii, x)
    domain = spherepacking.Domain(spheres=spheres, porosity=0)
    domain.length[:] = 10.0
    sp = spherepacking.SpherePack(domain, spheres, domain.length.copy(), x.shape[0])
    sp.gen_periodic_objects()

    pack_io = SpherePackIO(
        sp.domain,
        media_type="Ellipsoids",
        run_folder=str(tmp_path / "run"),
        out_folder=str(tmp_path / "out"),
        dim=dim,
        factor=factor,
    )
    ellipsoid_sp = pack_io.convert_to_ellipsoids(sp)
    return pack_io, ellipsoid_sp


def test_save_pack_stl_includes_periodic_ellipsoids(tmp_path):
    pack_io, sp = build_periodic_ellipsoid_pack(tmp_path)
    expected_total = sp.n_spheres + sp.n_b_p_spheres
    # Sanity check: periodic copies actually exist for this test to be meaningful.
    assert sp.n_b_p_spheres > 0

    fake_geom = MagicMock()
    fake_geom.__enter__ = MagicMock(return_value=fake_geom)
    fake_geom.__exit__ = MagicMock(return_value=False)
    fake_geom.generate_mesh.return_value = MagicMock()

    with patch(
        "spherepacking.sphere_pack_io.pygmsh.geo.Geometry", return_value=fake_geom
    ):
        pack_io.save_pack_stl(sp, "test_pack")

    assert fake_geom.add_ellipsoid.call_count == expected_total


if __name__ == "__main__":
    import tempfile
    import pathlib

    with tempfile.TemporaryDirectory() as tmp:
        test_save_pack_stl_includes_periodic_ellipsoids(pathlib.Path(tmp))
    print("OK")
