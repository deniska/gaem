import os
import pathlib
import shutil
import subprocess

base_dir = pathlib.Path(__file__).parent
download_dir = base_dir / 'dl'
src_dir = base_dir / 'src'
prefix_dir = base_dir / 'prefix'
out_dir = base_dir.parent / 'gaem_libs'

ANDROID_NDK_HOME = '/home/denis/sdk/android-ndk-r25b'
TOOLCHAIN = f'{ANDROID_NDK_HOME}/toolchains/llvm/prebuilt/linux-x86_64'
PATH = f'{TOOLCHAIN}/bin:{os.environ["PATH"]}'
TARGET = 'aarch64-linux-android'
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
        '--with-build-python',
    )


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
            'android-arm64',
            f'-D__ANDROID_API__={API}',
            f'--prefix={prefix_dir}',
            f'--openssldir={prefix_dir}',
        ],
        cwd=cwd,
    )
    subprocess.check_call(['make', '-j12'], cwd=cwd)
    subprocess.check_call(['make', 'install_sw'], cwd=cwd)


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
