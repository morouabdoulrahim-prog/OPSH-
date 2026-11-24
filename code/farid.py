import os
import signal
import shlex
import rahim

# Variables globales pour le Jalon 4 ($? et $!)
dernier_statut = 0
dernier_pid = 0

def nettoyer_zombies(signum, frame):
    """Nettoie les processus enfants terminés en arrière-plan (évite les zombies)."""
    try:
        while True:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid <= 0:
                break
    except ChildProcessError:
        pass

signal.signal(signal.SIGCHLD, nettoyer_zombies)

def executer_externe(tokens, redir_in=None, redir_out=None, mode_append=False):
    """Exécute une commande externe avec fork/execvp, redirections, & et mise à jour de $? et $!."""
    global dernier_statut, dernier_pid

    en_arriere_plan = False
    if tokens and tokens[-1] == "&":
        en_arriere_plan = True
        tokens = tokens[:-1]

    if not tokens:
        return

    pid = os.fork()

    if pid == 0:
        # --- PROCESSUS ENFANT ---
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
            if redir_in:
                fd_in = os.open(redir_in, os.O_RDONLY)
                os.dup2(fd_in, 0)
                os.close(fd_in)

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
            dernier_pid = pid
            print(f"[Arrière-plan] PID : {pid}")
        else:
            _, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status):
                dernier_statut = os.WEXITSTATUS(status)

def executer_pipe(ligne):
    """Gère le pipe personnalisé '->' entre deux ou plusieurs commandes."""
    global dernier_statut

    parties = [p.strip() for p in ligne.split("->")]
    if len(parties) < 2 or any(not p for p in parties):
        print("opsh: syntaxe de pipe invalide (utilisez cmd1 -> cmd2)")
        dernier_statut = 1
        return

    nb_cmds = len(parties)
    pipes = [os.pipe() for _ in range(nb_cmds - 1)]
    pids = []

    for i, partie in enumerate(parties):
        tokens = rahim.appliquer_alias(shlex.split(partie))
        tokens, redir_in, redir_out, mode_append = rahim.extraire_redirections(tokens)

        pid = os.fork()
        if pid == 0:
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            if i > 0:
                os.dup2(pipes[i - 1][0], 0)
            elif redir_in:
                fd_in = os.open(redir_in, os.O_RDONLY)
                os.dup2(fd_in, 0)
                os.close(fd_in)

            if i < nb_cmds - 1:
                os.dup2(pipes[i][1], 1)
            elif redir_out:
                flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if mode_append else os.O_TRUNC)
                fd_out = os.open(redir_out, flags, 0o644)
                os.dup2(fd_out, 1)
                os.close(fd_out)

            for r, w in pipes:
                os.close(r)
                os.close(w)

            try:
                os.execvp(tokens[0], tokens)
            except Exception as e:
                print(f"opsh: erreur pipe : {e}")
                os._exit(127)
        else:
            pids.append(pid)

    for r, w in pipes:
        os.close(r)
        os.close(w)

    for idx, pid in enumerate(pids):
        _, status = os.waitpid(pid, 0)
        if idx == len(pids) - 1 and os.WIFEXITED(status):
            dernier_statut = os.WEXITSTATUS(status)
