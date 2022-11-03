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
typedef uint32_t Uint32;
typedef uint16_t Uint16;
typedef uint8_t Uint8;
typedef int32_t Sint32;
typedef int16_t Sint16;
typedef Sint32 SDL_Keycode;

typedef struct SDL_version
{
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
} SDL_version;

void SDL_GetVersion(SDL_version * ver);

typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct SDL_PixelFormat SDL_PixelFormat;
typedef struct SDL_Texture SDL_Texture;
typedef struct SDL_BlitMap SDL_BlitMap;
typedef union SDL_Event SDL_Event;

int SDL_Init(uint32_t flags);
void SDL_Quit(void);

SDL_Window * SDL_CreateWindow(const char *title,
                              int x, int y, int w,
                              int h, uint32_t flags);
void SDL_DestroyWindow(SDL_Window * window);

typedef struct SDL_Point
{
    int x;
    int y;
} SDL_Point;

typedef struct SDL_FPoint
{
    float x;
    float y;
} SDL_FPoint;

typedef struct SDL_FRect
{
    float x;
    float y;
    float w;
    float h;
} SDL_FRect;

typedef struct SDL_Rect
{
    int x, y;
    int w, h;
} SDL_Rect;

typedef struct SDL_Surface
{
    uint32_t flags;
    SDL_PixelFormat *format;
    int w, h;
    int pitch;
    void *pixels;
    void *userdata;
    int locked;
    void *list_blitmap;
    SDL_Rect clip_rect;
    SDL_BlitMap *map;
    int refcount;
} SDL_Surface;


typedef struct SDL_Keysym
{
    int scancode;
    SDL_Keycode sym;
    Uint16 mod;
    Uint32 unused;
} SDL_Keysym;

typedef struct SDL_KeyboardEvent
{
    Uint32 type;
    Uint32 timestamp;
    Uint32 windowID;
    Uint8 state;
    Uint8 repeat;
    Uint8 padding2;
    Uint8 padding3;
    SDL_Keysym keysym;
} SDL_KeyboardEvent;

typedef struct SDL_MouseMotionEvent
{
    Uint32 type;
    Uint32 timestamp;
    Uint32 windowID;
    Uint32 which;
    Uint32 state;
    Sint32 x;
    Sint32 y;
    Sint32 xrel;
    Sint32 yrel;
} SDL_MouseMotionEvent;

typedef struct SDL_MouseButtonEvent
{
    Uint32 type;
    Uint32 timestamp;
    Uint32 windowID;
    Uint32 which;
    Uint8 button;
    Uint8 state;
    Uint8 clicks;
    Uint8 padding1;
    Sint32 x;
    Sint32 y;
} SDL_MouseButtonEvent;


typedef struct SDL_WindowEvent
{
    Uint32 type;
    Uint32 timestamp;
    Uint32 windowID;
    Uint8 event;
    Uint8 padding1;
    Uint8 padding2;
    Uint8 padding3;
    Sint32 data1;
    Sint32 data2;
} SDL_WindowEvent;

SDL_Renderer * SDL_CreateRenderer(SDL_Window * window,
                       int index, uint32_t flags);
void SDL_DestroyRenderer(SDL_Renderer * renderer);
int SDL_RenderClear(SDL_Renderer * renderer);
int SDL_RenderCopy(SDL_Renderer * renderer,
                   SDL_Texture * texture,
                   const SDL_Rect * srcrect,
                   const struct SDL_Rect * dstrect);
void SDL_RenderPresent(SDL_Renderer * renderer);
int SDL_RenderCopyExF(SDL_Renderer * renderer,
                    SDL_Texture * texture,
                    const SDL_Rect * srcrect,
                    const SDL_FRect * dstrect,
                    const double angle,
                    const SDL_FPoint *center,
                    const int flip);
int SDL_SetRenderDrawColor(SDL_Renderer * renderer,
                   Uint8 r, Uint8 g, Uint8 b,
                   Uint8 a);

SDL_Texture * SDL_CreateTextureFromSurface(SDL_Renderer * renderer, SDL_Surface * surface);
void SDL_DestroyTexture(SDL_Texture * texture);

SDL_Surface* SDL_LoadBMP(const char* file);
void SDL_FreeSurface(SDL_Surface * surface);

const char* SDL_GetError(void);
void SDL_Delay(uint32_t ms);
uint64_t SDL_GetTicks64(void);
uint64_t SDL_GetPerformanceCounter(void);
uint64_t SDL_GetPerformanceFrequency(void);

int IMG_Init(int flags);
void IMG_Quit(void);
SDL_Surface * IMG_Load(const char *file);

typedef struct Mix_Chunk Mix_Chunk;
int Mix_OpenAudio(int frequency, Uint16 format, int channels, int chunksize);
void Mix_CloseAudio(void);
Mix_Chunk * Mix_LoadWAV(const char *file);
int Mix_PlayChannel(int channel, Mix_Chunk *chunk, int loops);
void Mix_Resume(int channel);
void Mix_Pause(int channel);
int Mix_HaltChannel(int channel);
int Mix_VolumeChunk(Mix_Chunk *chunk, int volume);
void Mix_FreeChunk(Mix_Chunk *chunk);
int Mix_Volume(int channel, int volume);
int Mix_SetPosition(int channel, Sint16 angle, Uint8 distance);

int my_poll_event(void);
SDL_Event * get_my_event_ptr(void);
uint32_t my_get_event_type(void);
static const SDL_Event my_event;
"""
)

ffibuilder.set_source(
    '_mysdl2',
    """
#include <SDL.h>
#include <SDL_image.h>
#include <SDL_mixer.h>

SDL_Event my_event;

int my_poll_event(void) {
    return SDL_PollEvent(&my_event);
}

Uint32 my_get_event_type(void) {
    return my_event.type;
}

SDL_Event * get_my_event_ptr(void) {
    return &my_event;
}
""",
    extra_compile_args=[*sdl2_cflags],
    extra_link_args=[*sdl2_libs, '-lSDL2_image', '-lSDL2_mixer'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
