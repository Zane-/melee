"""Names: the 26 playable characters and the canonical move keys.

Character `id` is the slug used everywhere in data/ (file names, links).
`dat` is the two-letter code of the fighter's data file (PlFx.dat).
`code` is the fighter's module under src/melee/ft/kinds/. `specials` gives
the community names of the four special moves (neutral, side, up, down).
"""

ROSTER = [
    {"id": "bowser", "code": "ftKoopa", "name": "Bowser", "dat": "Kp", "raw": "Bowser",
     "specials": ["Fire Breath", "Koopa Klaw", "Whirling Fortress",
                  "Bowser Bomb"]},
    {"id": "captain-falcon", "code": "ftCaptain", "name": "Captain Falcon", "dat": "Ca",
     "raw": "Captain_Falcon",
     "specials": ["Falcon Punch", "Raptor Boost", "Falcon Dive",
                  "Falcon Kick"]},
    {"id": "donkey-kong", "code": "ftDonkey", "name": "Donkey Kong", "dat": "Dk",
     "raw": "Donkey_Kong",
     "specials": ["Giant Punch", "Headbutt", "Spinning Kong", "Hand Slap"]},
    {"id": "dr-mario", "code": "ftDrMario", "name": "Dr. Mario", "dat": "Dr", "raw": "Dr_Mario",
     "specials": ["Megavitamins (pills)", "Super Sheet (cape)",
                  "Super Jump Punch", "Dr. Tornado"]},
    {"id": "falco", "code": "ftFalco", "name": "Falco", "dat": "Fc", "raw": "Falco",
     "specials": ["Blaster (laser)", "Falco Phantasm (side B)",
                  "Fire Bird", "Reflector (shine)"]},
    {"id": "fox", "code": "ftFox", "name": "Fox", "dat": "Fx", "raw": "Fox",
     "specials": ["Blaster (laser)", "Fox Illusion (side B)", "Fire Fox",
                  "Reflector (shine)"]},
    {"id": "ganondorf", "code": "ftGanon", "name": "Ganondorf", "dat": "Gn", "raw": "Ganon",
     "specials": ["Warlock Punch", "Gerudo Dragon", "Dark Dive",
                  "Wizard's Foot"]},
    {"id": "ice-climbers", "code": "ftPopo", "name": "Ice Climbers", "dat": "Pp",
     "raw": "Ice_Climbers", "partner_dat": "Nn",
     "specials": ["Ice Shot", "Squall Hammer", "Belay", "Blizzard"]},
    {"id": "jigglypuff", "code": "ftPurin", "name": "Jigglypuff", "dat": "Pr",
     "raw": "Jigglypuff",
     "specials": ["Rollout", "Pound", "Sing", "Rest"]},
    {"id": "kirby", "code": "ftKirby", "name": "Kirby", "dat": "Kb", "raw": "Kirby",
     "specials": ["Swallow (Inhale)", "Hammer", "Final Cutter", "Stone"]},
    {"id": "link", "code": "ftLink", "name": "Link", "dat": "Lk", "raw": "Link",
     "specials": ["Bow", "Boomerang", "Spin Attack", "Bomb"]},
    {"id": "luigi", "code": "ftLuigi", "name": "Luigi", "dat": "Lg", "raw": "Luigi",
     "specials": ["Fireball", "Green Missile", "Super Jump Punch",
                  "Luigi Cyclone"]},
    {"id": "mario", "code": "ftMario", "name": "Mario", "dat": "Mr", "raw": "Mario",
     "specials": ["Fireball", "Cape", "Super Jump Punch", "Mario Tornado"]},
    {"id": "marth", "code": "ftMars", "name": "Marth", "dat": "Ms", "raw": "Marth",
     "specials": ["Shield Breaker", "Dancing Blade", "Dolphin Slash",
                  "Counter"]},
    {"id": "mewtwo", "code": "ftMewtwo", "name": "Mewtwo", "dat": "Mt", "raw": "Mewtwo",
     "specials": ["Shadow Ball", "Confusion", "Teleport", "Disable"]},
    {"id": "mr-game-and-watch", "code": "ftGameWatch", "name": "Mr. Game & Watch", "dat": "Gw",
     "raw": "Mr_Game_and_Watch",
     "specials": ["Chef", "Judgment (Judge)", "Fire", "Oil Panic (bucket)"]},
    {"id": "ness", "code": "ftNess", "name": "Ness", "dat": "Ns", "raw": "Ness",
     "specials": ["PK Flash", "PK Fire", "PK Thunder", "PSI Magnet"]},
    {"id": "peach", "code": "ftPeach", "name": "Peach", "dat": "Pe", "raw": "Peach",
     "specials": ["Toad", "Peach Bomber", "Peach Parasol",
                  "Vegetable (turnip pull)"]},
    {"id": "pichu", "code": "ftPichu", "name": "Pichu", "dat": "Pc", "raw": "Pichu",
     "specials": ["Thunder Jolt", "Skull Bash", "Agility", "Thunder"]},
    {"id": "pikachu", "code": "ftPikachu", "name": "Pikachu", "dat": "Pk", "raw": "Pikachu",
     "specials": ["Thunder Jolt", "Skull Bash", "Quick Attack", "Thunder"]},
    {"id": "roy", "code": "ftEmblem", "name": "Roy", "dat": "Fe", "raw": "Roy",
     "specials": ["Flare Blade", "Double-Edge Dance", "Blazer", "Counter"]},
    {"id": "samus", "code": "ftSamus", "name": "Samus", "dat": "Ss", "raw": "Samus",
     "specials": ["Charge Shot", "Missile", "Screw Attack", "Bomb"]},
    {"id": "sheik", "code": "ftSeak", "name": "Sheik", "dat": "Sk", "raw": "Sheik",
     "specials": ["Needle Storm (needles)", "Chain", "Vanish",
                  "Transform"]},
    {"id": "yoshi", "code": "ftYoshi", "name": "Yoshi", "dat": "Ys", "raw": "Yoshi",
     "specials": ["Egg Lay", "Egg Roll", "Egg Throw", "Yoshi Bomb"]},
    {"id": "young-link", "code": "ftCLink", "name": "Young Link", "dat": "Cl",
     "raw": "Young_Link",
     "specials": ["Fire Bow", "Boomerang", "Spin Attack", "Bomb"]},
    {"id": "zelda", "code": "ftZelda", "name": "Zelda", "dat": "Zd", "raw": "Zelda",
     "specials": ["Nayru's Love", "Din's Fire", "Farore's Wind",
                  "Transform"]},
]

