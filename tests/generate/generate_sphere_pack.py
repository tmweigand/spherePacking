import spherepacking

run_folder = "temp"

# Delete sphere pack files so runs
spherepacking.remove_dir(run_folder)

# Determine radii distribution 
radii = spherepacking.SphereRadii(
    n = 50,
    distribution='lognormal',
    mean=1,
    stdev=0,
    run_folder =run_folder
)

spheres = spherepacking.Spheres(radii.radii)

domain = spherepacking.Domain(
    spheres=spheres,
    porosity=0.4
)

domain.gen_min_cube()

packIO = spherepacking.SpherePackIO(domain,media_type = 'Spheres',run_folder = run_folder, out_folder="data_out")

sp = packIO.generate_sphere_pack(seed = 6, periodic=True)
# packIO.save_pack_txt(sp,"uniform")
# packIO.save_pack_stl(sp,"uniform")
packIO.save_openfoam(sp,'uniform_openfoam')