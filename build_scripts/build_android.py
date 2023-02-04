import os
import pathlib
import shutil
import subprocess

base_dir = pathlib.Path(__file__).parent
download_dir = base_dir / 'dl'
src_dir = base_dir / 'src'
prefix_dir = base_dir / 'prefix'
out_dir = base_dir.parent / 'gaem_libs'

CMAKE = '/home/denis/Android/Sdk/cmake/3.22.1/bin/cmake'
ANDROID_NDK_HOME = '/home/denis/sdk/android-ndk-r25b'
TOOLCHAIN = f'{ANDROID_NDK_HOME}/toolchains/llvm/prebuilt/linux-x86_64'
PATH = f'{TOOLCHAIN}/bin:{os.environ["PATH"]}'
TARGET = 'aarch64-linux-android'  # TODO: build for all targets
API = '21'
AR = f'{TOOLCHAIN}/bin/llvm-ar'
CC = f'{TOOLCHAIN}/bin/{TARGET}{API}-clang'
AS = CC
CXX = f'{TOOLCHAIN}/bin/{TARGET}{API}-clang++'
LD = f'{TOOLCHAIN}/bin/ld'
RANLIB = f'{TOOLCHAIN}/bin/llvm-ranlib'
STRIP = f'{TOOLCHAIN}/bin/llvm-strip'
READELF = f'{TOOLCHAIN}/bin/llvm-readelf'
PKG_CONFIG_LIBDIR = f'{prefix_dir}/lib/pkgconfig'


def export(name, val):
    os.environ[name] = val


export('ANDROID_NDK_HOME', ANDROID_NDK_HOME)
export('TOOLCHAIN', TOOLCHAIN)
export('PATH', PATH)
export('TARGET', TARGET)
export('API', API)
export('AR', AR)
export('CC', CC)
export('AS', AS)
export('CXX', CXX)
export('LD', LD)
export('RANLIB', RANLIB)
export('STRIP', STRIP)
export('READELF', READELF)
export('PKG_CONFIG_LIBDIR', PKG_CONFIG_LIBDIR)


def build_world():
    clear_dir(src_dir)
    clear_dir(prefix_dir)
    clear_dir(out_dir)
    unpack('Python-3.11.1.tar.xz')
    unpack('util-linux-2.38.1.tar.gz')
    unpack('sqlite-autoconf-3400100.tar.gz')
    unpack('xz-5.4.1.tar.xz')
    unpack('openssl-1.1.1s.tar.gz')
    unpack('libffi-3.4.4.tar.gz')
    unpack('bzip2-latest.tar.gz')
    unpack('SDL2-2.26.2.tar.gz')
    unpack('SDL2_image-2.6.2.tar.gz')
    unpack('SDL2_ttf-2.20.1.tar.gz')
    unpack('SDL2_mixer-2.6.2.tar.gz')
    download_mixer_deps('SDL2_mixer-2.6.2')
    build_bzip2('bzip2-1.0.8')
    build_openssl('openssl-1.1.1s')
    build('xz-5.4.1')
    build('sqlite-autoconf-3400100')
    build('libffi-3.4.4')
    autogen('util-linux-2.38.1')
    build(
        'util-linux-2.38.1',
        '--disable-all-programs',
        '--enable-libuuid',
    )
    build(
        'Python-3.11.1',
        '--build=x86_64-pc-linux-gnu',
        'ac_cv_file__dev_ptmx=yes',
        'ac_cv_file__dev_ptc=no',
        'ac_cv_buggy_getaddrinfo=no',
        f'CPPFLAGS=-I{prefix_dir}/include',
        f'LDFLAGS=-L{prefix_dir}/lib',
        '--disable-test-modules',
        '--with-build-python=python3.11',
        '--with-system-ffi',
        '--without-readline',
    )
    build(
        'SDL2-2.26.2',
        '--enable-hidapi=no',
        '--enable-rpath=no',
        'LDFLAGS=-lOpenSLES',
    )
    cmake_build('SDL2_image-2.6.2', '-DSDL2IMAGE_SAMPLES=off')
    cmake_build(
        'SDL2_ttf-2.20.1', '-DSDL2TTF_VENDORED=on', '-DSDL2TTF_SAMPLES=off'
    )
    cmake_build(
        'SDL2_mixer-2.6.2',
        '-DSDL2MIXER_VENDORED=ON',
        '-DSDL2MIXER_SAMPLES=OFF',
    )
    # TODO:
    # python3.11 -m venv crossenv_build
    # venv_build/bin/pip install crossenv cffi
    # venv_build/bin/python -m crossenv /home/denis/private/prg/gaem/build_scripts/prefix/bin/python3 cross_venv
    # cross_venv/bin/cross-pip install cffi
    # venv_build/bin/python gaem_build --only_emit_c_code _gaem.c
    # compile _gaem.c into _gaem.so
    # copy to out_dir everything we need
    # fiddle with rpaths?


