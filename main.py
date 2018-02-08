import urwid as u

import random
import datetime
import threading

# TODO: Add WPM


class Prompt():
    """ Container for text processing"""

    def __init__(self, prompt: str):
        """ Prompt("Prompt Text")

        Args:
            prompt (str): Original prompt
        """
        self.orig = prompt
        self.com = ''  # Completed Text
        self.incor = ''  # Incorrect Text
        self.incom = prompt  # Incomplete Text

        self.body = u.Text([('complete', self.com),
                            ('incomplete', self.incom)])

        self.length = 0
        self.ccount = 0  # Character count
        self.wpm = 0
        self.timeStart = None
        self.flag = [False, 0]


    def update(self, flag):
        if flag:
            self.body.set_text([('complete', self.com),
                                ('incorrect', self.incor),
                                ('incomplete', self.incom)])
        else:
            self.body.set_text([('complete', self.com),
                                ('incomplete', self.incom)])
            self.ccount += 1

    def wpm_update(self):
        """ (characters typed / 5 characters) / (seconds / 60)"""
        elapsedSeconds = (datetime.datetime.now() - self.timeStart)
        elapsedMinutes = (elapsedSeconds.total_seconds()) / 60
        wpm = int((self.ccount / 5) / elapsedMinutes)
        self.wpm = wpm
        return str(self.wpm)

    def process(self, resp):

        def add():
            if self.flag[0]:
                self.incor += self.incom[0]
            else:
                self.com += self.incom[0]

            self.incom = self.incom[1:]
            self.update(self.flag[0])
            self.length += 1

        def rem():
            if self.flag[0]:
                self.incom = self.incor[-1] + self.incom
                self.incor = self.incor[:len(self.incor) - 1]
            else:
                self.incom = self.com[-1] + self.incom
                self.com = self.com[:len(self.com) - 1]

            if len(self.incor) == 0:
                self.flag = [False, 0]
            self.update(self.flag[0])
            self.length -= 1

        entry = resp[-1]  # Last character entered
        current = self.orig[self.length]  # Next character to check against
        added = len(resp) > self.length  # True if character was added

        # Check state for invalid charcater
        if self.flag[0]:

            # Insert / Delete
            if added:
                add()
            else:
                rem()

        # Add character
        elif added:

            # Upon entry of invalid character: flag the last correct character
            if entry != current and not self.flag[0]:
                self.flag = [True, self.length]
                add()
            else:
                add()

        # Delete character
        else:
            rem()


def exit_on_q(key):
    if key == 'ctrl q':
        raise u.ExitMainLoop()


palette = [
    ('complete', 'light blue', 'default'),
    ('incomplete', 'white', 'default'),
    ('incorrect', 'light red', 'default')]

with open('prompts.txt', 'r') as f:
    text = random.choice(f.readlines()).strip()

# Widgets
prompt = Prompt(text)
div = u.Divider()
wpm = u.Text("Words Per Minute: ")

response = u.Edit(('response', ''))


def on_resp_change(resp, newtext):
    """ Event signaling a change in the response text box"""

    prompt.process(newtext)

    # Start timing on first input
    if prompt.timeStart is None:
        prompt.timeStart = datetime.datetime.now()

    # Update WPM
    wpm.set_text("Words Per Minute: " + prompt.wpm_update())


u.connect_signal(response, 'change', on_resp_change)

pile = u.Pile([prompt.body, div, wpm, response])
top = u.Filler(u.LineBox(pile))  # topmost widget must be a box widget

loop = u.MainLoop(top, palette, unhandled_input=exit_on_q)
loop.run()
