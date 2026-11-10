"""Résolution couche par couche (méthode débutant), avec une explication pour chaque étape.

Chaque étape place une pièce (ou un groupe de pièces) sans défaire les précédentes. Les algorithmes sont
écrits pour la face avant, puis « tournés » vers chacune des quatre faces de côté. Pour chaque pièce,
une courte recherche essaie les algorithmes connus (et quelques tours du dessus) et garde la suite la plus
courte qui place la pièce sans rien déranger : pas de cas oublié dans un tableau écrit à la main.

La première couronne est construite sur la face du dessous, la dernière couche sur celle du dessus.
"""
from . import moteur
from .moteur import ARETES, COINS, COULEURS, FACES, MOUVEMENTS, applique_perm, compose, face_de

COTES = "FRBL"  # faces de côté, dans l'ordre où elles se suivent vues du dessus (chacune a la suivante à sa droite)


class EtatImpossible(ValueError):
    """L'état saisi ne correspond à aucun cube réel (sticker mal saisi, pièce retournée…)."""


def _vers_face(sequence, avant):
    """Réécrit une suite pensée « face avant = F » pour une autre face avant (rotation du cube sur l'axe vertical)."""
    i = COTES.index(avant)
    correspondance = {c: COTES[(j + i) % 4] for j, c in enumerate(COTES)}
    correspondance.update(U="U", D="D")
    return [correspondance[m[0]] + m[1:] for m in moteur.lit_sequence(sequence)]


class _Macro:
    def __init__(self, mouvements, est_u=False):
        self.mouvements = list(mouvements)
        self.perm = compose(*(MOUVEMENTS[m] for m in self.mouvements))
        self.est_u = est_u


_TOURS_U = [_Macro([m], est_u=True) for m in ("U", "U'", "U2")]


def _macros(*sequences, tours_u=True):
    liste = list(_TOURS_U) if tours_u else []
    for sequence in sequences:
        for avant in COTES:
            liste.append(_Macro(_vers_face(sequence, avant)))
    return liste


def _cherche(etat, macros, but, profondeur_max):
    """Suite de macros la plus courte (au plus profondeur_max) qui rend but(état) vrai."""
    def explore(e, profondeur, precedent_u):
        if profondeur == 0:
            return [] if but(e) else None
        for macro in macros:
            if macro.est_u and precedent_u:
                continue  # deux tours du dessus de suite : déjà couverts par un seul
            suite = explore(applique_perm(e, macro.perm), profondeur - 1, macro.est_u)
            if suite is not None:
                return macro.mouvements + suite
        return None

    for profondeur in range(profondeur_max + 1):
        suite = explore(etat, profondeur, False)
        if suite is not None:
            return suite
    raise EtatImpossible(
        "Ce cube ne peut pas être résolu : une pièce a sans doute été mal saisie (deux stickers inversés, "
        "un coin ou une arête retourné). Vérifiez les couleurs, face par face."
    )


# --- Lecture de l'état ------------------------------------------------------------

def _centre(etat, face):
    return etat[FACES.index(face) * 9 + 4]


def _piece_cible(etat, faces):
    """Stickers de l'emplacement délimité par ces faces (ex. "DF" : l'arête entre dessous et avant)."""
    for piece in ARETES + COINS:
        if {face_de(k) for k in piece} == set(faces):
            return piece
    raise KeyError(faces)


def _en_place(etat, piece):
    return all(etat[k] == _centre(etat, face_de(k)) for k in piece)


def _ou_est(etat, couleurs):
    """Emplacement (ensemble de faces) où se trouve la pièce de ces couleurs."""
    for piece in ARETES + COINS:
        if sorted(etat[k] for k in piece) == sorted(couleurs):
            return {face_de(k) for k in piece}
    raise EtatImpossible("Une pièce du cube est introuvable : vérifiez les couleurs saisies.")


def _nom(etat, faces):
    return "-".join(COULEURS[_centre(etat, f)] for f in faces)


def _droite(face):
    return COTES[(COTES.index(face) + 1) % 4]


