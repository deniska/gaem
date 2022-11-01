import gaem

SPEED = 0.5


class SubregionExample(gaem.Game):
    def on_load(self):
        gaem.set_background_color(255, 244, 165)
        w, h = gaem.get_screen_size()
        img = gaem.load_image('assets/regions.png')
        self.imgs = [
            img.subregion(0, 0, 64, 64),
            img.subregion(64, 0, 64, 64),
            img.subregion(0, 64, 64, 64),
            img.subregion(64, 64, 64, 64),
        ]
        for i, img in enumerate(self.imgs, start=1):
            img.center()
            img.x = w / 5 * i
            img.y = h / 3
        the_second_row = []
        for img in self.imgs:
            new_img = img.copy()
            new_img.y = h / 3 * 2
            the_second_row.append(new_img)
        self.imgs.extend(the_second_row)

    def on_draw(self):
        for img in self.imgs:
            img.draw()

    def on_update(self, dt):
        for i, img in enumerate(self.imgs, start=1):
            img.angle += SPEED * dt * i

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()


gaem.run(SubregionExample(), title='Subregion example')
