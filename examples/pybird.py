import random

import gaem

HEIGHT = 800
WIDTH = 600

FLAP_VEL = -500
GRAVITY = 1300

PIPE_VDIST = 250
PIPE_HDIST = 180
START_X = -250
BIRD_X = 60

SPEED = 100


class PyBird(gaem.Game):
    def on_load(self):
        self.pipe_img = gaem.load_image('examples/pipe.png')
        self.bird_img = gaem.load_image('examples/bird.png', center=True)
        gaem.set_background_color(50, 210, 220)
        self.reset()

    def reset(self):
        self.y = HEIGHT / 2
        self.x = START_X
        self.yvel = 0.0
        self.pipes = [next_pipe() for _ in range(3)]
        self.started = False
        self.dead = False
        self.can_restart = False

    def on_draw(self):
        # pipes
        for i, pipe_y in enumerate(self.pipes):
            self.pipe_img.draw(
                x=(self.pipe_img.width + PIPE_HDIST) * i - self.x,
                y=pipe_y + PIPE_VDIST / 2,
            )
            self.pipe_img.draw(
                x=(self.pipe_img.width + PIPE_HDIST) * i - self.x,
                y=pipe_y - PIPE_VDIST / 2,
                sy=-1.0,
            )
        # bird
        angle = -self.yvel / 500
        angle = max(angle, -0.8)
        if self.dead:
            angle = -1.5
        self.bird_img.draw(
            x=BIRD_X,
            y=self.y,
            angle=angle,
        )

    def on_update(self, dt):
        if not self.started:
            return
        self.y += self.yvel * dt
        self.yvel += GRAVITY * dt
        if self.y > HEIGHT - self.bird_img.width / 4:
            self.y = HEIGHT - self.bird_img.width / 4
            self.can_restart = True
            self.dead = True
        if self.dead:
            return
        self.x += SPEED * dt
        if self.x > PIPE_HDIST + self.pipe_img.width:
            self.x -= PIPE_HDIST + self.pipe_img.width
            self.pipes.pop(0)
            self.pipes.append(next_pipe())
        bird_girth = self.bird_img.height / 2
        for i, pipe_y in enumerate(self.pipes):
            top_pipe_y = pipe_y - PIPE_VDIST / 2
            bottom_pipe_y = pipe_y + PIPE_VDIST / 2
            pipe_left = (self.pipe_img.width + PIPE_HDIST) * i - self.x
            pipe_right = (
                (self.pipe_img.width + PIPE_HDIST) * i
                - self.x
                + self.pipe_img.width
            )
            if (
                self.y - bird_girth < top_pipe_y
                and BIRD_X + bird_girth > pipe_left
                and BIRD_X - bird_girth < pipe_right
                or self.y + bird_girth > bottom_pipe_y
                and BIRD_X + bird_girth > pipe_left
                and BIRD_X - bird_girth < pipe_right
                or self.y + bird_girth > HEIGHT
            ):
                self.dead = True

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
        elif event.scancode == 'space':
            if not self.dead:
                self.yvel = FLAP_VEL
                self.started = True
            elif self.can_restart:
                self.reset()


def next_pipe():
    return random.randint(PIPE_VDIST, HEIGHT - PIPE_VDIST)


gaem.run(PyBird(), title='PyBird', width=WIDTH, height=HEIGHT)
