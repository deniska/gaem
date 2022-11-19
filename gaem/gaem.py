import enum
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import _gaem

NULL = _gaem.ffi.NULL

SDL_WINDOWPOS_CENTERED = 0x2FFF0000
SDL_WINDOWPOS_UNDEFINED = 0x1FFF0000

SDL_WINDOW_RESIZABLE = 0x00000020

SDL_RENDERER_SOFTWARE = 0x00000001
SDL_RENDERER_ACCELERATED = 0x00000002
SDL_RENDERER_PRESENTVSYNC = 0x00000004
SDL_RENDERER_TARGETTEXTURE = 0x00000008

IMG_INIT_PNG = 0x00000002
IMG_INIT_JPG = 0x00000001

SDL_INIT_EVERYTHING = 62001

SDL_QUIT = 0x100
SDL_KEYDOWN = 0x300
SDL_KEYUP = 0x301
SDL_TEXTEDITING = 0x302
SDL_TEXTINPUT = 0x303
SDL_KEYMAPCHANGED = 0x304
SDL_TEXTEDITING_EXT = 0x305

SDL_JOYAXISMOTION = 0x600
SDL_JOYBALLMOTION = 0x601
SDL_JOYHATMOTION = 0x602
SDL_JOYBUTTONDOWN = 0x603
SDL_JOYBUTTONUP = 0x604
SDL_JOYDEVICEADDED = 0x605
SDL_JOYDEVICEREMOVED = 0x606

SDL_CONTROLLERAXISMOTION = 0x650
SDL_CONTROLLERBUTTONDOWN = 0x651
SDL_CONTROLLERBUTTONUP = 0x652
SDL_CONTROLLERDEVICEADDED = 0x653
SDL_CONTROLLERDEVICEREMOVED = 0x654

SDL_CONTROLLER_AXIS_LEFTX = 0
SDL_CONTROLLER_AXIS_LEFTY = 1
SDL_CONTROLLER_AXIS_RIGHTX = 2
SDL_CONTROLLER_AXIS_RIGHTY = 3
SDL_CONTROLLER_AXIS_TRIGGERLEFT = 4
SDL_CONTROLLER_AXIS_TRIGGERRIGHT = 5

SDL_MOUSEMOTION = 0x400
SDL_MOUSEBUTTONDOWN = 0x401
SDL_MOUSEBUTTONUP = 0x402
SDL_MOUSEWHEEL = 0x403

SDL_WINDOWEVENT = 0x200

SDL_WINDOWEVENT_SIZE_CHANGED = 6

SDL_FLIP_HORIZONTAL = 0x00000001
SDL_FLIP_VERTICAL = 0x00000002

SDLK_SCANCODE_MASK = 1 << 30

AUDIO_S16LSB = 0x8010
SDL_MIX_MAXVOLUME = 128

WHITE = (255, 255, 255)


class BlendMode(enum.IntEnum):
    NONE = 0x00000000
    BLEND = 0x00000001
    ADD = 0x00000002
    MOD = 0x00000004
    MUL = 0x00000008


class TextAlign(enum.Enum):
    LEFT = enum.auto()
    CENTER = enum.auto()
    RIGHT = enum.auto()
    # todo: justified?


class g:  # yes, globals, wanna fight?
    win = None
    ren = None
    should_quit = False
    screen_width = 0
    screen_height = 0
    pressed_keys = set()
    mouse_x = 0
    mouse_y = 0
    pressed_mouse_buttons = set()
    background_color = (0, 0, 0, 255)
    music_finished = False
    gamepads = {}


