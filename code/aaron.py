import os
import re
import sys
import shlex
import subprocess
import rahim
import farid

def substituer_commandes(ligne):
    """Remplace $(commande) et `commande` par leur sortie (Jalon 5)."""
    def executer_capture(match):
        cmd_interne = match.group(1)
        mots = shlex.split(cmd_interne)
        mots = rahim.appliquer_alias(mots)
        try:
            res = subprocess.check_output(mots, stderr=subprocess.DEVNULL, text=True)
            return res.strip().replace("\n", " ")
        except Exception:
            return ""

    ligne = re.sub(r"\$\(([^)]+)\)", executer_capture, ligne)
    ligne = re.sub(r"`([^`]+)`", executer_capture, ligne)
    return ligne

def etendre_variables(ligne):
    """Remplace $?, $!, ${VAR} et $VAR par leurs valeurs (Jalon 4)."""
    ligne = ligne.replace("$?", str(farid.dernier_statut))
    ligne = ligne.replace("$!", str(farid.dernier_pid))

    ligne = re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: os.environ.get(m.group(1), ""),
        ligne
    )
    ligne = re.sub(
        r"\$([A-Za-z_][A-Za-z0-9_]*)",
        lambda m: os.environ.get(m.group(1), ""),
        ligne
    )
    return ligne

def executer_ligne(ligne):
    """Traite et exécute une seule ligne de commande."""
    ligne = ligne.strip()
    if not ligne or ligne.startswith("#"):
        return

    ligne = substituer_commandes(ligne)
    ligne = etendre_variables(ligne)

    if "->" in ligne:
        farid.executer_pipe(ligne)
        return

    tokens = shlex.split(ligne)
    tokens = rahim.appliquer_alias(tokens)
    tokens, redir_in, redir_out, mode_append = rahim.extraire_redirections(tokens)
    if not tokens:
        return

    if rahim.est_builtin(tokens):
        rahim.executer_builtin(tokens, redir_out, mode_append)
    else:
        farid.executer_externe(tokens, redir_in, redir_out, mode_append)

def executer_bloc_lignes(lignes):
    """Exécute une liste de lignes avec support basique de if, for et while (Jalon 6)."""
    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()
        if not ligne or ligne.startswith("#"):
            i += 1
            continue

        # --- Structure FOR : for VAR in val1 val2 ; do ... done ---
        if ligne.startswith("for "):
            entete = ligne.split(";")[0].strip()
            parties = entete.split()
            nom_var = parties[1]
            valeurs = parties[3:] if len(parties) > 3 else []

            bloc = []
            i += 1
            while i < len(lignes) and lignes[i].strip() != "done":
                if lignes[i].strip() != "do":
                    bloc.append(lignes[i])
                i += 1

            for val in valeurs:
                os.environ[nom_var] = val
                executer_bloc_lignes(bloc)
            i += 1

        # --- Structure IF : if commande ; then ... else ... fi ---
        elif ligne.startswith("if "):
            condition = ligne[3:].split(";")[0].strip()
            bloc_then = []
            bloc_else = []
            dans_else = False
            i += 1
            while i < len(lignes) and lignes[i].strip() != "fi":
                actuelle = lignes[i].strip()
                if actuelle == "then":
                    pass
                elif actuelle == "else":
                    dans_else = True
                else:
                    if dans_else:
                        bloc_else.append(lignes[i])
                    else:
                        bloc_then.append(lignes[i])
                i += 1

            executer_ligne(condition)
            if farid.dernier_statut == 0:
                executer_bloc_lignes(bloc_then)
            else:
                executer_bloc_lignes(bloc_else)
            i += 1

        # --- Structure WHILE : while commande ; do ... done ---
        elif ligne.startswith("while "):
            condition = ligne[6:].split(";")[0].strip()
            bloc = []
            i += 1
            while i < len(lignes) and lignes[i].strip() != "done":
                if lignes[i].strip() != "do":
                    bloc.append(lignes[i])
                i += 1

            while True:
                executer_ligne(condition)
                if farid.dernier_statut != 0:
                    break
                executer_bloc_lignes(bloc)
            i += 1

        else:
            executer_ligne(ligne)
            i += 1

def charger_opshrc():
    """Charge automatiquement ~/.opshrc au démarrage s'il existe (Jalon 5)."""
    chemin_rc = os.path.expanduser("~/.opshrc")
    if os.path.isfile(chemin_rc):
        with open(chemin_rc, "r", encoding="utf-8") as f:
            executer_bloc_lignes(f.readlines())

def main():
    rahim.configurer_autocompletion()
    charger_opshrc()

    # Mode Script (Jalon 6) : python3 code/aaron.py mon_script.opsh
    if len(sys.argv) > 1:
        fichier_script = sys.argv[1]
        if not os.path.isfile(fichier_script):
            print(f"opsh: fichier script introuvable : {fichier_script}")
            sys.exit(1)
        with open(fichier_script, "r", encoding="utf-8") as f:
            executer_bloc_lignes(f.readlines())
        sys.exit(farid.dernier_statut)

    # Mode Interactif (REPL)
    while True:
        try:
            ligne = input("opsh> ").strip()
            if not ligne:
                continue
            rahim.ajouter_historique(ligne)
            executer_ligne(ligne)

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print("\nFermeture de opsh.")
            break
        except Exception as e:
            print(f"Erreur opsh : {e}")

if __name__ == "__main__":
    main()