BY_ID = {e["id"]: e for e in ROSTER}

# subaction short name -> (canonical key, display name, group)
MOVE_NAMES = {
    "Attack11": ("jab1", "Jab 1", "ground"),
    "Attack12": ("jab2", "Jab 2", "ground"),
    "Attack13": ("jab3", "Jab 3", "ground"),
    "Attack100Start": ("rapid_jab_start", "Rapid jab start", "ground"),
    "Attack100Loop": ("rapid_jab_loop", "Rapid jab loop", "ground"),
    "Attack100End": ("rapid_jab_end", "Rapid jab end", "ground"),
    "AttackDash": ("dash_attack", "Dash attack", "ground"),
    "AttackS3Hi": ("ftilt_high", "Forward tilt (angled up)", "ground"),
    "AttackS3HiS": ("ftilt_mid_high", "Forward tilt (slightly up)",
                    "ground"),
    "AttackS3S": ("ftilt", "Forward tilt", "ground"),
    "AttackS3LwS": ("ftilt_mid_low", "Forward tilt (slightly down)",
                    "ground"),
    "AttackS3Lw": ("ftilt_low", "Forward tilt (angled down)", "ground"),
    "AttackHi3": ("utilt", "Up tilt", "ground"),
    "AttackLw3": ("dtilt", "Down tilt", "ground"),
    "AttackS4Hi": ("fsmash_high", "Forward smash (angled up)", "ground"),
    "AttackS4HiS": ("fsmash_mid_high", "Forward smash (slightly up)",
                    "ground"),
    "AttackS4S": ("fsmash", "Forward smash", "ground"),
    "AttackS4": ("fsmash", "Forward smash", "ground"),
    "AttackS4LwS": ("fsmash_mid_low", "Forward smash (slightly down)",
                    "ground"),
    "AttackS4Lw": ("fsmash_low", "Forward smash (angled down)", "ground"),
    "AttackHi4": ("usmash", "Up smash", "ground"),
    "AttackLw4": ("dsmash", "Down smash", "ground"),
    "AttackAirN": ("nair", "Neutral air", "air"),
    "AttackAirF": ("fair", "Forward air", "air"),
    "AttackAirB": ("bair", "Back air", "air"),
    "AttackAirHi": ("uair", "Up air", "air"),
    "AttackAirLw": ("dair", "Down air", "air"),
    "Catch": ("grab", "Grab", "grab"),
    "CatchDash": ("dash_grab", "Dash grab", "grab"),
    "CatchAttack": ("pummel", "Pummel", "grab"),
    "ThrowF": ("fthrow", "Forward throw", "grab"),
    "ThrowB": ("bthrow", "Back throw", "grab"),
    "ThrowHi": ("uthrow", "Up throw", "grab"),
    "ThrowLw": ("dthrow", "Down throw", "grab"),
    "EscapeN": ("spotdodge", "Spot dodge", "defense"),
    "EscapeF": ("roll_forward", "Roll forward", "defense"),
    "EscapeB": ("roll_backward", "Roll backward", "defense"),
    "EscapeAir": ("airdodge", "Air dodge", "defense"),
    "Passive": ("tech_in_place", "Tech in place", "tech"),
    "PassiveStandF": ("tech_roll_forward", "Tech roll forward", "tech"),
    "PassiveStandB": ("tech_roll_backward", "Tech roll backward", "tech"),
    "PassiveWall": ("wall_tech", "Wall tech", "tech"),
    "PassiveWallJump": ("wall_tech_jump", "Wall tech jump", "tech"),
    "PassiveCeil": ("ceiling_tech", "Ceiling tech", "tech"),
    "DownBoundU": ("missed_tech_bounce_faceup",
                   "Missed tech bounce (face up)", "tech"),
    "DownBoundD": ("missed_tech_bounce_facedown",
                   "Missed tech bounce (face down)", "tech"),
    "DownStandU": ("getup_stand_faceup", "Getup stand (face up)", "tech"),
    "DownStandD": ("getup_stand_facedown", "Getup stand (face down)",
                   "tech"),
    "DownAttackU": ("getup_attack_faceup", "Getup attack (face up)",
                    "tech"),
    "DownAttackD": ("getup_attack_facedown", "Getup attack (face down)",
                    "tech"),
    "DownFowardU": ("getup_roll_forward_faceup",
                    "Getup roll forward (face up)", "tech"),
    "DownFowardD": ("getup_roll_forward_facedown",
                    "Getup roll forward (face down)", "tech"),
    "DownBackU": ("getup_roll_backward_faceup",
                  "Getup roll backward (face up)", "tech"),
    "DownBackD": ("getup_roll_backward_facedown",
                  "Getup roll backward (face down)", "tech"),
    "CliffClimbQuick": ("ledge_getup", "Ledge getup (<100%)", "ledge"),
    "CliffClimbSlow": ("ledge_getup_slow", "Ledge getup (>=100%)", "ledge"),
    "CliffAttackQuick": ("ledge_attack", "Ledge attack (<100%)", "ledge"),
    "CliffAttackSlow": ("ledge_attack_slow", "Ledge attack (>=100%)",
                        "ledge"),
    "CliffEscapeQuick": ("ledge_roll", "Ledge roll (<100%)", "ledge"),
    "CliffEscapeSlow": ("ledge_roll_slow", "Ledge roll (>=100%)", "ledge"),
    "CliffJumpQuick1": ("ledge_jump_1", "Ledge jump part 1 (<100%)",
                        "ledge"),
    "CliffJumpQuick2": ("ledge_jump_2", "Ledge jump part 2 (<100%)",
                        "ledge"),
    "CliffJumpSlow1": ("ledge_jump_slow_1", "Ledge jump part 1 (>=100%)",
                       "ledge"),
    "CliffJumpSlow2": ("ledge_jump_slow_2", "Ledge jump part 2 (>=100%)",
                       "ledge"),
    "CliffCatch": ("ledge_catch", "Ledge grab", "ledge"),
    "Landing": ("landing", "Landing (animation)", "misc"),
    "Dash": ("dash", "Dash (animation)", "misc"),
    "Turn": ("turn", "Turn (animation)", "misc"),
    "RunBrake": ("run_brake", "Run brake (animation)", "misc"),
    "GuardOn": ("shield_on", "Shield startup (animation)", "misc"),
    "GuardOff": ("shield_off", "Shield release", "misc"),
    "Rebound": ("rebound", "Clank rebound", "misc"),
    "Appeal": ("taunt", "Taunt", "misc"),
}

SPECIAL_DIRS = {"N": 0, "S": 1, "Hi": 2, "Lw": 3}


def snake(name):
    out = []
    for i, c in enumerate(name):
        if c.isupper() and i:
            prev_lower = not name[i - 1].isupper()
            next_lower = i + 1 < len(name) and name[i + 1].islower()
            if prev_lower or next_lower:
                out.append("_")
        out.append(c.lower())
    return "".join(out)


def move_key(short):
    """Canonical key for a subaction short name, or None to skip it."""
    if short in MOVE_NAMES:
        return MOVE_NAMES[short][0]
    if short.startswith("Special"):
        return snake(short)
    return None