def run(
    game,
    *,
    title='Gaem',
    width=800,
    height=480,
    x=None,
    y=None,
    vsync=False,
    resizable=False,
):
    ret = _gaem.lib.SDL_Init(SDL_INIT_EVERYTHING)
    raise_for_neg(ret)

    img_flags = IMG_INIT_PNG | IMG_INIT_JPG
    if img_flags != _gaem.lib.IMG_Init(img_flags):
        raise GaemError('Failed to initialize SDL_Image')

    ret = _gaem.lib.Mix_OpenAudio(44100, AUDIO_S16LSB, 2, 512)
    raise_for_neg(ret)
    _gaem.lib.Mix_ChannelFinished(_gaem.lib.channel_finished_callback)
    _gaem.lib.Mix_HookMusicFinished(_gaem.lib.music_finished_callback)

    ret = _gaem.lib.TTF_Init()
    raise_for_neg(ret)

    if x is None:
        x = SDL_WINDOWPOS_CENTERED
    if y is None:
        y = SDL_WINDOWPOS_CENTERED
    title = to_cstr(title)
    flags = 0
    if resizable:
        flags |= SDL_WINDOW_RESIZABLE
    g.screen_width = width
    g.screen_height = height
    g.win = _gaem.lib.SDL_CreateWindow(title, x, y, width, height, flags)
    raise_for_null(g.win)

    flags = SDL_RENDERER_ACCELERATED
    if vsync:
        flags |= SDL_RENDERER_PRESENTVSYNC
    g.ren = _gaem.lib.SDL_CreateRenderer(g.win, -1, flags)
    raise_for_null(g.ren)

    game.on_load()

    previous_ticks = None
    counter_resolution = _gaem.lib.SDL_GetPerformanceFrequency()

    sdl2_event = _gaem.lib.gaem_get_event_ptr()
    while not g.should_quit:
        while _gaem.lib.gaem_poll_event():
            ev_type = _gaem.lib.gaem_get_event_type()
            if ev_type == SDL_QUIT:
                ret = game.on_quit()
                g.should_quit = bool(ret)
            elif ev_type == SDL_KEYDOWN:
                sdl_kb_event = _gaem.ffi.cast(
                    'SDL_KeyboardEvent *', sdl2_event
                )
                if sdl_kb_event.repeat:
                    continue
                event = KeyboardEvent.from_sdl_event(sdl_kb_event)
                g.pressed_keys.add(event.scancode)
                game.on_keydown(event)
            elif ev_type == SDL_KEYUP:
                sdl_kb_event = _gaem.ffi.cast(
                    'SDL_KeyboardEvent *', sdl2_event
                )
                event = KeyboardEvent.from_sdl_event(sdl_kb_event)
                g.pressed_keys.discard(event.scancode)
                game.on_keyup(event)
            elif ev_type == SDL_MOUSEMOTION:
                sdl_mouse_motion_event = _gaem.ffi.cast(
                    'SDL_MouseMotionEvent *', sdl2_event
                )
                event = MouseMotionEvent.from_sdl_event(sdl_mouse_motion_event)
                g.mouse_x = event.x
                g.mouse_y = event.y
                game.on_mousemotion(event)
            elif ev_type == SDL_MOUSEBUTTONDOWN:
                sdl_mouse_button_event = _gaem.ffi.cast(
                    'SDL_MouseButtonEvent *', sdl2_event
                )
                event = MouseButtonEvent.from_sdl_event(sdl_mouse_button_event)
                g.mouse_x = event.x
                g.mouse_y = event.y
                g.pressed_mouse_buttons.add(event.button)
                game.on_mousedown(event)
            elif ev_type == SDL_MOUSEBUTTONUP:
                sdl_mouse_button_event = _gaem.ffi.cast(
                    'SDL_MouseButtonEvent *', sdl2_event
                )
                event = MouseButtonEvent.from_sdl_event(sdl_mouse_button_event)
                g.mouse_x = event.x
                g.mouse_y = event.y
                g.pressed_mouse_buttons.discard(event.button)
                game.on_mouseup(event)
            elif ev_type == SDL_WINDOWEVENT:
                sdl_window_event = _gaem.ffi.cast(
                    'SDL_WindowEvent *', sdl2_event
                )
                if sdl_window_event.event == SDL_WINDOWEVENT_SIZE_CHANGED:
                    event = ResizeEvent(
                        width=sdl_window_event.data1,
                        height=sdl_window_event.data2,
                    )
                    g.screen_width = event.width
                    g.screen_height = event.height
                    game.on_resize(event)
            elif ev_type == SDL_CONTROLLERDEVICEADDED:
                sdl_controller_event = _gaem.ffi.cast(
                    'SDL_ControllerDeviceEvent *', sdl2_event
                )
                idx = sdl_controller_event.which
                if not _gaem.lib.SDL_IsGameController(idx):
                    continue
                controller = _gaem.lib.SDL_GameControllerOpen(idx)
                raise_for_null(controller)
                joystick = _gaem.lib.SDL_GameControllerGetJoystick(controller)
                raise_for_null(joystick)
                instance_id = _gaem.lib.SDL_JoystickInstanceID(joystick)
                gamepad = Gamepad(controller)
                g.gamepads[instance_id] = gamepad
                game.on_gamepad_connected(gamepad)
            elif ev_type == SDL_CONTROLLERDEVICEREMOVED:
                sdl_controller_event = _gaem.ffi.cast(
                    'SDL_ControllerDeviceEvent *', sdl2_event
                )
                gamepad = g.gamepads.pop(sdl_controller_event.which)
                game.on_gamepad_disconnected(gamepad)
            elif ev_type == SDL_CONTROLLERBUTTONDOWN:
                sdl_controller_event = _gaem.ffi.cast(
                    'SDL_ControllerButtonEvent *', sdl2_event
                )
                gamepad = g.gamepads.get(sdl_controller_event.which)
                event = GamepadButtonEvent(
                    gamepad=gamepad,
                    button=gamepad_button_names[sdl_controller_event.button],
                )
                game.on_gamepad_button_down(event)
            elif ev_type == SDL_CONTROLLERBUTTONUP:
                sdl_controller_event = _gaem.ffi.cast(
                    'SDL_ControllerButtonEvent *', sdl2_event
                )
                gamepad = g.gamepads.get(sdl_controller_event.which)
                event = GamepadButtonEvent(
                    gamepad=gamepad,
                    button=gamepad_button_names[sdl_controller_event.button],
                )
                game.on_gamepad_button_up(event)
            elif ev_type == SDL_CONTROLLERAXISMOTION:
                sdl_controller_event = _gaem.ffi.cast(
                    'SDL_ControllerAxisEvent *', sdl2_event
                )
                gamepad = g.gamepads.get(sdl_controller_event.which)
                event = GamepadAxisEvent(
                    gamepad=gamepad,
                    axis=gamepad_axis_names[sdl_controller_event.axis],
                    value=sdl_controller_event.value / 32767,
                )
                game.on_gamepad_axis_motion(event)
            if g.music_finished:
                g.music_finished = False
                game.on_music_finished()
        if g.music_finished:  # again in case we polled no sdl events
            g.music_finished = False
            game.on_music_finished()
        _gaem.lib.SDL_SetRenderDrawColor(g.ren, *g.background_color)
        _gaem.lib.SDL_RenderClear(g.ren)
        if previous_ticks:
            current_ticks = _gaem.lib.SDL_GetPerformanceCounter()
            dt = (current_ticks - previous_ticks) / counter_resolution
            previous_ticks = current_ticks
            game.on_update(dt)
        else:
            previous_ticks = _gaem.lib.SDL_GetPerformanceCounter()
        game.on_draw()
        _gaem.lib.SDL_RenderPresent(g.ren)

    del game

    _gaem.lib.SDL_DestroyRenderer(g.ren)
    _gaem.lib.SDL_DestroyWindow(g.win)
    _gaem.lib.Mix_CloseAudio()
    _gaem.lib.TTF_Quit()
    _gaem.lib.IMG_Quit()
    _gaem.lib.SDL_Quit()


