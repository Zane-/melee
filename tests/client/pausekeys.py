"""For the client tests: leaving a match or a drill through the client's
pause menu, with keys on the virtual display.

The pause menu opens on a START tap (let go within 3 s) and runs until a
row is chosen, calling the client's `person` hook every frame: so a test
gives that hook a Chooser, which taps START (Return), goes to the tab with
the row asked for (R, the s key), moves down (the Down key, one frame
pressed, one not) until the row is in focus, and presses A (x).
"""


class Chooser:
    def __init__(self, client, ident):
        self.c = client
        self.ident = ident
        self.step = 0
        self.down = False
        self.done = False

    def __call__(self, game):
        """One frame. True once the row has been chosen."""
        c = self.c
        if self.done:
            return True
        if self.step == 0:
            game.key("Return")
            self.step = 1
        elif self.step == 1:
            game.key("Return", False)        # let go: the menu opens
            self.step = 2
        elif self.step == 2:
            if not c.pause_open:
                return False
            if self.down:
                game.key("Down", False)
                game.key("s", False)
                self.down = False
            elif self.ident not in getattr(c, "pause_idents",
                                           [self.ident]):
                game.key("s")                # R: the next tab
                self.down = True
            elif c.pause_focus == self.ident:
                game.key("x")
                self.step = 3
            else:
                game.key("Down")
                self.down = True
        elif self.step == 3:
            game.key("x", False)
            self.done = True
        return self.done


def leave(client, game, ident, frames):
    """Out of a match (free play, Versus): choose `ident` in the pause menu,
    running `frames(n)` (the test's way of playing n frames)."""
    chooser = Chooser(client, ident)
    before = client.person
    client.person = lambda g, frame: chooser(g)
    try:
        for _ in range(400):
            if chooser.done or client.screen not in ("match", "versus",
                                                      "drill"):
                break
            chooser(game) if not client.pause_open else None
            frames(1)
    finally:
        client.person = before
    game.key("x", False)
    game.key("Return", False)
    game.key("Down", False)
    game.key("s", False)
    frames(6)
