import os
import pathlib
import shutil
import subprocess

base_dir = pathlib.Path(__file__).parent
download_dir = base_dir / 'dl'
src_dir = base_dir / 'src'
prefix_dir = base_dir / 'prefix'
out_dir = base_dir / 'out'


def build_sdl():
    clear_dir(src_dir)
    clear_dir(prefix_dir)
    clear_dir(out_dir)

    unpack('SDL2-2.24.1.tar.gz')
    unpack('SDL2_image-2.6.2.tar.gz')
    unpack('SDL2_mixer-2.6.2.tar.gz')
    unpack('SDL2_ttf-2.20.1.tar.gz')

    build('SDL2-2.24.1', '--enable-rpath=no')

    with_sdl_prefix = f'--with-sdl-prefix={prefix_dir}'
    build('SDL2_image-2.6.2', with_sdl_prefix)
    build('SDL2_mixer-2.6.2', with_sdl_prefix)
    build('SDL2_ttf-2.20.1', with_sdl_prefix)

    set_rpath_to_origin(
        'libSDL2_image.so',
        'libSDL2_mixer.so',
        'libSDL2_ttf.so',
    )


def build(name, *opts):
    configure(name, *opts)
    make(name)
    make_install(name)


def unpack(name):
    print(f'Extracting {name}')
    full_path = download_dir / name
    subprocess.check_call(['tar', 'xf', full_path], cwd=src_dir)


def configure(name, *opts):
    cwd = src_dir / name
    subprocess.check_call(
        [cwd / 'configure', f'--prefix={prefix_dir}', *opts], cwd=cwd
    )


def set_rpath_to_origin(*names):
    print(f'Fixing rpath in {", ".join(names)}')
    paths = [prefix_dir / 'lib' / n for n in names]
    subprocess.check_call(['chrpath', '-r', '$ORIGIN', *paths])


def make(name):
    cwd = src_dir / name
    subprocess.check_call(['make', '-j12'], cwd=cwd)


def make_install(name):
    cwd = src_dir / name
    subprocess.check_call(['make', 'install'], cwd=cwd)


def clear_dir(d):
    print(f'Recreate {d}')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)


if __name__ == '__main__':
    build_sdl()