class Image:
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width = width
        self.height = height
        self._srcrect = _gaem.ffi.new('SDL_Rect *')
        self._srcrect.x = 0
        self._srcrect.y = 0
        self._srcrect.w = width
        self._srcrect.h = height
        self._dstrect = _gaem.ffi.new('SDL_FRect *')
        self._center = _gaem.ffi.new('SDL_FPoint *')
        self.x = 0.0
        self.y = 0.0
        self.sx = 1.0
        self.sy = 1.0
        self.cx = 0.0
        self.cy = 0.0
        self.angle = 0.0
        self.color = (255, 255, 255, 255)

    def draw(
        self,
        *,
        x=None,
        y=None,
        sx=None,
        sy=None,
        cx=None,
        cy=None,
        angle=None,
        renderer=None,
        color=None,
    ):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if sx is None:
            sx = self.sx
        if sy is None:
            sy = self.sy
        if cx is None:
            cx = self.cx
        if cy is None:
            cy = self.cy
        if angle is None:
            angle = self.angle
        if renderer is None:
            renderer = g.ren
        if color is None:
            color = self.color
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        flip_flags = 0
        if sx < 0:
            sx = -sx
            cx = self.width - cx
            flip_flags |= SDL_FLIP_HORIZONTAL
        elif sy < 0:
            sy = -sy
            cy = self.height - cy
            flip_flags |= SDL_FLIP_VERTICAL
        dstrect = self._dstrect
        center = self._center
        offset_x = cx * sx
        offset_y = cy * sy
        dstrect.x = x - offset_x
        dstrect.y = y - offset_y
        dstrect.w = self.width * sx
        dstrect.h = self.height * sy
        center.x = offset_x
        center.y = offset_y
        ret = _gaem.lib.SDL_SetTextureColorMod(
            self.texture.ptr, color[0], color[1], color[2]
        )
        raise_for_neg(ret)
        ret = _gaem.lib.SDL_SetTextureAlphaMod(self.texture.ptr, color[3])
        raise_for_neg(ret)
        ret = _gaem.lib.SDL_RenderCopyExF(
            renderer,
            self.texture.ptr,
            self._srcrect,
            dstrect,
            -angle / math.tau * 360.0,
            center,
            flip_flags,
        )
        raise_for_neg(ret)

    def center(self):
        self.cx = self.width / 2
        self.cy = self.height / 2

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def subregion(self, x, y, w, h):
        img = Image(self.texture, w, h)
        img._srcrect.x = self._srcrect.x + x
        img._srcrect.y = self._srcrect.y + y
        img._srcrect.w = w
        img._srcrect.h = h
        return img

    def copy(self):
        img = Image(self.texture, self.width, self.height)
        img._srcrect.x = self._srcrect.x
        img._srcrect.y = self._srcrect.y
        img._srcrect.w = self._srcrect.w
        img._srcrect.h = self._srcrect.h
        img.x = self.x
        img.y = self.y
        img.sx = self.sx
        img.sy = self.sy
        img.cx = self.cx
        img.cy = self.cy
        img.angle = self.angle
        return img


class Sound:
    def __init__(self, chunk):
        self.chunk = chunk

    def play(
        self,
        *,
        channel_id=-1,
        looping=False,
        volume=1.0,
        angle=math.tau / 4,
        distance=0.0,
    ):
        if looping:
            loops = -1
        else:
            loops = 0
        ret = _gaem.lib.Mix_PlayChannel(channel_id, self.chunk, loops)
        if ret == -1:
            return None
        channel = Channel.get_or_create(ret)
        channel.set_volume(volume)
        channel.set_position(angle, distance)
        return channel

    def __del__(self):
        _gaem.lib.Mix_FreeChunk(self.chunk)

    @property
    def volume(self):
        return _gaem.lib.Mix_VolumeChunk(self.chunk, -1) / SDL_MIX_MAXVOLUME

    @volume.setter
    def volume(self, val):
        _gaem.lib.Mix_VolumeChunk(self.chunk, int(val * SDL_MIX_MAXVOLUME))

    def looper(self):
        return SoundPlayer(self, looping=True)

    def player(self):
        return SoundPlayer(self, looping=False)


