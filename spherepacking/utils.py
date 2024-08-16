import os


def remove_file(file):
    """
    Remove files if exists
    """
    if os.path.isfile(file):
        os.remove(file)


def remove_dir(folder):
    """
    Ensure run folder is empty
    """
    cwd = os.getcwd()
    pathway = cwd + "/" + folder
    if os.path.isdir(pathway):
        clean_directory(pathway)
    check_folder_path(folder)

def clean_directory(run_path):
    """
    Clean the directory
    """
    remove_file(run_path + "/contraction_energies.txt")
    remove_file(run_path + "/packing_init.xyzd")
    remove_file(run_path + "/packing.nfo")
    remove_file(run_path + "/packing.xyzd")
    remove_file(run_path + "/packing_prev.xyzd")
    remove_file(run_path + "/diameters.txt")
    remove_file(run_path + "/generation.conf")
    


def check_folder_path(folder):
    """
    Ensure pathways exists, if not make it
    """
    cwd = os.getcwd()
    pathway = cwd + "/" +  folder
    print(cwd,pathway)
    if not os.path.isdir(pathway):
        os.makedirs(pathway)