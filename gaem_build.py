import subprocess
import sys
from pathlib import Path

from cffi import FFI

cflags = []
ldflags = []

if sys.platform == 'linux':
    sdl2_config = Path(__file__).parent / Path(
        'build_scripts', 'prefix', 'bin', 'sdl2-config'
    )

    cflags += subprocess.run(
        [sdl2_config, '--cflags'], stdout=subprocess.PIPE, encoding='utf-8'
    ).stdout.split()
    ldflags += subprocess.run(
        [sdl2_config, '--libs'], stdout=subprocess.PIPE, encoding='utf-8'
    ).stdout.split()

    ldflags += ['-lSDL2_image', '-lSDL2_mixer', '-lSDL2_ttf']
    ldflags += ['-Wl,-rpath=$ORIGIN/gaem_libs']
elif sys.platform == 'win32':
    include_dir = Path(__file__).parent / Path(
        'build_scripts', 'prefix', 'include'
    )
    lib_dir = Path(__file__).parent / Path('build_scripts', 'prefix', 'lib')
    cflags += ['/I', str(include_dir)]
    ldflags += [
        f'/LIBPATH:{lib_dir}',
        'SDL2.lib',
        'SDL2_image.lib',
        'SDL2_mixer.lib',
        'SDL2_ttf.lib',
    ]

ffibuilder = FFI()

ffibuilder.cdef(
    """
typedef uint32_t Uint32;
typedef uint16_t Uint16;
typedef uint8_t Uint8;
typedef int32_t Sint32;
typedef int16_t Sint16;
typedef Sint32 SDL_Keycode;

typedef int SDL_bool;

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

typedef Sint32 SDL_JoystickID;
typedef struct _SDL_GameController SDL_GameController;
typedef struct _SDL_Joystick SDL_Joystick;
SDL_GameController* SDL_GameControllerOpen(int joystick_index);
SDL_Joystick* SDL_GameControllerGetJoystick(SDL_GameController *gamecontroller);
SDL_JoystickID SDL_JoystickInstanceID(SDL_Joystick *joystick);
SDL_bool SDL_IsGameController(int joystick_index);
Sint16 SDL_GameControllerGetAxis(SDL_GameController *gamecontroller, int axis);
Uint8 SDL_GameControllerGetButton(SDL_GameController *gamecontroller,
                                  int button);

typedef struct SDL_ControllerDeviceEvent
{
    Uint32 type;
    Uint32 timestamp;
    Sint32 which;
} SDL_ControllerDeviceEvent;

typedef struct SDL_ControllerButtonEvent
{
    Uint32 type;
    Uint32 timestamp;
    SDL_JoystickID which;
    Uint8 button;
    Uint8 state;
    Uint8 padding1;
    Uint8 padding2;
} SDL_ControllerButtonEvent;

typedef struct SDL_ControllerAxisEvent
{
    Uint32 type;
    Uint32 timestamp;
    SDL_JoystickID which;
    Uint8 axis;
    Uint8 padding1;
    Uint8 padding2;
    Uint8 padding3;
    Sint16 value;
    Uint16 padding4;
} SDL_ControllerAxisEvent;

typedef struct SDL_Color
{
    Uint8 r;
    Uint8 g;
    Uint8 b;
    Uint8 a;
} SDL_Color;

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
int SDL_RenderDrawRect(SDL_Renderer * renderer,
                       const SDL_Rect * rect);
int SDL_RenderFillRect(SDL_Renderer * renderer,
                       const SDL_Rect * rect);
int SDL_RenderDrawLine(SDL_Renderer * renderer,
                       int x1, int y1, int x2, int y2);
int SDL_SetRenderDrawBlendMode(SDL_Renderer * renderer,
                               int blendMode);
int SDL_SetSurfaceBlendMode(SDL_Surface * surface,
                            int blendMode);
int SDL_SetTextureBlendMode(SDL_Texture * texture,
                            int blendMode);
int SDL_SetTextureColorMod(SDL_Texture * texture,
                           Uint8 r, Uint8 g, Uint8 b);
int SDL_SetTextureAlphaMod(SDL_Texture * texture,
                           Uint8 alpha);
int SDL_RenderSetClipRect(SDL_Renderer * renderer,
                          const SDL_Rect * rect);
SDL_Surface* SDL_CreateRGBSurface
    (Uint32 flags, int width, int height, int depth,
     Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask);
int SDL_BlitSurface(SDL_Surface*    src,
                    const SDL_Rect* srcrect,
                    SDL_Surface*    dst,
                    SDL_Rect*       dstrect);

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
typedef struct Mix_Music Mix_Music;
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
void Mix_ChannelFinished(void (*channel_finished)(int channel));
int Mix_MasterVolume(int volume);
int Mix_VolumeMusic(int volume);
int Mix_HaltMusic(void);
Mix_Music * Mix_LoadMUS(const char *file);
int Mix_PlayMusic(Mix_Music *music, int loops);
void Mix_HookMusicFinished(void (*music_finished)(void));
void Mix_PauseMusic(void);
void Mix_ResumeMusic(void);
void Mix_FreeMusic(Mix_Music *music);

int gaem_poll_event(void);
SDL_Event * gaem_get_event_ptr(void);
uint32_t gaem_get_event_type(void);
static const SDL_Event gaem_event;

extern "Python" void channel_finished_callback(int channel);
extern "Python" void music_finished_callback(void);

int TTF_Init(void);
void TTF_Quit(void);
typedef struct _TTF_Font TTF_Font;
TTF_Font * TTF_OpenFont(const char *file, int ptsize);
SDL_Surface * TTF_RenderUTF8_Blended(TTF_Font *font,
                const char *text, SDL_Color fg);
SDL_Surface * TTF_RenderGlyph32_Blended(TTF_Font *font,
                Uint32 ch, SDL_Color fg);
int TTF_GetFontKerningSizeGlyphs32(TTF_Font *font, Uint32 previous_ch, Uint32 ch);
int TTF_FontLineSkip(const TTF_Font *font);
void TTF_CloseFont(TTF_Font *font);
"""
)

ffibuilder.set_source(
    '_gaem',
    """
#include <SDL.h>
#include <SDL_image.h>
#include <SDL_mixer.h>
#include <SDL_ttf.h>

SDL_Event gaem_event;

int gaem_poll_event(void) {
    return SDL_PollEvent(&gaem_event);
}

Uint32 gaem_get_event_type(void) {
    return gaem_event.type;
}

SDL_Event * gaem_get_event_ptr(void) {
    return &gaem_event;
}
""",
    extra_compile_args=cflags,
    extra_link_args=ldflags,
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