class SoundPlayer:
    def __init__(self, sound, *, looping):
        self.sound = sound
        self.channel = None
        self.looping = looping
        self._volume = 1.0
        self._angle = math.tau / 4
        self._distance = 0.0
        self._finish_callback = None

    def play(self):
        if self.channel is None:
            self.channel = self.sound.play(
                looping=self.looping,
                volume=self._volume,
                angle=self._angle,
                distance=self._distance,
            )
            if self.channel is not None:
                self.channel.set_finish_callback(self._on_finished)
        else:
            self.channel.play()
        return self.channel

    def stop(self):
        if self.channel is not None:
            self.channel.set_finish_callback(None)
            self.channel.stop()
            self.channel = None

    def pause(self):
        if self.channel is not None:
            self.channel.pause()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = val
        if self.channel is not None:
            self.channel.set_volume(self._volume)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        self._angle = val
        if self.channel is not None:
            self.channel.set_position(self._angle, self._distance)

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, val):
        self._distance = val
        if self.channel is not None:
            self.channel.set_position(self._angle, self._distance)

    def _on_finished(self):
        if self.channel is not None:
            self.channel.set_finish_callback(None)
            self.channel = None
            if self._finish_callback is not None:
                self._finish_callback()

    def set_finish_callback(self, finish_callback):
        self._finish_callback = finish_callback


class Channel:
    channels = {}

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self._finish_callback = None

    @classmethod
    def get_or_create(cls, channel_id):
        channel = cls.channels.get(channel_id)
        if channel is None:
            channel = cls(channel_id)
            cls.channels[channel_id] = channel
        return channel

    def stop(self):
        ret = _gaem.lib.Mix_HaltChannel(self.channel_id)
        raise_for_neg(ret)

    def pause(self):
        _gaem.lib.Mix_Pause(self.channel_id)

    def play(self):
        _gaem.lib.Mix_Resume(self.channel_id)

    def set_volume(self, volume):
        _gaem.lib.Mix_Volume(self.channel_id, int(volume * SDL_MIX_MAXVOLUME))

    def set_position(self, angle, distance):
        distance = min(max(distance, 0.0), 1.0)
        _gaem.lib.Mix_SetPosition(
            self.channel_id,
            int(angle / math.tau * 360.0 - 90.0),
            int(distance * 255),
        )

    def _on_finished(self):
        if self._finish_callback is not None:
            self._finish_callback()

    def set_finish_callback(self, finish_callback):
        self._finish_callback = finish_callback


class Music:
    def __init__(self, music):
        self.music = music

    def __del__(self):
        _gaem.lib.Mix_FreeMusic(self.music)

    def play(self, *, looping=False):
        if looping:
            loops = -1
        else:
            loops = 0
        _gaem.lib.Mix_PlayMusic(self.music, loops)


class Gamepad:
    def __init__(self, controller):
        self.controller = controller

    def is_button_pressed(self, button):
        if self.controller is None:
            return False
        button_id = gamepad_button_ids.get(button)
        if button_id is None:
            raise ValueError(f'Unknown button {button}')
        return bool(
            _gaem.lib.SDL_GameControllerGetButton(self.controller, button_id)
        )

    def get_axis(self, axis):
        if self.controller is None:
            return 0.0
        axis_id = gamepad_axis_ids.get(axis)
        if axis_id is None:
            raise ValueError(f'Unknown axis {button}')
        return (
            _gaem.lib.SDL_GameControllerGetAxis(self.controller, axis_id)
            / 32767
        )

    def __getattr__(self, name):
        if name.startswith('axis_'):
            return self.get_axis(name.removeprefix('axis_'))
        elif name.startswith('button_'):
            return self.is_button_pressed(name.removeprefix('button_'))
        # basically raise
        return super().__getattribute__(name)


@_gaem.ffi.def_extern()
def channel_finished_callback(channel_id):
    Channel.get_or_create(channel_id)._on_finished()


@_gaem.ffi.def_extern()
def music_finished_callback():
    g.music_finished = True


class SDL2Texture:
    "Holder object which owns SDL texture"

    def __init__(self, texture):
        self.ptr = texture

    def __del__(self):
        if self.ptr is not None:
            _gaem.lib.SDL_DestroyTexture(self.ptr)

    def replace(self, texture):
        if self.ptr is not None:
            _gaem.lib.SDL_DestroyTexture(self.ptr)
        self.ptr = texture


@dataclass
class KeyboardEvent:
    scancode: str
    keycode: str

    @classmethod
    def from_sdl_event(cls, sdl_kb_event):
        sym = sdl_kb_event.keysym.sym
        if sym & SDLK_SCANCODE_MASK:
            sym &= ~SDLK_SCANCODE_MASK
            keycode = scancodes[sym]
        else:
            keycode = bytes([sym]).decode('ascii')
        return cls(
            scancode=scancodes[sdl_kb_event.keysym.scancode],
            keycode=keycode,
        )


@dataclass
class MouseMotionEvent:
    which: int
    state: int
    x: int
    y: int
    xrel: int
    yrel: int

    @classmethod
    def from_sdl_event(cls, sdl_mouse_motion_event):
        return cls(
            which=sdl_mouse_motion_event.which,
            state=sdl_mouse_motion_event.state,
            x=sdl_mouse_motion_event.x,
            y=sdl_mouse_motion_event.y,
            xrel=sdl_mouse_motion_event.xrel,
            yrel=sdl_mouse_motion_event.yrel,
        )


