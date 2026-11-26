"""For the client tests: leaving a match or a drill through the client's
pause menu, with keys on the virtual display.

The pause menu opens on a START tap (let go within 3 s) and runs until a
row is chosen, calling the client's `person` hook every frame: so a test
gives that hook a Chooser, which taps START (Return, held two frames, and
again if the menu has not opened two seconds later), goes to the tab with
the row asked for (R, the s key), moves down (the Down key, one frame
pressed, one not) until the row is in focus, and presses A (x).
"""


class Chooser:
    AGAIN = 120         # frames without the menu before START is tapped again

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
            self.step, self.held = 1, 0
        elif self.step == 1:
            # held two frames (pressed and let go inside one, a key is not
            # seen), then let go: the menu opens
            self.held += 1
            if self.held < 2:
                return False
            game.key("Return", False)
            self.step, self.waited = 2, 0
        elif self.step == 2:
            if not c.pause_open:
                # (not seen all the same, on a busy machine: again)
                self.waited += 1
                if self.waited > self.AGAIN:
                    self.step = 0
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
    """Out of a match (Versus, the Lab): choose `ident` in the pause menu,
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
