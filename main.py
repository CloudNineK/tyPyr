import urwid as u
import random

# TODO: Add WPM


class Prompt(u.Filler):
    def __init__(self, prompt: str):
        self.orig = prompt
        self.com = ''  # Completed Text
        self.incor = ''
        self.incom = prompt  # Incomplete Text
        self.body = u.Text([('complete', self.com),
                            ('incomplete', self.incom)])
        self.length = 0
        self.flag = [False, 0]

    def update(self, flag):
        if flag:
            self.body.set_text([('complete', self.com),
                                ('incorrect', self.incor),
                                ('incomplete', self.incom)])
        else:
            self.body.set_text([('complete', self.com),
                                ('incomplete', self.incom)])

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

prompt = Prompt(text)

div = u.Divider()
temp = u.Text("test")

response = u.Edit(('response', ''))


def on_resp_change(resp, newtext):
    prompt.process(newtext)
    temp.set_text(str(prompt.length) + ' ' + str(prompt.flag[1]) + ' ' + str(prompt.flag[0]) + ' ' + newtext[-1] + ' ' + prompt.orig[prompt.flag[1] - 1] + ' ' + prompt.incor)


u.connect_signal(response, 'change', on_resp_change)

pile = u.Pile([prompt.body, div, temp, response])
top = u.Filler(u.LineBox(pile))  # topmost widget must be a box

loop = u.MainLoop(top, palette, unhandled_input=exit_on_q)
loop.run()
