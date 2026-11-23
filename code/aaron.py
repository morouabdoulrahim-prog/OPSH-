import sys
import shlex
import rahim
import farid

def main():
    while True:
        try:
            # 1. Afficher le prompt opsh> et lire la commande
            ligne = input("opsh> ").strip()
            if not ligne:
                continue

            # 2. Vérifier si la commande contient un pipe (->)
            if "->" in ligne:
                farid.executer_pipe(ligne)
                continue

            # 3. Découper la ligne en mots (gère aussi les guillemets)
            tokens = shlex.split(ligne)

            # 4. Appliquer les alias de Rahim (ex: list -> ls, show -> cat)
            tokens = rahim.appliquer_alias(tokens)

            # 5. Vérifier s'il y a des redirections (>, >>, <)
            tokens, redir_in, redir_out, mode_append = rahim.extraire_redirections(tokens)
            if not tokens:
                continue

            # 6. Vérifier si c'est une commande interne (builtin) de Rahim
            if rahim.est_builtin(tokens[0]):
                rahim.executer_builtin(tokens, redir_out, mode_append)
            else:
                # 7. Sinon, Farid exécute la commande système (avec fork/exec ou &)
                farid.executer_externe(tokens, redir_in, redir_out, mode_append)

        except KeyboardInterrupt:
            # Ctrl+C ne ferme pas le shell opsh, il passe juste à la ligne
            print()
            continue
        except EOFError:
            # Ctrl+D quitte proprement le shell
            print("\nFermeture de opsh.")
            break
        except Exception as e:
            print(f"Erreur opsh : {e}")

if __name__ == "__main__":
    main()