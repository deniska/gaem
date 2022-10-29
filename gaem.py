from dataclasses import dataclass

import _mysdl2

NULL = _mysdl2.ffi.NULL

SDL_WINDOWPOS_CENTERED = 0x2FFF0000
SDL_WINDOWPOS_UNDEFINED = 0x1FFF0000

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

SDLK_SCANCODE_MASK = 1 << 30


class g:  # yes, globals, wanna fight?
    win = None
    ren = None
    should_quit = False
    screen_width = 0
    screen_height = 0
    pressed_keys = set()


def run(game, *, title='Gaem', width=800, height=480, x=None, y=None):
    ret = _mysdl2.lib.SDL_Init(SDL_INIT_EVERYTHING)
    raise_for_neg(ret)

    img_flags = IMG_INIT_PNG | IMG_INIT_JPG
    if img_flags != _mysdl2.lib.IMG_Init(img_flags):
        raise GaemError('Failed to initialize SDL_Image')

    if x is None:
        x = SDL_WINDOWPOS_CENTERED
    if y is None:
        y = SDL_WINDOWPOS_CENTERED
    title = to_cstr(title)
    flags = 0
    g.screen_width = width
    g.screen_height = height
    g.win = _mysdl2.lib.SDL_CreateWindow(title, x, y, width, height, flags)
    raise_for_null(g.win)

    g.ren = _mysdl2.lib.SDL_CreateRenderer(
        g.win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    )
    raise_for_null(g.ren)

    game.on_load()

    previous_ticks = None
    counter_resolution = _mysdl2.lib.SDL_GetPerformanceFrequency()

    sdl2_event = _mysdl2.lib.get_my_event_ptr()
    while not g.should_quit:
        while _mysdl2.lib.my_poll_event():
            ev_type = _mysdl2.lib.my_get_event_type()
            if ev_type == SDL_QUIT:
                ret = game.on_quit()
                g.should_quit = bool(ret)
            elif ev_type == SDL_KEYDOWN:
                sdl_kb_event = _mysdl2.ffi.cast(
                    'struct SDL_KeyboardEvent *', sdl2_event
                )
                if sdl_kb_event.repeat:
                    continue
                event = KeyboardEvent.from_sdl_event(sdl_kb_event)
                g.pressed_keys.add(event.scancode)
                game.on_keydown(event)
            elif ev_type == SDL_KEYUP:
                sdl_kb_event = _mysdl2.ffi.cast(
                    'struct SDL_KeyboardEvent *', sdl2_event
                )
                if sdl_kb_event.repeat:
                    continue
                event = KeyboardEvent.from_sdl_event(sdl_kb_event)
                g.pressed_keys.discard(event.scancode)
                game.on_keyup(event)
        _mysdl2.lib.SDL_RenderClear(g.ren)
        if previous_ticks:
            current_ticks = _mysdl2.lib.SDL_GetPerformanceCounter()
            dt = (current_ticks - previous_ticks) / counter_resolution
            previous_ticks = current_ticks
            game.on_update(dt)
        else:
            previous_ticks = _mysdl2.lib.SDL_GetPerformanceCounter()
        game.on_draw()
        _mysdl2.lib.SDL_RenderPresent(g.ren)

    _mysdl2.lib.SDL_DestroyRenderer(g.ren)
    _mysdl2.lib.SDL_DestroyWindow(g.win)
    _mysdl2.lib.IMG_Quit()
    _mysdl2.lib.SDL_Quit()


class Image:
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width = width
        self.height = height
        self._dstrect = _mysdl2.ffi.new('SDL_FRect * dstrect')

    def __del__(self):
        _mysdl2.lib.SDL_DestroyTexture(self.texture)

    def render(self, renderer, *, x, y):
        dstrect = self._dstrect
        dstrect.x = x
        dstrect.y = y
        dstrect.w = self.width
        dstrect.h = self.height
        _mysdl2.lib.SDL_RenderCopyExF(
            renderer, self.texture, NULL, dstrect, 0.0, NULL, 0
        )


@dataclass
class KeyboardEvent:
    scancode: object
    keycode: object

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


def load_image(path):
    surf = _mysdl2.lib.IMG_Load(to_cstr(path))
    raise_for_null(surf)
    texture = _mysdl2.lib.SDL_CreateTextureFromSurface(g.ren, surf)
    raise_for_null(texture)
    img = Image(texture, surf.w, surf.h)
    _mysdl2.lib.SDL_FreeSurface(surf)
    return img


def draw(drawable, *, x=0, y=0):
    drawable.render(g.ren, x=x, y=y)


def get_screen_size():
    return (g.screen_width, g.screen_height)


def raise_for_neg(ret):
    if ret < 0:
        err = from_cstr(_mysdl2.lib.SDL_GetError())
        raise GaemError(err)


def raise_for_null(ret):
    if ret == _mysdl2.ffi.NULL:
        err = from_cstr(_mysdl2.lib.SDL_GetError())
        raise GaemError(err)


def from_cstr(cstr):
    return _mysdl2.ffi.string(cstr).decode('utf-8')


def to_cstr(s):
    return _mysdl2.ffi.new('char[]', s.encode('utf-8'))


class GaemError(Exception):
    pass


class Game:
    def on_load(self):
        pass

    def on_update(self, dt):
        pass

    def on_render(self):
        pass

    def on_keydown(self, event):
        pass

    def on_keyup(self, event):
        pass

    def on_quit(self):
        return True


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
