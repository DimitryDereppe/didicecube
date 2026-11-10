"""Moteur de mouvements du cube : état de 54 stickers et 18 mouvements de base.

L'état est une chaîne (ou un tuple) de 54 lettres, une par sticker, faces dans l'ordre U, D, L, R, F, B
(dessus, dessous, gauche, droite, avant, arrière), 9 stickers par face, de gauche à droite et de haut en bas,
la face vue de l'extérieur. Couleurs : B blanc, J jaune, R rouge, O orange, V vert, L bleu.

Les mouvements ne sont pas écrits à la main : ils sont calculés à partir de la position 3D de chaque
sticker, tournée d'un quart de tour. Le JavaScript reçoit ces mêmes permutations (une seule source de vérité).
"""
import random

FACES = "UDLRFB"
COULEURS = {"B": "blanc", "J": "jaune", "R": "rouge", "O": "orange", "V": "vert", "L": "bleu"}
NOMS_FACES = {"U": "dessus", "D": "dessous", "L": "gauche", "R": "droite", "F": "avant", "B": "arrière"}
RESOLU = "B" * 9 + "J" * 9 + "O" * 9 + "R" * 9 + "V" * 9 + "L" * 9

# Repère de chaque face (x vers la droite, y vers le haut, z vers soi) : normale sortante, puis les
# directions « droite » et « haut » de la face vue de l'extérieur (droite × haut = normale).
_REPERES = {
    "U": ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
    "D": ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    "L": ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
    "R": ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
    "F": ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
    "B": ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
}


def _plus(*vecteurs):
    return tuple(sum(c) for c in zip(*vecteurs, strict=True))


def _fois(k, v):
    return tuple(k * c for c in v)


def _vectoriel(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _scalaire(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def _sticker(k):
    """Position (centre du petit cube) et normale du sticker numéro k."""
    normale, droite, haut = _REPERES[FACES[k // 9]]
    ligne, colonne = divmod(k % 9, 3)
    return _plus(normale, _fois(colonne - 1, droite), _fois(1 - ligne, haut)), normale


STICKERS = [_sticker(k) for k in range(54)]
_INDICE = {s: k for k, s in enumerate(STICKERS)}


def _quart_horaire(face):
    """Permutation d'un quart de tour horaire (vu de l'extérieur) : nouveau[i] = ancien[perm[i]]."""
    axe = _REPERES[face][0]
    perm = list(range(54))
    for k, (position, normale) in enumerate(STICKERS):
        if _scalaire(position, axe) != 1:
            continue
        # Rotation de -90° autour de l'axe : v -> (v·a)a - a×v
        tourne = lambda v: _plus(_fois(_scalaire(v, axe), axe), _fois(-1, _vectoriel(axe, v)))  # noqa: E731
        perm[_INDICE[(tourne(position), tourne(normale))]] = k
    return tuple(perm)


def compose(*perms):
    """Permutation équivalente à appliquer les permutations dans l'ordre donné."""
    resultat = tuple(range(54))
    for p in perms:
        resultat = tuple(resultat[i] for i in p)
    return resultat


MOUVEMENTS = {}
for _f in FACES:
    _q = _quart_horaire(_f)
    MOUVEMENTS[_f] = _q
    MOUVEMENTS[_f + "2"] = compose(_q, _q)
    MOUVEMENTS[_f + "'"] = compose(_q, _q, _q)


def lit_sequence(texte):
    """« R U R' » -> ["R", "U", "R'"] ; refuse les mouvements inconnus."""
    mouvements = texte.split()
    for m in mouvements:
        if m not in MOUVEMENTS:
            raise ValueError(f"Mouvement inconnu : {m}")
    return mouvements


def applique(etat, mouvements):
    """Applique une suite de mouvements (liste ou texte) ; renvoie une chaîne de 54 lettres."""
    if isinstance(mouvements, str):
        mouvements = lit_sequence(mouvements)
    for m in mouvements:
        perm = MOUVEMENTS[m]
        etat = [etat[i] for i in perm]
    return "".join(etat)


def applique_perm(etat, perm):
    return tuple(etat[i] for i in perm)


def inverse(mouvements):
    """Inverse d'une suite : ordre renversé, chaque mouvement inversé (U <-> U', U2 inchangé)."""
    def inv(m):
        return m[0] if m.endswith("'") else m if m.endswith("2") else m + "'"
    return [inv(m) for m in reversed(mouvements)]


def simplifie(mouvements):
    """Fusionne les mouvements consécutifs d'une même face (U U -> U2, U U' -> rien)."""
    quarts = {"": 1, "2": 2, "'": 3}
    pile = []
    for m in mouvements:
        face, n = m[0], quarts[m[1:]]
        if pile and pile[-1][0] == face:
            n = (pile.pop()[1] + n) % 4
        if n:
            pile.append((face, n))
    noms = {1: "", 2: "2", 3: "'"}
    return [face + noms[n] for face, n in pile]


def melange(nombre=25, graine=None):
    """Mélange aléatoire : renvoie (état, mouvements). Deux mouvements de suite ne touchent pas la même face."""
    hasard = random.Random(graine)
    mouvements = []
    while len(mouvements) < nombre:
        m = hasard.choice(FACES) + hasard.choice(["", "'", "2"])
        if mouvements and mouvements[-1][0] == m[0]:
            continue
        mouvements.append(m)
    return applique(RESOLU, mouvements), mouvements


def est_resolu(etat):
    return all(len(set(etat[f * 9:f * 9 + 9])) == 1 for f in range(6))


# Petits cubes : stickers regroupés par position (8 coins de 3 stickers, 12 arêtes de 2).
_PIECES = {}
for _k, (_pos, _n) in enumerate(STICKERS):
    _PIECES.setdefault(_pos, []).append(_k)
COINS = [tuple(v) for v in _PIECES.values() if len(v) == 3]
ARETES = [tuple(v) for v in _PIECES.values() if len(v) == 2]
CENTRES = [f * 9 + 4 for f in range(6)]


def face_de(k):
    return FACES[k // 9]
