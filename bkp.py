import urwid as u


class Prompt(u.Filler):
    def __init__(self, prompt: str):
        self.orig = prompt
        self.com = ''  # Completed Text
        self.incom = prompt  # Incomplete Text
        self.body = u.Text([('complete', self.com),
                            ('incomplete', self.incom)], align='center')
        self.length = 0
        self.flag = [False, 0]

    def update(self):
        self.body.set_text([('complete', self.com),
                            ('incomplete', self.incom)])

    def process(self, resp):

        def add():
            self.com += self.incom[0]
            self.incom = self.incom[1:]
            self.update()
            self.length += 1

        def rem():
            self.incom = self.com[-1] + self.incom
            self.com = self.com[:len(self.com) - 1]
            self.update()
            self.length -= 1

        entry = resp[-1]
        current = self.orig[self.length]

        # Upon entry of invalid character: change state
        if entry != current and not self.flag[0]:
            if len(resp) > self.length:
                self.flag = [True, len(resp)]

        # Check state for invalid charcater
        if self.flag[0]:
            if self.length == self.flag[1]:
                if entry == self.orig[self.flag[1]]:
                    self.flag = [False, 0]

                # Insert / Delete
                elif len(resp) < self.length:
                    self.length -= 1
                else:
                    self.length += 1

            # Insert / Delete
            if len(resp) < self.length:
                self.length -= 1
            else:
                self.length += 1

        # Upon adding a character
        elif len(resp) > self.length:
            add()

        # Upon removing a character
        else:
            rem()


def exit_on_q(key):
    if key == 'ctrl q':
        raise u.ExitMainLoop()


palette = [
    ('complete', 'light blue', 'default'),
    ('incomplete', 'light red', 'default')]

text = "The quick brown fox jumped over the lazy dog."
prompt = Prompt(text)

div = u.Divider()
temp = u.Text("test")

response = u.Edit(('response', ''))


def on_resp_change(resp, newtext):
    prompt.process(newtext)
    temp.set_text(str(prompt.length) + ' ' + str(prompt.flag[1]) + str(prompt.flag[0]))


u.connect_signal(response, 'change', on_resp_change)

pile = u.Pile([prompt.body, div, temp, response])
top = u.Filler(u.LineBox(pile))  # topmost widget must be a box

loop = u.MainLoop(top, palette, unhandled_input=exit_on_q)
loop.run()
