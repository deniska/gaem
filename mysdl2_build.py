import subprocess

from cffi import FFI

sdl2_config = '/home/denis/sdk/sdl2/bin/sdl2-config'

sdl2_cflags = subprocess.run(
    [sdl2_config, '--cflags'], stdout=subprocess.PIPE, encoding='utf-8'
).stdout.split()
sdl2_libs = subprocess.run(
    [sdl2_config, '--libs'], stdout=subprocess.PIPE, encoding='utf-8'
).stdout.split()

ffibuilder = FFI()

ffibuilder.cdef(
    """
typedef struct SDL_version
{
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
} SDL_version;

void SDL_GetVersion(SDL_version * ver);

typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct SDL_Surface SDL_Surface;
typedef struct SDL_Texture SDL_Texture;

int SDL_Init(uint32_t flags);
void SDL_Quit(void);

SDL_Window * SDL_CreateWindow(const char *title,
                              int x, int y, int w,
                              int h, uint32_t flags);
void SDL_DestroyWindow(SDL_Window * window);

struct SDL_Point
{
    int x;
    int y;
};

struct SDL_FPoint
{
    float x;
    float y;
};

struct SDL_FRect
{
    float x;
    float y;
    float w;
    float h;
};

SDL_Renderer * SDL_CreateRenderer(SDL_Window * window,
                       int index, uint32_t flags);
void SDL_DestroyRenderer(SDL_Renderer * renderer);
int SDL_RenderClear(SDL_Renderer * renderer);
int SDL_RenderCopy(SDL_Renderer * renderer,
                   SDL_Texture * texture,
                   const struct SDL_Rect * srcrect,
                   const struct SDL_Rect * dstrect);
void SDL_RenderPresent(SDL_Renderer * renderer);

SDL_Texture * SDL_CreateTextureFromSurface(SDL_Renderer * renderer, SDL_Surface * surface);
void SDL_DestroyTexture(SDL_Texture * texture);

SDL_Surface* SDL_LoadBMP(const char* file);
void SDL_FreeSurface(SDL_Surface * surface);

const char* SDL_GetError(void);
void SDL_Delay(uint32_t ms);
uint64_t SDL_GetTicks64(void);
uint64_t SDL_GetPerformanceCounter(void);
uint64_t SDL_GetPerformanceFrequency(void);

int my_poll_event(void);
uint32_t my_get_event_type(void);
"""
)

ffibuilder.set_source(
    '_mysdl2',
    """
#include <SDL.h>

SDL_Event my_event;

int my_poll_event(void) {
    return SDL_PollEvent(&my_event);
}

Uint32 my_get_event_type(void) {
    return my_event.type;
}
""",
    extra_compile_args=[*sdl2_cflags],
    extra_link_args=[*sdl2_libs],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