def verifie(etat):
    """Vérifie qu'un état saisi est plausible ; lève EtatImpossible avec un message clair sinon."""
    if len(etat) != 54 or any(c not in COULEURS for c in etat):
        raise EtatImpossible("L'état doit compter 54 stickers, chacun d'une des six couleurs.")
    for code, nom in COULEURS.items():
        if etat.count(code) != 9:
            raise EtatImpossible(f"Il faut 9 stickers de chaque couleur : le {nom} en compte {etat.count(code)}.")
    centres = {_centre(etat, f) for f in FACES}
    if len(centres) != 6:
        raise EtatImpossible("Les six centres doivent être de six couleurs différentes.")
    attendues = {frozenset(_centre(etat, face_de(k)) for k in piece) for piece in ARETES + COINS}
    vues = [frozenset(etat[k] for k in piece) for piece in ARETES + COINS]
    for piece, couleurs in zip(ARETES + COINS, vues, strict=True):
        if couleurs not in attendues or len(couleurs) != len(piece):
            noms = ", ".join(COULEURS[etat[k]] for k in piece)
            raise EtatImpossible(f"Cette pièce n'existe pas sur un vrai cube : {noms}.")
    if len(set(vues)) != len(vues):
        raise EtatImpossible("Une même pièce apparaît deux fois : vérifiez les couleurs saisies.")


# --- Étapes de la méthode ---------------------------------------------------------

_MACROS_CROIX = _macros("F2", "R U R'", "L' U' L", "U L F' L'", "U' R' F R")
_MACROS_COINS = _macros("R U R'", *(" ".join(["R U R' U'"] * n) for n in range(1, 6)))
_MACROS_MILIEU = _macros("U R U' R' U' F' U F", "U' L' U L U F U' F'")
_MACROS_CROIX_HAUT = _macros("F R U R' U' F'", "F U R U' R' F'", tours_u=False)
_MACROS_ARETES_HAUT = _macros("R U R' U R U2 R'")
_AA = "R' F R' B2 R F' R' B2 R2"
_MACROS_COINS_HAUT = _macros(_AA, " ".join(moteur.inverse(moteur.lit_sequence(_AA))), tours_u=False)