def unpack(name):
    print(f'Extracting {name}')
    full_path = download_dir / name
    subprocess.check_call(['tar', 'xf', full_path], cwd=src_dir)


def clear_dir(d):
    print(f'Recreate {d}')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)


def autogen(name):
    cwd = src_dir / name
    subprocess.check_call([cwd / 'autogen.sh'], cwd=cwd)


def build_openssl(name):
    cwd = src_dir / name
    subprocess.check_call(
        [
            cwd / 'Configure',
            'android-arm64',  # TODO: switch depending on TARGET
            f'-D__ANDROID_API__={API}',
            f'--prefix={prefix_dir}',
            f'--openssldir={prefix_dir}',
        ],
        cwd=cwd,
    )
    subprocess.check_call(['make', '-j12'], cwd=cwd)
    subprocess.check_call(['make', 'install_sw'], cwd=cwd)


def build_bzip2(name):
    cwd = src_dir / name
    subprocess.check_call(
        ['make', '-j12', f'CC={CC}', f'AR={AR}', f'RANLIB={RANLIB}', 'bzip2'],
        cwd=cwd,
    )
    subprocess.check_call(['make', f'PREFIX={prefix_dir}', 'install'], cwd=cwd)


def cmake_build(name, *opts):
    cwd = src_dir / name / 'build'
    cwd.mkdir(exist_ok=True)
    subprocess.check_call(
        [
            CMAKE,
            '..',
            f'-DCMAKE_INSTALL_PREFIX={prefix_dir}',
            f'-DCMAKE_PREFIX_PATH={prefix_dir}',
            f'-DCMAKE_TOOLCHAIN_FILE={ANDROID_NDK_HOME}/build/cmake/android.toolchain.cmake',
            f'-DANDROID_PLATFORM={API}',
            f'-DANDROID_TOOLCHAIN_NAME={TARGET}',
            '-DANDROID_ABI=arm64-v8a',  # TODO: Detect depending on target?
            f'-DSDL2_LIBRARY={prefix_dir}/lib/libSDL2-2.0.so',
            f'-DSDL2_INCLUDE_DIR={prefix_dir}/include/SDL2',
            *opts,
        ],
        cwd=cwd,
    )
    subprocess.check_call(['make', '-j12'], cwd=cwd)
    subprocess.check_call(['make', 'install'], cwd=cwd)


def download_mixer_deps(name):
    cwd = src_dir / name / 'external'
    subprocess.check_call([cwd / 'download.sh'], cwd=cwd)


def build(name, *opts):
    configure(name, *opts)
    make(name)
    make_install(name)


def configure(name, *opts):
    cwd = src_dir / name
    subprocess.check_call(
        [
            cwd / 'configure',
            f'--prefix={prefix_dir}',
            f'--host={TARGET}',
            *opts,
        ],
        cwd=cwd,
    )


def make(name):
    cwd = src_dir / name
    subprocess.check_call(['make', '-j12'], cwd=cwd)


def make_install(name):
    cwd = src_dir / name
    subprocess.check_call(['make', 'install'], cwd=cwd)


if __name__ == '__main__':
    build_world()
