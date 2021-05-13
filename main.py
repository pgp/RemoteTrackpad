__version__ = '1.0'

import time

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.utils import platform

from hashview import HashView

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException
from random import random
from math import sqrt

from xreclient import *

"""
Web source:
https://kivy.org/doc/stable/examples/gen__demo__touchtracer__main__py.html
"""

def showPopup(data):
    x, y = 400, 400
    p = Popup(size_hint=(None, None), size=(x, y), content=HashView(data, 16, 3, x, y), auto_dismiss=True)
    p.open()

def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o


class Touchtracer(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running_app = App.get_running_app()
        self.only_click = False

    def on_touch_down(self, touch):
        logging.info('on touch down')
        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 5
        if 'pressure' in touch.profile:
            ud['pressure'] = touch.pressure
            pointsize = (touch.pressure * 100000) ** 2
        ud['color'] = random()

        with self.canvas:
            Color(ud['color'], 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y), source='particle.png',
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        self.update_touch_label(ud['label'], touch, start_move=True)
        self.add_widget(ud['label'])
        touch.grab(self)
        self.only_click = True
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        # logging.info('on touch move')
        if not self.running_app.is_android:
            self.only_click = False
        else:
            self.only_click = 1 if self.only_click is True else False
        ud = touch.ud
        ud['lines'][0].pos = touch.x, 0
        ud['lines'][1].pos = 0, touch.y

        index = -1

        while True:
            try:
                points = ud['lines'][index].points
                oldx, oldy = points[-2], points[-1]
                break
            except:
                index -= 1

        points = calculate_points(oldx, oldy, touch.x, touch.y)

        # if pressure changed create a new point instruction
        if 'pressure' in ud:
            if not .95 < (touch.pressure / ud['pressure']) < 1.05:
                g = ud['group']
                pointsize = (touch.pressure * 100000) ** 2
                with self.canvas:
                    Color(ud['color'], 1, 1, mode='hsv', group=g)
                    ud['lines'].append(
                        Point(points=(), source='particle.png',
                              pointsize=pointsize, group=g))

        if points:
            try:
                lp = ud['lines'][-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass

        ud['label'].pos = touch.pos
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        self.update_touch_label(ud['label'], touch, start_move=False)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        logging.info('on touch up')
        if self.only_click:
            logging.info('down + up : click')
            self.running_app.left_down()
            self.running_app.left_up()
            self.only_click = False
        touch.ungrab(self)
        ud = touch.ud
        self.canvas.remove_group(ud['group'])
        self.remove_widget(ud['label'])

    def update_touch_label(self, label, touch, start_move):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20
        if self.running_app.remote_trackpad is not None:
            # invert y-axis direction for windows compatibility
            logging.debug(f'Debug x: {touch.x}, type {type(touch.x)}; {touch.y}, type {type(touch.y)}')
            xx,yy = int(touch.x), int(max(self.height - touch.y, 0.0))
            self.running_app.remote_trackpad.move_cursor(xx, yy, start_move)


class TouchtracerApp(App):
    title = 'Touchtracer'
    icon = 'icon.png'

    def build(self):
        self.is_android = platform == 'android'
        self.tt = Builder.load_file("touchtracer.kv")
        self.remote_trackpad = RemoteTrackpad(self.toggle_connect_widgets, showPopup)
        self.is_connected = False
        return self.tt

    def on_pause(self):
        try:
            self.remote_trackpad.Q.paused = True
            logging.info('Sent pause event')
        except:
            logging.info('Not connected, no pause event to send')
            pass
        return True

    def on_resume(self):
        try:
            self.remote_trackpad.Q.paused = False
            self.remote_trackpad.Q.data_available.set()
            logging.info('Sent resume event')
        except:
            logging.info('Not connected, no resume event to send')
            pass

    def toggle_connect_widgets(self, connected):
        c = not not connected
        self.is_connected = c
        self.root.ids.connect_host_input.disabled = c
        self.root.ids.connect_btn.text = 'Disconnect' if c else 'Connect'
        self.root.ids.left_click_btn.disabled = not c
        self.root.ids.right_click_btn.disabled = not c

    def left_down(self):
        logging.debug('Left down kv')
        self.remote_trackpad.mouse_buttons(self.remote_trackpad.CODES.LEFTDOWN)

    def left_up(self):
        logging.debug('Left up kv')
        self.remote_trackpad.mouse_buttons(self.remote_trackpad.CODES.LEFTUP)

    def right_down(self):
        logging.debug('Right down kv')
        self.remote_trackpad.mouse_buttons(self.remote_trackpad.CODES.RIGHTDOWN)

    def right_up(self):
        logging.debug('Right up kv')
        self.remote_trackpad.mouse_buttons(self.remote_trackpad.CODES.RIGHTUP)

    def connect_remote(self):
        if not self.is_connected:
            try:
                host = self.root.ids.connect_host_input.text
                logging.info(f'Trying to connect to: {host}')
                self.remote_trackpad.connect(host, port=11111)
                logging.info('Connected')
            except BaseException as e:
                logging.error(e)
                logging.error('Unable to connect')
        else:
            self.remote_trackpad.disconnect()


if __name__ == '__main__':
    TouchtracerApp().run()