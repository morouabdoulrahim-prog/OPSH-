import os
import sys
import readline
import farid

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

BUILTINS = ["go", "quit", "say", "info", "past", "osinfo", "export"]
HISTORIQUE = []

def configurer_autocompletion():
    """Active la complétion automatique avec la touche Tab (Jalon 5)."""
    def completer(texte, etat):
        options = BUILTINS + list(ALIAS.keys()) + os.listdir(".")
        correspondances = [opt for opt in options if opt.startswith(texte)]
        return correspondances[etat] if etat < len(correspondances) else None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

def ajouter_historique(ligne):
    """Enregistre chaque commande tapée pour le builtin 'past'."""
    if ligne.strip():
        HISTORIQUE.append(ligne.strip())

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

def est_builtin(tokens):
    return len(tokens) > 0 and tokens[0] in BUILTINS

def executer_builtin(tokens, redir_out=None, mode_append=False):
    """Exécute les commandes internes de opsh."""
    cmd = tokens[0]
    args = tokens[1:]

    ancien_stdout = sys.stdout
    fichier_sortie = None
    if redir_out:
        mode = "a" if mode_append else "w"
        fichier_sortie = open(redir_out, mode)
        sys.stdout = fichier_sortie

    try:
        if cmd == "go":
            # cd doit être un builtin car un enfant ne peut pas changer le dossier du parent
            cible = args[0] if args else os.path.expanduser("~")
            os.chdir(cible)
            farid.dernier_statut = 0

        elif cmd == "quit":
            sys.exit(0)

        elif cmd == "say":
            print(" ".join(args))
            farid.dernier_statut = 0

        elif cmd == "osinfo":
            print("Systèmes d’Exploitation –- UIR/ESIN")
            farid.dernier_statut = 0

        elif cmd == "export":
            if not args:
                for cle, val in os.environ.items():
                    print(f"{cle}={val}")
            else:
                for arg in args:
                    if "=" in arg:
                        cle, val = arg.split("=", 1)
                        os.environ[cle] = val
                    else:
                        print("opsh: syntaxe export invalide (utilisez export VAR=VALEUR)")
                        farid.dernier_statut = 1
                        return
            farid.dernier_statut = 0

        elif cmd == "past":
            for index, entree in enumerate(HISTORIQUE, start=1):
                print(f"{index}  {entree}")
            farid.dernier_statut = 0

        elif cmd == "info":
            print("Builtins : go, quit, say, info, past, osinfo, export")
            print("Alias    : list (ls), path (pwd), show (cat), copy (cp), move (mv), del (rm), newdir (mkdir), newfile (touch)")
            farid.dernier_statut = 0

    except Exception as e:
        print(f"opsh: erreur {cmd} : {e}")
        farid.dernier_statut = 1

    finally:
        if fichier_sortie:
            sys.stdout = ancien_stdout
            fichier_sortie.close()
