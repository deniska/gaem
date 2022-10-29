import re

d = {}
with open('/home/denis/sdk/sdl2/include/SDL2/SDL_scancode.h') as f:
    for line in f:
        r = re.search(r'SDL_SCANCODE_(\w+) = (\d+)', line)
        if not r:
            continue
        d[int(r[2])] = r[1].lower()

print(d)