@dataclass
class MouseButtonEvent:
    which: int
    button: int
    state: int
    clicks: int
    x: int
    y: int

    @classmethod
    def from_sdl_event(cls, sdl_mouse_button_event):
        return cls(
            which=sdl_mouse_button_event.which,
            button=sdl_mouse_button_event.button,
            state=sdl_mouse_button_event.state,
            clicks=sdl_mouse_button_event.clicks,
            x=sdl_mouse_button_event.x,
            y=sdl_mouse_button_event.y,
        )


@dataclass
class ResizeEvent:
    width: int
    height: int


@dataclass
class GamepadButtonEvent:
    gamepad: Gamepad
    button: str


@dataclass
class GamepadAxisEvent:
    gamepad: Gamepad
    axis: str
    value: float


def load_image(path, *, center=False):
    surf = _gaem.lib.IMG_Load(to_cstr(path))
    raise_for_null(surf)
    texture = _gaem.lib.SDL_CreateTextureFromSurface(g.ren, surf)
    raise_for_null(texture)
    img = Image(SDL2Texture(texture), surf.w, surf.h)
    _gaem.lib.SDL_FreeSurface(surf)
    if center:
        img.center()
    return img


def load_atlas(path):
    # assumes a single png image with the same name as the xml
    atlas = {}
    data = ET.parse(path)
    sheet = load_image(path.rpartition('.xml')[0] + '.png')
    for el in data.findall('./SubTexture'):
        name = el.attrib['name'].removesuffix('.png')
        img = sheet.subregion(
            int(el.attrib['x']),
            int(el.attrib['y']),
            int(el.attrib['width']),
            int(el.attrib['height']),
        )
        atlas[name] = img
    return atlas


class Font:
    def __init__(self, font):
        self.font = font
        self._glyphs = {}
        self._surface = None
        self._texture = SDL2Texture(None)
        self._height = 0
        self._x = 0
        self._y = 0
        self._dstrect = _gaem.ffi.new('SDL_Rect *')
        self.line_skip = _gaem.lib.TTF_FontLineSkip(self.font)

    def __del__(self):
        _gaem.lib.TTF_CloseFont(self.font)

    def render_text_to_image(self, text, *, color=WHITE):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        surf = _gaem.lib.TTF_RenderUTF8_Blended(
            self.font, to_cstr(text), color
        )
        raise_for_null(surf)
        texture = _gaem.lib.SDL_CreateTextureFromSurface(g.ren, surf)
        raise_for_null(texture)
        img = Image(SDL2Texture(texture), surf.w, surf.h)
        _gaem.lib.SDL_FreeSurface(surf)
        return img

    def draw(
        self,
        text,
        *,
        x=0,
        y=0,
        w=None,
        h=None,
        sx=1.0,
        sy=1.0,
        color=WHITE,
        align=TextAlign.LEFT,
    ):
        # TODO: kerning. Although looks surprisingly OK without it.
        self._ensure_glyphs(text)

        multiline = False
        clipping = False

        if w is not None:
            clipping = True
            w *= sx
            clip_left = int(min(x, x + w))
            clip_right = int(max(x, x + w))
            clip_top = 0
            clip_bottom = g.screen_height
            if h is not None:
                multiline = True
                h *= sy
                clip_top = int(min(y, y + h))
                clip_bottom = int(max(y, y + h))
            clip_rect = _gaem.ffi.new('SDL_Rect *')
            clip_rect.x = clip_left
            clip_rect.y = clip_top
            clip_rect.w = clip_right - clip_left
            clip_rect.h = clip_bottom - clip_top
            ret = _gaem.lib.SDL_RenderSetClipRect(g.ren, clip_rect)
            raise_for_neg(ret)

        # I should really use something like harfbuzz
        # instead of trying to layout text myself
        # but it should work for boring LTR writing I use
        if not multiline:
            # simple algorithm
            line_width = sum(self._glyphs[c].width for c in text)
            if w is not None:
                if align is TextAlign.CENTER:
                    x += (w - line_width) / 2
                elif align is TextAlign.RIGHT:
                    x += w - line_width
            for c in text:
                glyph = self._glyphs[c]
                glyph.draw(x=x, y=y, color=color)
                x += glyph.width
        else:
            lines = self._calculate_line_widths(text, w)
            for line_width, words in lines:
                current_x = x
                if align is TextAlign.CENTER:
                    current_x += (w - line_width) / 2
                elif align is TextAlign.RIGHT:
                    current_x += w - line_width
                for word in words:
                    for c in word:
                        glyph = self._glyphs[c]
                        glyph.draw(x=current_x, y=y, color=color)
                        current_x += glyph.width
                y += self.line_skip

        if clipping:
            ret = _gaem.lib.SDL_RenderSetClipRect(g.ren, NULL)
            raise_for_neg(ret)

    def calc_size(self, text, w=None):
        self._ensure_glyphs(text)
        if w is None:
            w = sum(self._glyphs[c].width for c in text)
            h = self.line_skip
            return w, h
        lines = self._calculate_line_widths(text, w)
        w = max(l[0] for l in lines)
        h = self.line_skip * len(lines)
        return w, h

    def _calculate_line_widths(self, text, w):
        # here we go, first let's calculate lines and widths
        lines = []  # list of (width, words) tuples
        current_line = []
        words = re.split(r'(?<=\S)(?=\s)', text)
        cursor = 0
        current_line_width = 0
        while cursor < len(words):
            word = words[cursor]
            word_width = sum(self._glyphs[c].width for c in word)
            # can we fit the current word?
            if word_width + current_line_width <= w:
                # we can
                cursor += 1
                current_line_width += word_width
                current_line.append(word)
            else:
                # we can't
                if current_line_width == 0:
                    # oh no, we're still at the first word
                    # we'll have to split it at whatever characters fit
                    # always fit the first character in case if
                    # it is wider than available width
                    word_width = self._glyphs[word[0]].width
                    if len(word) == 1:
                        cursor += 1
                        lines.append((word_width, [word]))
                    for i, c in enumerate(word[1:], start=1):
                        glyph_width = self._glyphs[c].width
                        if word_width + glyph_width > w:
                            words[cursor] = word[i:]
                            lines.append((word_width, [word[:i]]))
                            break
                        word_width += glyph_width
                else:
                    # current word goes on the next line
                    # with whitespace stripped
                    words[cursor] = word.lstrip()
                    lines.append((current_line_width, current_line))
                current_line_width = 0
                current_line = []
        lines.append((current_line_width, current_line))
        return lines

    def _ensure_glyphs(self, s):
        if self._surface is None:
            # first time
            self._init_new_texture()
        # simplification, 1 codepoint = 1 glyph
        glyphs_to_create = set(s) - self._glyphs.keys()
        for glyph in glyphs_to_create:
            self._add_glyph(glyph)
        self._recreate_texture_from_surface()

    def _init_new_texture(self):
        w = 512  # maybe calculate these?
        h = 512
        if self._surface is not None:
            _gaem.lib.SDL_FreeSurface(self._surface)
        self._surface = _gaem.lib.SDL_CreateRGBSurface(
            0,
            w,
            h,
            32,
            0xFF_00_00_00,
            0x00_FF_00_00,
            0x00_00_FF_00,
            0x00_00_00_FF,
        )
        raise_for_null(self._surface)
        self._texture = SDL2Texture(None)
        self._height = 0
        self._x = 0
        self._y = 0

    def _add_glyph(self, c):
        # TODO: I think we'll need padding
        glyph_surf = _gaem.lib.TTF_RenderGlyph32_Blended(
            self.font, ord(c), (255, 255, 255, 255)
        )
        # are we out of horizontal space?
        if self._x + glyph_surf.w > self._surface.w:
            # we are, let's start the next line
            self._x = 0
            self._y += self._height
            self._height = 0
        # are we out of vertical space?
        if self._y + glyph_surf.h > self._surface.h:
            # we are, let's start a new image
            self._recreate_texture_from_surface()
            self._init_new_texture()
        dstrect = self._dstrect
        dstrect.x = self._x
        dstrect.y = self._y
        ret = _gaem.lib.SDL_BlitSurface(
            glyph_surf, NULL, self._surface, dstrect
        )
        raise_for_neg(ret)
        glyph_image = Image(self._texture, glyph_surf.w, glyph_surf.h)
        glyph_image._srcrect.x = self._x
        glyph_image._srcrect.y = self._y
        self._x += glyph_surf.w
        self._height = max(self._height, glyph_surf.h)
        self._glyphs[c] = glyph_image
        _gaem.lib.SDL_FreeSurface(glyph_surf)

    def _recreate_texture_from_surface(self):
        t = _gaem.lib.SDL_CreateTextureFromSurface(g.ren, self._surface)
        raise_for_null(t)
        self._texture.replace(t)


