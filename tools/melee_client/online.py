"""Playing a friend online: finding each other without a server of ours.

The owner (2026-11-13), choosing it over typing IP addresses: "if there is a
better way to do it (STUN server), that sounds way better as a solution".
docs/ai/netplay-p2p.md has the study behind it.

1. A UDP socket asks a public STUN server what its address looks like from
   outside (RFC 5389: a binding request; the answer's XOR-MAPPED-ADDRESS).
   The router keeps that mapping open for a while for this socket.
2. That address, and the one on the local network, become a short code the
   players paste to each other over any chat. A plain "ip:port" works too
   (a forwarded port, a VPN such as Tailscale, the same LAN).
3. Both sides send to each other's addresses at once; each router sees its
   own side's packets go out first and lets the other's in (hole punching).
4. Over the path that worked, a little lobby: who is port 1 and who port 2,
   their characters and colours, the stage, the random seed, the input
   delay. Then each closes the socket and the game opens the same local port
   for the session (src/host/net.c), which the router still maps.

About 70 to 85% of pairs connect this way; two symmetric NATs, or carrier-
grade NAT without hairpinning, do not (the study's numbers). Then a
forwarded port or a VPN does.
"""
import base64
import ipaddress
import json
import os
import random
import socket
import struct
import time

STUN_SERVERS = [("stun.l.google.com", 19302), ("stun.cloudflare.com", 3478)]
MAGIC_COOKIE = 0x2112A442
LOBBY = b"MLBY"
SESSION = struct.pack("<I", 0x4D4E4554)   # the game's packets (net.c)
VERSION = 1


class OnlineError(RuntimeError):
    pass


# ---- STUN ----------------------------------------------------------------------

def stun(sock, servers=STUN_SERVERS, timeout=2.0):
    """(public ip, public port) of `sock` as a STUN server sees it."""
    last = None
    for host, port in servers:
        try:
            addr = socket.getaddrinfo(host, port, socket.AF_INET,
                                      socket.SOCK_DGRAM)[0][4]
        except OSError as e:
            last = e
            continue
        tid = os.urandom(12)
        request = struct.pack(">HHI", 0x0001, 0, MAGIC_COOKIE) + tid
        deadline = time.time() + timeout
        sock.settimeout(0.4)
        while time.time() < deadline:
            try:
                sock.sendto(request, addr)
                data, _ = sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError as e:
                last = e
                break
            got = parse_stun(data, tid)
            if got is not None:
                sock.settimeout(None)
                return got
    sock.settimeout(None)
    raise OnlineError("no STUN server answered (%s)" % (last,))


def parse_stun(data, tid):
    """The mapped address in a binding response for transaction `tid`."""
    if len(data) < 20:
        return None
    kind, length, cookie = struct.unpack(">HHI", data[:8])
    if kind != 0x0101 or cookie != MAGIC_COOKIE or data[8:20] != tid:
        return None
    at, end = 20, 20 + length
    plain = None
    while at + 4 <= end and at + 4 <= len(data):
        atype, alen = struct.unpack(">HH", data[at:at + 4])
        value = data[at + 4:at + 4 + alen]
        if atype in (0x0020, 0x8020) and len(value) >= 8 and value[1] == 1:
            port = struct.unpack(">H", value[2:4])[0] ^ (MAGIC_COOKIE >> 16)
            ip = struct.unpack(">I", value[4:8])[0] ^ MAGIC_COOKIE
            return str(ipaddress.IPv4Address(ip)), port
        if atype == 0x0001 and len(value) >= 8 and value[1] == 1:
            plain = (str(ipaddress.IPv4Address(value[4:8])),
                     struct.unpack(">H", value[2:4])[0])
        at += 4 + alen + (-alen % 4)
    return plain


