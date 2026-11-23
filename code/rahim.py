import os
import sys

# Table des alias imposée par le sujet
ALIAS = {
    "list": "ls",
    "path": "pwd",
    "show": "cat",
    "copy": "cp",
    "move": "mv",
    "del": "rm",
    "newdir": "mkdir",
    "newfile": "touch"
}

BUILTINS = ["go", "quit", "say", "info", "past", "osinfo"]

def appliquer_alias(tokens):
    """Remplace le premier mot s'il fait partie des alias."""
    if tokens and tokens[0] in ALIAS:
        tokens[0] = ALIAS[tokens[0]]
    return tokens

def extraire_redirections(tokens):
    """Sépare la commande des symboles <, > et >>."""
    redir_in = None
    redir_out = None
    mode_append = False
    cmd_propre = []

    i = 0
    while i < len(tokens):
        if tokens[i] == "<" and i + 1 < len(tokens):
            redir_in = tokens[i + 1]
            i += 2
        elif tokens[i] == ">" and i + 1 < len(tokens):
            redir_out = tokens[i + 1]
            mode_append = False
            i += 2
        elif tokens[i] == ">>" and i + 1 < len(tokens):
            redir_out = tokens[i + 1]
            mode_append = True
            i += 2
        else:
            cmd_propre.append(tokens[i])
            i += 1

    return cmd_propre, redir_in, redir_out, mode_append

def est_builtin(commande):
    return commande in BUILTINS

def executer_builtin(tokens, redir_out=None, mode_append=False):
    """Exécute les commandes internes de opsh."""
    cmd = tokens[0]
    args = tokens[1:]

    # Gestion de la redirection de sortie pour les builtins (ex: say hello > f.txt)
    ancien_stdout = sys.stdout
    fichier_sortie = None
    if redir_out:
        mode = "a" if mode_append else "w"
        fichier_sortie = open(redir_out, mode)
        sys.stdout = fichier_sortie

    try:
        if cmd == "go":
            # cd doit être un builtin car un processus enfant ne peut pas changer le dossier du parent
            cible = args[0] if args else os.path.expanduser("~")
            os.chdir(cible)

        elif cmd == "quit":
            sys.exit(0)

        elif cmd == "say":
            print(" ".join(args))

        elif cmd == "osinfo":
            print("Systèmes d’Exploitation –- UIR/ESIN")

        elif cmd == "info":
            print("Builtins disponibles : go, quit, say, info, past, osinfo")
            print("Alias disponibles : list, path, show, copy, move, del, newdir, newfile")

        elif cmd == "past":
            print("Historique à implémenter ici (Jalon 5)")

    finally:
        if fichier_sortie:
            sys.stdout = ancien_stdout
            fichier_sortie.close()