def load_sound(path):
    chunk = _gaem.lib.Mix_LoadWAV(to_cstr(path))
    raise_for_null(chunk)
    return Sound(chunk)


def load_music(path):
    music = _gaem.lib.Mix_LoadMUS(to_cstr(path))
    raise_for_null(music)
    return Music(music)


def load_font(path, ptsize=14):
    font = _gaem.lib.TTF_OpenFont(to_cstr(path), ptsize)
    raise_for_null(font)
    return Font(font)


def get_screen_size():
    return (g.screen_width, g.screen_height)


def is_key_pressed(scancode):
    return scancode in g.pressed_keys


def is_mouse_button_pressed(button=1):
    return button in g.pressed_mouse_buttons


def get_mouse_position():
    return (g.mouse_x, g.mouse_y)


def get_gamepads():
    return list(g.gamepads.values())


def set_background_color(red, green, blue, alpha=255):
    g.background_color = (red, green, blue, alpha)


def draw_rect(x, y, w, h, color=WHITE, *, blend_mode=BlendMode.BLEND):
    if len(color) == 3:
        color = (color[0], color[1], color[2], 255)
    ret = _gaem.lib.SDL_SetRenderDrawColor(
        g.ren, color[0], color[1], color[2], color[3]
    )
    raise_for_neg(ret)
    rect = _gaem.ffi.new('SDL_Rect *')
    rect.x = int(x)
    rect.y = int(y)
    rect.w = int(w)
    rect.h = int(h)
    ret = _gaem.lib.SDL_SetRenderDrawBlendMode(g.ren, blend_mode)
    raise_for_neg(ret)
    ret = _gaem.lib.SDL_RenderDrawRect(g.ren, rect)
    raise_for_neg(ret)