def lan_address():
    """This machine's address on its local network (no packet is sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))      # a documentation address
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


# ---- codes -------------------------------------------------------------------------

def make_code(public, lan):
    """A code for two addresses (public, LAN): 13 bytes in base32."""
    raw = bytes([VERSION]) + socket.inet_aton(public[0]) + \
        struct.pack(">H", public[1]) + socket.inet_aton(lan[0]) + \
        struct.pack(">H", lan[1])
    text = base64.b32encode(raw).decode().rstrip("=")
    return "-".join(text[i:i + 5] for i in range(0, len(text), 5))


def read_code(text):
    """[(ip, port), ...] to try: from a code, or from "ip:port"."""
    text = text.strip()
    if ":" in text and "." in text:
        host, port = text.rsplit(":", 1)
        return [(socket.gethostbyname(host.strip()), int(port))]
    clean = text.replace("-", "").replace(" ", "").upper()
    try:
        raw = base64.b32decode(clean + "=" * (-len(clean) % 8))
    except ValueError:
        raise OnlineError("not a code: %r" % text)
    if len(raw) != 13 or raw[0] != VERSION:
        raise OnlineError("not a code of this version")
    public = (socket.inet_ntoa(raw[1:5]), struct.unpack(">H", raw[5:7])[0])
    lan = (socket.inet_ntoa(raw[7:11]), struct.unpack(">H", raw[11:13])[0])
    return [public] if lan == public else [public, lan]


# ---- the lobby -----------------------------------------------------------------------

class Lobby:
    """A UDP socket, its code, and the meeting with a friend.

    me: {"nick", "char", "color"}; stage and delay are proposed by whichever
    side becomes port 1."""

    def __init__(self, port=0, use_stun=True):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.port = self.sock.getsockname()[1]
        self.lan = (lan_address(), self.port)
        self.public = stun(self.sock) if use_stun else self.lan
        self.code = make_code(self.public, self.lan)
        self.nonce = random.getrandbits(48)

    def close(self):
        self.sock.close()

    def meet(self, friend, me, stage="final-destination", delay=2,
             timeout=20.0, tick=None):
        """Connect to `friend` (a code or "ip:port"). Returns a dict: peer
        (ip, port), local (0 or 1: the port this side plays), chars and
        colors of ports 0 and 1, stage, seed, delay, bind (the local UDP
        port the game is to use). `tick` is called while waiting (a client
        keeps its window alive)."""
        targets = read_code(friend)
        heard = None          # the address the friend was heard from
        theirs = None         # the friend's hello
        settings = None
        acked = False
        sock = self.sock
        sock.setblocking(False)
        deadline = time.time() + timeout
        last_send = 0.0

        def send(msg, to):
            data = LOBBY + json.dumps(msg).encode()
            try:
                sock.sendto(data, to)
            except OSError:
                pass

        while time.time() < deadline:
            now = time.time()
            if now - last_send > 0.1:
                last_send = now
                hello = dict(t="hello", nonce=self.nonce, heard=theirs
                             is not None, **me)
                for to in ([heard] if heard else targets):
                    send(hello, to)
                if settings is not None and heard:
                    send(dict(t="go", **settings), heard)
            try:
                while True:
                    data, addr = sock.recvfrom(4096)
                    if data.startswith(SESSION) and settings is not None \
                            and addr == heard:
                        acked = True      # its game is already sending
                        continue
                    if not data.startswith(LOBBY):
                        continue
                    msg = json.loads(data[len(LOBBY):].decode())
                    if msg.get("t") == "hello":
                        heard = addr
                        theirs = msg
                    elif msg.get("t") == "go" and theirs is not None:
                        heard = addr
                        for _ in range(5):      # its socket closes next
                            send(dict(t="ack"), addr)
                            time.sleep(0.02)
                        sock.setblocking(True)
                        return self._result(msg, addr, local=1)
                    elif msg.get("t") == "ack" and settings is not None:
                        acked = True
            except BlockingIOError:
                pass
            if theirs is not None and theirs.get("heard") and \
                    settings is None and self.nonce < theirs["nonce"]:
                # the lower nonce is port 1 and chooses the rest
                settings = dict(
                    chars=[me["char"], theirs["char"]],
                    colors=[me.get("color", 0), theirs.get("color", 0)],
                    nicks=[me.get("nick", ""), theirs.get("nick", "")],
                    stage=stage, seed=random.getrandbits(31) | 1,
                    delay=delay)
            if acked:
                sock.setblocking(True)
                return self._result(settings, heard, local=0)
            if tick is not None:
                tick()
            else:
                time.sleep(0.01)
        sock.setblocking(True)
        raise OnlineError("no answer from %s in %d s" % (
            friend, timeout) if theirs is None else
            "heard the friend, but the meeting did not finish")

    def _result(self, settings, addr, local):
        return dict(peer=addr, local=local, bind=self.port,
                    chars=settings["chars"], colors=settings["colors"],
                    nicks=settings.get("nicks", ["", ""]),
                    stage=settings["stage"], seed=settings["seed"],
                    delay=settings["delay"])


# ---- friends ------------------------------------------------------------------------

def friends(save):
    return list(save.get("friends", []))


def add_friend(save, name, code):
    """Keep a friend (a name and a code or "ip:port") in the client's
    save; the same code again renames it."""
    read_code(code)                          # it must parse
    out = [f for f in friends(save) if f["code"] != code]
    out.append(dict(name=name, code=code))
    save["friends"] = out
    return out
