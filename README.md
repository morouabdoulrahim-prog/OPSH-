# Projet OPSH — Mini-Shell en Python

Interpréteur de commandes (mini-shell) développé en Python sous Ubuntu dans le cadre du module **Systèmes d'Exploitation (UIR/ESIN)**.

## Membres du groupe
* **Rahim** : Commandes internes (builtins), table des alias, redirections et historique (`code/rahim.py`).
* **Aaron** : Boucle REPL, parsing, variables d'environnement, substitution et mode script (`code/aaron.py`).
* **Farid** : Exécution système (`fork`/`execvp`/`waitpid`), pipes `->`, arrière-plan `&` et gestion des signaux (`code/farid.py`).

## Lancement du projet

### Mode interactif
```bash
python3 code/aaron.py
```

### Mode script
```bash
python3 code/aaron.py script.opsh
```

## Commandes supportées

### Builtins (Commandes internes)
* `go <dossier>` : Change le répertoire courant (équivalent de `cd`).
* `quit` : Quitte le shell `opsh` (équivalent de `exit`).
* `say <texte>` : Affiche un message à l'écran (équivalent de `echo`).
* `info` : Affiche l'aide et la liste des commandes disponibles (équivalent de `help`).
* `past` : Affiche l'historique des commandes exécutées (équivalent de `history`).
* `osinfo` : Affiche `Systèmes d’Exploitation –- UIR/ESIN`.
* `export VAR=VALEUR` : Définit une variable d'environnement.

### Alias (Commandes renommées)

| Commande `opsh` | Équivalent Bash | Description |
| :--- | :--- | :--- |
| `list` | `ls` | Liste les fichiers du répertoire |
| `path` | `pwd` | Affiche le chemin du répertoire courant |
| `show` | `cat` | Affiche le contenu d'un fichier |
| `copy` | `cp` | Copie un fichier ou un dossier |
| `move` | `mv` | Déplace ou renomme un fichier |
| `del` | `rm` | Supprime un fichier |
| `newdir` | `mkdir` | Crée un nouveau dossier |
| `newfile` | `touch` | Crée un nouveau fichier vide |

## Fonctionnalités avancées
* **Redirections :** `<` (entrée), `>` (sortie avec écrasement), `>>` (sortie en ajout).
* **Pipes personnalisés :** Utilisation de `->` à la place de `|` (ex: `show f.txt -> wc -l`).
* **Arrière-plan et signaux :** Support de `&`, nettoyage automatique des processus zombies via `SIGCHLD`, et protection contre `Ctrl+C` (`SIGINT`).
* **Variables et substitution :** Expansion de `$VAR`, `${VAR}`, `$?`, `$!`, substitution `$(...)` et chargement automatique de `~/.opshrc`.