def fill_rect(x, y, w, h, color=WHITE, *, blend_mode=BlendMode.BLEND):
    if len(color) == 3:
        color = (color[0], color[1], color[2], 255)
    ret = _gaem.lib.SDL_SetRenderDrawColor(
        g.ren, color[0], color[1], color[2], color[3]
    )
    raise_for_neg(ret)
    rect = _gaem.ffi.new('SDL_Rect *')
    rect.x = int(x)
    rect.y = int(y)
    rect.w = int(w)
    rect.h = int(h)
    ret = _gaem.lib.SDL_SetRenderDrawBlendMode(g.ren, blend_mode)
    raise_for_neg(ret)
    ret = _gaem.lib.SDL_RenderFillRect(g.ren, rect)
    raise_for_neg(ret)


def draw_line(x1, y1, x2, y2, color=WHITE, *, blend_mode=BlendMode.BLEND):
    if len(color) == 3:
        color = (color[0], color[1], color[2], 255)
    ret = _gaem.lib.SDL_SetRenderDrawColor(
        g.ren, color[0], color[1], color[2], color[3]
    )
    raise_for_neg(ret)
    ret = _gaem.lib.SDL_SetRenderDrawBlendMode(g.ren, blend_mode)
    raise_for_neg(ret)
    ret = _gaem.lib.SDL_RenderDrawLine(
        g.ren, int(x1), int(y1), int(x2), int(y2)
    )
    raise_for_neg(ret)


def stop_sounds():
    ret = _gaem.lib.Mix_HaltChannel(-1)
    raise_for_neg(ret)


def stop_music():
    _gaem.lib.Mix_HaltMusic()


def pause_music():
    _gaem.lib.Mix_PauseMusic()


def resume_music():
    _gaem.lib.Mix_ResumeMusic()


def set_sounds_volume(self, volume):
    _gaem.lib.Mix_MasterVolume(int(volume * SDL_MIX_MAXVOLUME))


def set_music_volume(self, volume):
    _gaem.lib.Mix_VolumeMusic(int(volume * SDL_MIX_MAXVOLUME))


def quit():
    g.should_quit = True


def raise_for_neg(ret):
    if ret < 0:
        err = from_cstr(_gaem.lib.SDL_GetError())
        raise GaemError(err)


def raise_for_null(ret):
    if ret == _gaem.ffi.NULL:
        err = from_cstr(_gaem.lib.SDL_GetError())
        raise GaemError(err)


def from_cstr(cstr):
    return _gaem.ffi.string(cstr).decode('utf-8')


def to_cstr(s):
    return _gaem.ffi.new('char[]', s.encode('utf-8'))


class GaemError(Exception):
    pass


class Game:
    def on_load(self):
        pass

    def on_update(self, dt):
        pass

    def on_draw(self):
        pass

    def on_keydown(self, event):
        pass

    def on_keyup(self, event):
        pass

    def on_mousemotion(self, event):
        pass

    def on_mousedown(self, event):
        pass

    def on_mouseup(self, event):
        pass

    def on_gamepad_connected(self, gamepad):
        pass

    def on_gamepad_disconnected(self, gamepad):
        pass

    def on_gamepad_button_down(self, event):
        pass

    def on_gamepad_button_up(self, event):
        pass

    def on_gamepad_axis_motion(self, event):
        pass

    def on_quit(self):
        return True

    def on_resize(self, event):
        pass

    def on_music_finished(self):
        pass


