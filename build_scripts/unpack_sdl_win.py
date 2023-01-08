import glob
import os
import pathlib
import shutil
import zipfile

base_dir = pathlib.Path(__file__).parent
download_dir = base_dir / 'dl'
extract_dir = base_dir / 'extract'
prefix_dir = base_dir / 'prefix'
include_dir = prefix_dir / 'include'
lib_dir = prefix_dir / 'lib'
out_dir = base_dir.parent / 'gaem_libs'


def unpack_sdl_win():
    clear_dir(extract_dir)
    clear_dir(prefix_dir)
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    clear_dir(out_dir)
    extract('SDL2-devel-2.26.2-VC.zip')
    extract('SDL2_image-devel-2.6.2-VC.zip')
    extract('SDL2_mixer-devel-2.6.2-VC.zip')
    extract('SDL2_ttf-devel-2.20.1-VC.zip')
    copy_includes_and_libs()
    copy_dll('SDL2.dll')
    copy_dll('SDL2_image.dll')
    copy_dll('SDL2_mixer.dll')
    copy_dll('SDL2_ttf.dll')


def extract(zip_name):
    print(f'Extract {zip_name}')
    with zipfile.ZipFile(download_dir / zip_name) as f:
        f.extractall(extract_dir)


def copy_includes_and_libs():
    print('Copying includes and lib files')
    for n in glob.iglob(str(extract_dir / '*' / 'include' / '*.h')):
        shutil.copy(n, include_dir)

    for n in glob.iglob(str(extract_dir / '*' / 'lib' / 'x64' / '*.dll')):
        shutil.copy(n, lib_dir)

    for n in glob.iglob(str(extract_dir / '*' / 'lib' / 'x64' / '*.lib')):
        shutil.copy(n, lib_dir)


def clear_dir(d):
    print(f'Recreate {d}')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)


def copy_dll(dll):
    print(f'Copy dll {dll}')
    shutil.copy(lib_dir / dll, out_dir)


if __name__ == '__main__':
    unpack_sdl_win()
