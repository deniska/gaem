import gaem


class DebugDrawing(gaem.Game):
    def on_draw(self):
        gaem.draw_rect(20, 20, 100, 200, (255, 0, 0))
        gaem.draw_rect(90, 140, 100, 200, (0, 255, 0))
        gaem.draw_rect(160, 260, 100, 200, (0, 0, 255))

        gaem.fill_rect(240, 20, 100, 200, (255, 0, 0))
        gaem.fill_rect(310, 140, 100, 200, (0, 255, 0))
        gaem.fill_rect(380, 260, 100, 200, (0, 0, 255))

        gaem.fill_rect(460, 20, 100, 200, (255, 0, 0, 127))
        gaem.fill_rect(530, 140, 100, 200, (0, 255, 0, 127))
        gaem.fill_rect(600, 260, 100, 200, (0, 0, 255, 127))

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()


if __name__ == '__main__':
    gaem.run(DebugDrawing(), title='Debug drawing example', vsync=True)