def resous(etat):
    """Renvoie la liste des étapes : [{"titre", "explication", "mouvements"}], toutes non vides sauf si déjà résolu."""
    etat = "".join(etat)
    verifie(etat)
    etapes = []

    def ajoute(titre, explication, mouvements):
        nonlocal etat
        mouvements = moteur.simplifie(mouvements)
        if mouvements:
            etat = moteur.applique(etat, mouvements)
            etapes.append({"titre": titre, "explication": explication, "mouvements": mouvements})

    bas, haut = COULEURS[_centre(etat, "D")], COULEURS[_centre(etat, "U")]
    places = []  # pièces déjà placées, à ne plus déranger

    def garde(e):
        return all(_en_place(e, p) for p in places)

    # 1. La croix sur la face du dessous.
    for cote in COTES:
        piece = _piece_cible(etat, "D" + cote)
        but = lambda e, p=piece: _en_place(e, p) and garde(e)  # noqa: E731
        ajoute(
            f"Croix {bas}",
            f"Placer l'arête {_nom(etat, 'D' + cote)} sous le centre {COULEURS[_centre(etat, cote)]}, "
            f"le {bas} vers le bas. Si elle est déjà en bas mais mal placée, on la remonte d'abord.",
            _cherche(etat, _MACROS_CROIX, but, 3),
        )
        places.append(piece)

    # 2. Les coins de la première couronne.
    for cote in COTES:
        faces = "D" + cote + _droite(cote)
        piece = _piece_cible(etat, faces)
        but = lambda e, p=piece: _en_place(e, p) and garde(e)  # noqa: E731
        ajoute(
            f"Coins {bas}s",
            f"Amener le coin {_nom(etat, faces)} au-dessus de sa place, puis répéter R U R' U' "
            f"jusqu'à ce qu'il descende bien orienté.",
            _cherche(etat, _MACROS_COINS, but, 3),
        )
        places.append(piece)

    # 3. Les arêtes de la couronne du milieu.
    for cote in COTES:
        faces = cote + _droite(cote)
        piece = _piece_cible(etat, faces)
        but = lambda e, p=piece: _en_place(e, p) and garde(e)  # noqa: E731
        ajoute(
            "Deuxième couronne",
            f"Placer l'arête {_nom(etat, faces)} entre ses deux centres : on l'aligne sur le dessus, puis on "
            f"l'insère vers la droite (U R U' R' U' F' U F) ou vers la gauche (U' L' U L U F U' F').",
            _cherche(etat, _MACROS_MILIEU, but, 3),
        )
        places.append(piece)

    # 4. La croix du dessus (orientation des arêtes).
    aretes_haut = [_piece_cible(etat, "U" + c) for c in COTES]
    y = _centre(etat, "U")

    def croix_haut(e):
        return garde(e) and all(e[k] == y for p in aretes_haut for k in p if face_de(k) == "U")

    ajoute(
        f"Croix {haut}",
        f"Former une croix {haut} sur le dessus avec F R U R' U' F' (point → L → ligne → croix) "
        f"ou F U R U' R' F' (L → croix directement).",
        _cherche(etat, _MACROS_CROIX_HAUT, croix_haut, 3),
    )

    # 5. Les arêtes du dessus à leur place.
    def aretes_placees(e):
        return croix_haut(e) and all(_en_place(e, p) for p in aretes_haut)

    ajoute(
        f"Arêtes {haut}s",
        "Tourner le dessus et échanger deux arêtes voisines avec R U R' U R U2 R' jusqu'à ce que chaque "
        "arête soit sous le bon centre.",
        _cherche(etat, _MACROS_ARETES_HAUT, aretes_placees, 6),
    )
    places.extend(aretes_haut)

    # 6. Les coins du dessus à leur place (pas encore forcément bien tournés).
    coins_haut = [_piece_cible(etat, "U" + c + _droite(c)) for c in COTES]

    def coins_places(e):
        if not garde(e):
            return False
        for p in coins_haut:
            if sorted(e[k] for k in p) != sorted(_centre(e, face_de(k)) for k in p):
                return False
        return True

    ajoute(
        f"Coins {haut}s à leur place",
        "Permuter trois coins du dessus avec R' F R' B2 R F' R' B2 R2 (ou son inverse) jusqu'à ce que "
        "chaque coin soit à sa place, même mal tourné.",
        _cherche(etat, _MACROS_COINS_HAUT, coins_places, 2),
    )

    # 7. Tourner les coins du dessus : R' D' R D sur le coin avant droit, puis U pour passer au suivant.
    # La couronne du bas se dérange pendant l'étape et se remet en place à la fin. Les tours du dessus
    # sont reportés sur le coin suivant qui a besoin d'être tourné (rien à faire si tout est déjà bon).
    coin_avant_droit = _piece_cible(etat, "UFR")
    sticker_haut = next(k for k in coin_avant_droit if face_de(k) == "U")
    tours_en_attente = []
    for numero in range(1, 5):
        e = moteur.applique(etat, tours_en_attente)
        mouvements = []
        for _ in range(6):
            if e[sticker_haut] == y:
                break
            mouvements += moteur.lit_sequence("R' D' R D")
            e = moteur.applique(e, "R' D' R D")
        if mouvements:
            ajoute(
                f"Orientation des coins {haut}s",
                f"Coin {numero} sur 4, amené devant à droite en tournant le dessus : répéter R' D' R D jusqu'à "
                f"ce que son {haut} soit sur le dessus. Le bas se dérange : il se remettra en place tout seul.",
                tours_en_attente + mouvements,
            )
            tours_en_attente = []
        tours_en_attente.append("U")
    ajoute(f"Orientation des coins {haut}s", "Dernier réglage : tourner le dessus pour aligner les couleurs.", tours_en_attente)
    if not moteur.est_resolu(etat):
        raise EtatImpossible(
            "Ce cube ne peut pas être résolu : un coin a sans doute été saisi tourné. "
            "Vérifiez les couleurs des coins."
        )
    return etapes


def solution(etat):
    """Étapes et liste complète des mouvements."""
    etapes = resous(etat)
    return {"etapes": etapes, "mouvements": [m for e in etapes for m in e["mouvements"]]}
