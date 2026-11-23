import os
import signal
import shlex
import rahim

# Gestionnaire pour nettoyer les processus zombies en arrière-plan
def nettoyer_zombies(signum, frame):
    try:
        while True:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid <= 0:
                break
    except ChildProcessError:
        pass

signal.signal(signal.SIGCHLD, nettoyer_zombies)

def executer_externe(tokens, redir_in=None, redir_out=None, mode_append=False):
    """Exécute une commande externe avec fork/execvp, redirections et &."""
    en_arriere_plan = False
    if tokens[-1] == "&":
        en_arriere_plan = True
        tokens = tokens[:-1]

    pid = os.fork()

    if pid == 0:
        # --- PROCESSUS ENFANT ---
        # Rétablir Ctrl+C par défaut pour l'enfant
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
            # Redirection entrée (<)
            if redir_in:
                fd_in = os.open(redir_in, os.O_RDONLY)
                os.dup2(fd_in, 0)
                os.close(fd_in)

            # Redirection sortie (> ou >>)
            if redir_out:
                flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if mode_append else os.O_TRUNC)
                fd_out = os.open(redir_out, flags, 0o644)
                os.dup2(fd_out, 1)
                os.close(fd_out)

            os.execvp(tokens[0], tokens)
        except FileNotFoundError:
            print(f"opsh: commande introuvable : {tokens[0]}")
            os._exit(127)
        except Exception as e:
            print(f"opsh: erreur d'exécution : {e}")
            os._exit(1)
    else:
        # --- PROCESSUS PARENT (opsh) ---
        if en_arriere_plan:
            print(f"[Arrière-plan] PID : {pid}")
        else:
            os.waitpid(pid, 0)

def executer_pipe(ligne):
    """Gère le pipe personnalisé '->' entre deux commandes (ex: show f.txt -> wc -l)."""
    parties = [p.strip() for p in ligne.split("->")]
    if len(parties) != 2:
        print("opsh: syntaxe de pipe invalide (utilisez cmd1 -> cmd2)")
        return

    cmd1 = rahim.appliquer_alias(shlex.split(parties[0]))
    cmd2 = rahim.appliquer_alias(shlex.split(parties[1]))

    r, w = os.pipe()

    pid1 = os.fork()
    if pid1 == 0:
        # Enfant 1 : écrit dans le pipe (stdout -> w)
        os.dup2(w, 1)
        os.close(r)
        os.close(w)
        os.execvp(cmd1[0], cmd1)

    pid2 = os.fork()
    if pid2 == 0:
        # Enfant 2 : lit depuis le pipe (stdin -> r)
        os.dup2(r, 0)
        os.close(r)
        os.close(w)
        os.execvp(cmd2[0], cmd2)

    # Parent : ferme les deux bouts du pipe et attend les enfants
    os.close(r)
    os.close(w)
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)
