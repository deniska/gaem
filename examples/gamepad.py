import gaem


class GamepadExample(gaem.Game):
    def on_load(self):
        self.gamepad = None

    def on_draw(self):
        if self.gamepad:
            visualize_gamepad(self.gamepad)

    def on_gamepad_connected(self, gamepad):
        self.gamepad = gamepad

    def on_gamepad_disconnected(self, gamepad):
        # example assumes a single gamepad
        self.gamepad = None

    def on_gamepad_button_down(self, event):
        print(f'Button down: {event.button}')

    def on_gamepad_button_up(self, event):
        print(f'Button up: {event.button}')

    def on_gamepad_axis_motion(self, event):
        print(f'Value: {event.value: .3f}; Axis: {event.axis}')

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()


AXIS_SIZE = 150
CROSS_SIZE = 20
BUTTON_SIZE = 30


def visualize_gamepad(gamepad):
    visualize_axis(
        100,
        400,
        gamepad.axis_left_x,
        gamepad.axis_left_y,
        gamepad.button_leftstick,
    )
    visualize_axis(
        380,
        400,
        gamepad.axis_right_x,
        gamepad.axis_right_y,
        gamepad.button_rightstick,
    )

    visualize_trigger(100, 200, gamepad.axis_trigger_left)
    visualize_trigger(380, 200, gamepad.axis_trigger_right)

    visualize_button(100, 530, gamepad.button_dpad_up)
    visualize_button(50, 580, gamepad.button_dpad_left)
    visualize_button(100, 630, gamepad.button_dpad_down)
    visualize_button(150, 580, gamepad.button_dpad_right)

    visualize_button(380, 530, gamepad.button_y)
    visualize_button(330, 580, gamepad.button_x)
    visualize_button(380, 630, gamepad.button_a)
    visualize_button(430, 580, gamepad.button_b)

    visualize_button(170, 130, gamepad.button_leftshoulder)
    visualize_button(310, 130, gamepad.button_rightshoulder)

    visualize_button(200, 650, gamepad.button_back)
    visualize_button(280, 650, gamepad.button_start)
    visualize_button(240, 400, gamepad.button_guide)


def visualize_axis(x, y, mx, my, b):
    gaem.draw_rect(x - AXIS_SIZE / 2, y - AXIS_SIZE / 2, AXIS_SIZE, AXIS_SIZE)
    cx = x + mx * AXIS_SIZE / 2
    cy = y + my * AXIS_SIZE / 2
    gaem.draw_line(cx - CROSS_SIZE / 2, cy, cx + CROSS_SIZE / 2, cy)
    gaem.draw_line(cx, cy - CROSS_SIZE / 2, cx, cy + CROSS_SIZE / 2)
    visualize_button(x, y, b)


def visualize_trigger(x, y, my):
    gaem.draw_rect(x - 10, y - AXIS_SIZE / 2, 20, AXIS_SIZE)
    cy = y - AXIS_SIZE / 2 + my * AXIS_SIZE
    gaem.draw_line(x - CROSS_SIZE / 2, cy, x + CROSS_SIZE / 2, cy)
    gaem.draw_line(x, cy - CROSS_SIZE / 2, x, cy + CROSS_SIZE / 2)


def visualize_button(x, y, b):
    if b:
        gaem.fill_rect(
            x - BUTTON_SIZE / 2, y - BUTTON_SIZE / 2, BUTTON_SIZE, BUTTON_SIZE
        )
    else:
        gaem.draw_rect(
            x - BUTTON_SIZE / 2, y - BUTTON_SIZE / 2, BUTTON_SIZE, BUTTON_SIZE
        )


if __name__ == '__main__':
    gaem.run(
        GamepadExample(),
        title='Gamepad example',
        vsync=True,
        width=480,
        height=800,
    )