scancodes = {
    0: 'unknown',
    4: 'a',
    5: 'b',
    6: 'c',
    7: 'd',
    8: 'e',
    9: 'f',
    10: 'g',
    11: 'h',
    12: 'i',
    13: 'j',
    14: 'k',
    15: 'l',
    16: 'm',
    17: 'n',
    18: 'o',
    19: 'p',
    20: 'q',
    21: 'r',
    22: 's',
    23: 't',
    24: 'u',
    25: 'v',
    26: 'w',
    27: 'x',
    28: 'y',
    29: 'z',
    30: '1',
    31: '2',
    32: '3',
    33: '4',
    34: '5',
    35: '6',
    36: '7',
    37: '8',
    38: '9',
    39: '0',
    40: 'return',
    41: 'escape',
    42: 'backspace',
    43: 'tab',
    44: 'space',
    45: 'minus',
    46: 'equals',
    47: 'leftbracket',
    48: 'rightbracket',
    49: 'backslash',
    50: 'nonushash',
    51: 'semicolon',
    52: 'apostrophe',
    53: 'grave',
    54: 'comma',
    55: 'period',
    56: 'slash',
    57: 'capslock',
    58: 'f1',
    59: 'f2',
    60: 'f3',
    61: 'f4',
    62: 'f5',
    63: 'f6',
    64: 'f7',
    65: 'f8',
    66: 'f9',
    67: 'f10',
    68: 'f11',
    69: 'f12',
    70: 'printscreen',
    71: 'scrolllock',
    72: 'pause',
    73: 'insert',
    74: 'home',
    75: 'pageup',
    76: 'delete',
    77: 'end',
    78: 'pagedown',
    79: 'right',
    80: 'left',
    81: 'down',
    82: 'up',
    83: 'numlockclear',
    84: 'kp_divide',
    85: 'kp_multiply',
    86: 'kp_minus',
    87: 'kp_plus',
    88: 'kp_enter',
    89: 'kp_1',
    90: 'kp_2',
    91: 'kp_3',
    92: 'kp_4',
    93: 'kp_5',
    94: 'kp_6',
    95: 'kp_7',
    96: 'kp_8',
    97: 'kp_9',
    98: 'kp_0',
    99: 'kp_period',
    100: 'nonusbackslash',
    101: 'application',
    102: 'power',
    103: 'kp_equals',
    104: 'f13',
    105: 'f14',
    106: 'f15',
    107: 'f16',
    108: 'f17',
    109: 'f18',
    110: 'f19',
    111: 'f20',
    112: 'f21',
    113: 'f22',
    114: 'f23',
    115: 'f24',
    116: 'execute',
    117: 'help',
    118: 'menu',
    119: 'select',
    120: 'stop',
    121: 'again',
    122: 'undo',
    123: 'cut',
    124: 'copy',
    125: 'paste',
    126: 'find',
    127: 'mute',
    128: 'volumeup',
    129: 'volumedown',
    130: 'lockingcapslock',
    131: 'lockingnumlock',
    132: 'lockingscrolllock',
    133: 'kp_comma',
    134: 'kp_equalsas400',
    135: 'international1',
    136: 'international2',
    137: 'international3',
    138: 'international4',
    139: 'international5',
    140: 'international6',
    141: 'international7',
    142: 'international8',
    143: 'international9',
    144: 'lang1',
    145: 'lang2',
    146: 'lang3',
    147: 'lang4',
    148: 'lang5',
    149: 'lang6',
    150: 'lang7',
    151: 'lang8',
    152: 'lang9',
    153: 'alterase',
    154: 'sysreq',
    155: 'cancel',
    156: 'clear',
    157: 'prior',
    158: 'return2',
    159: 'separator',
    160: 'out',
    161: 'oper',
    162: 'clearagain',
    163: 'crsel',
    164: 'exsel',
    176: 'kp_00',
    177: 'kp_000',
    178: 'thousandsseparator',
    179: 'decimalseparator',
    180: 'currencyunit',
    181: 'currencysubunit',
    182: 'kp_leftparen',
    183: 'kp_rightparen',
    184: 'kp_leftbrace',
    185: 'kp_rightbrace',
    186: 'kp_tab',
    187: 'kp_backspace',
    188: 'kp_a',
    189: 'kp_b',
    190: 'kp_c',
    191: 'kp_d',
    192: 'kp_e',
    193: 'kp_f',
    194: 'kp_xor',
    195: 'kp_power',
    196: 'kp_percent',
    197: 'kp_less',
    198: 'kp_greater',
    199: 'kp_ampersand',
    200: 'kp_dblampersand',
    201: 'kp_verticalbar',
    202: 'kp_dblverticalbar',
    203: 'kp_colon',
    204: 'kp_hash',
    205: 'kp_space',
    206: 'kp_at',
    207: 'kp_exclam',
    208: 'kp_memstore',
    209: 'kp_memrecall',
    210: 'kp_memclear',
    211: 'kp_memadd',
    212: 'kp_memsubtract',
    213: 'kp_memmultiply',
    214: 'kp_memdivide',
    215: 'kp_plusminus',
    216: 'kp_clear',
    217: 'kp_clearentry',
    218: 'kp_binary',
    219: 'kp_octal',
    220: 'kp_decimal',
    221: 'kp_hexadecimal',
    224: 'lctrl',
    225: 'lshift',
    226: 'lalt',
    227: 'lgui',
    228: 'rctrl',
    229: 'rshift',
    230: 'ralt',
    231: 'rgui',
    257: 'mode',
    258: 'audionext',
    259: 'audioprev',
    260: 'audiostop',
    261: 'audioplay',
    262: 'audiomute',
    263: 'mediaselect',
    264: 'www',
    265: 'mail',
    266: 'calculator',
    267: 'computer',
    268: 'ac_search',
    269: 'ac_home',
    270: 'ac_back',
    271: 'ac_forward',
    272: 'ac_stop',
    273: 'ac_refresh',
    274: 'ac_bookmarks',
    275: 'brightnessdown',
    276: 'brightnessup',
    277: 'displayswitch',
    278: 'kbdillumtoggle',
    279: 'kbdillumdown',
    280: 'kbdillumup',
    281: 'eject',
    282: 'sleep',
    283: 'app1',
    284: 'app2',
    285: 'audiorewind',
    286: 'audiofastforward',
    287: 'softleft',
    288: 'softright',
    289: 'call',
    290: 'endcall',
}

gamepad_axis_names = {
    0: 'left_x',
    1: 'left_y',
    2: 'right_x',
    3: 'right_y',
    4: 'trigger_left',
    5: 'trigger_right',
}

gamepad_axis_ids = {v: k for k, v in gamepad_axis_names.items()}

gamepad_button_names = {
    0: 'a',
    1: 'b',
    2: 'x',
    3: 'y',
    4: 'back',
    5: 'guide',
    6: 'start',
    7: 'leftstick',
    8: 'rightstick',
    9: 'leftshoulder',
    10: 'rightshoulder',
    11: 'dpad_up',
    12: 'dpad_down',
    13: 'dpad_left',
    14: 'dpad_right',
    15: 'misc1',
    16: 'paddle1',
    17: 'paddle2',
    18: 'paddle3',
    19: 'paddle4',
    20: 'touchpad',
}

gamepad_button_ids = {v: k for k, v in gamepad_button_names.items()}
