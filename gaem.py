import _mysdl2

NULL = _mysdl2.ffi.NULL

SDL_WINDOWPOS_CENTERED = 0x2FFF0000
SDL_WINDOWPOS_UNDEFINED = 0x1FFF0000

SDL_RENDERER_SOFTWARE = 0x00000001
SDL_RENDERER_ACCELERATED = 0x00000002
SDL_RENDERER_PRESENTVSYNC = 0x00000004
SDL_RENDERER_TARGETTEXTURE = 0x00000008

SDL_INIT_EVERYTHING = 62001


SDL_QUIT = 0x100


class g:  # yes, globals, wanna fight?
    win = None
    ren = None
    should_quit = False


def run(game, *, title='Gaem', width=800, height=480, x=None, y=None):
    ret = _mysdl2.lib.SDL_Init(SDL_INIT_EVERYTHING)
    raise_for_neg(ret)

    if x is None:
        x = SDL_WINDOWPOS_CENTERED
    if y is None:
        y = SDL_WINDOWPOS_CENTERED
    title = to_cstr(title)
    flags = 0
    g.win = _mysdl2.lib.SDL_CreateWindow(title, x, y, width, height, flags)
    raise_for_null(g.win)

    g.ren = _mysdl2.lib.SDL_CreateRenderer(
        g.win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    )
    raise_for_null(g.ren)

    game.on_load()

    previous_ticks = None
    counter_resolution = _mysdl2.lib.SDL_GetPerformanceFrequency()

    while not g.should_quit:
        while _mysdl2.lib.my_poll_event():
            ev_type = _mysdl2.lib.my_get_event_type()
            if ev_type == SDL_QUIT:
                ret = game.on_quit()
                g.should_quit = bool(ret)
        _mysdl2.lib.SDL_RenderClear(g.ren)
        if previous_ticks:
            current_ticks = _mysdl2.lib.SDL_GetPerformanceCounter()
            dt = (current_ticks - previous_ticks) / counter_resolution
            previous_ticks = current_ticks
            game.on_update(dt)
        else:
            previous_ticks = _mysdl2.lib.SDL_GetPerformanceCounter()
        game.on_render()
        _mysdl2.lib.SDL_RenderPresent(g.ren)

    _mysdl2.lib.SDL_DestroyRenderer(g.ren)
    _mysdl2.lib.SDL_DestroyWindow(g.win)
    _mysdl2.lib.SDL_Quit()


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

    def on_quit(self):
        return True
