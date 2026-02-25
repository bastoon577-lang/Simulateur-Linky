# SimuLinky
Cet outils rudimentaire permet de simuler le compteur Linky sur le port COM et ainsi effectuer des tests rapide avec le [Module TIC](https://github.com/bastoon577-lang/Module-TIC-SOFTWARE) compatible avec son PCB de flashage.

# Comment utiliser le script ?
Son utilisation passe par son lancement en Python.
Celui-ci demande ensuite:
 1. Le port COM utilisé.
 2. Le type de compteur à simuler.

Puis lors de son exécusion en continue, de permettre de modifier: 
 1. Le courant IINST (en monophasé) ou IINST1, IINST2, IINST3 (en triphasé).
 2. L'heure courante HP.. (Heure pleine) ou HC.. (Heure creuse).

