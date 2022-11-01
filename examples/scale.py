import gaem

SPEED = 3


class ScaleExample(gaem.Game):
    def on_load(self):
        self.hello_img = gaem.load_image('assets/hello.png')
        w, h = gaem.get_screen_size()
        self.hello_img.x = w / 2
        self.hello_img.y = h / 2

    def on_draw(self):
        self.hello_img.draw()

    def on_update(self, dt):
        if gaem.is_key_pressed('right'):
            self.hello_img.sx += SPEED * dt
        if gaem.is_key_pressed('left'):
            self.hello_img.sx -= SPEED * dt
        if gaem.is_key_pressed('up'):
            self.hello_img.sy -= SPEED * dt
        if gaem.is_key_pressed('down'):
            self.hello_img.sy += SPEED * dt

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
            return
        elif event.scancode == 'z':
            self.hello_img.center()
        elif event.scancode == 'x':
            self.hello_img.cx = 0
            self.hello_img.cy = 0

    def on_resize(self, event):
        self.hello_img.x = event.width / 2
        self.hello_img.y = event.height / 2


gaem.run(ScaleExample(), title='Scale example', resizable=True)
