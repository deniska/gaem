import math

import gaem


class PositionalAudio(gaem.Game):
    def on_load(self):
        self.pew_sound = gaem.load_sound('assets/tank_shoot.wav')

    def on_mousedown(self, event):
        w, h = gaem.get_screen_size()
        dx = event.x - w / 2
        dy = event.y - h / 2
        d = math.sqrt(dx**2 + dy**2) / (w / 2)
        a = math.atan2(dy, -dx)
        self.pew_sound.play(angle=a, distance=d)

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()


if __name__ == '__main__':
    gaem.run(
        PositionalAudio(),
        title='Positional audio example',
        width=300,
        height=300,
    )
