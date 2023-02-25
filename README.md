# AlphaZor0

AlphaZor0 est un bot discord pouvant jouer aux échecs en utilisant l'algorithme minimax et élagage alpha-bêta.


# Installation


## Librairies
Vous devez avoir installé python3 ainsi que plusieurs librairies importantes:
 `chess.py` `discord.py` `fentoboardimage`
https://python-chess.readthedocs.io/
https://discordpy.readthedocs.io/
https://pypi.org/project/fentoboardimage/

## Bot Discord

Il vous faudra avoir un bot discord et remplacer dans le fichier `constant.py`le token associé à votre bot.
Il faudra également l'ajouter à votre serveur en lui attribuant la permission de lire les messages.

## Personnalisation
Il est possible de personnaliser le plateau ainsi que les pièces en modifiant simplement les images du dossier `img` et `pieces`.

<p align="center"> <img height="300" src="/image presentation/custom.png"> </p>

## Utilisation

Exécuter le fichier `chessbot.py`.
Pour initialiser une partie du côté blanc: envoyer le message `zchess start w`.
Pour le côté des noirs: `zchess start b`.
Pour jouer, simplement envoyer un message de 4 caractères contenant les coordonnées du plateau (standard UCI).


# Présentation
<p align="center"> <img height="300" src="/image presentation/zchess start w.png"> <img height="300" src="/image presentation/zchess start b.png"> </p> 


# Fonctionnement


## Notation FEN

On utilise la notation FEN (https://fr.wikipedia.org/wiki/Notation_Forsyth-Edwards) pour représenter le plateau.

## Poids des pièces
Pour trouver le coup optimal à jouer pour le bot, on associe à chaque pièce du plateau un poids (valeur)

|Roi |Dame |Tour | Fou| Cavalier |Pion |
|---|---|---|---|---|---|
| 900| 90| 50| 30|30| 10|


## Algorithme MiniMax

<p align="center"> <img height="300" src="/image presentation/minimax.png"> </p>

L'algorithme fonctionne par récursivité, on explore tous les coups possibles à une profondeur donnée `n` on associe au plateau final une valeur calculée avec le poids des pièces puis de proche en proche on prend le maximum et le minimum afin de rechercher le meilleur coup.

## Élagage alpha-bêta
Comme calculer tous les coups possibles pour une profondeur donnée `n` assez grande de l'ordre de 5 est coûteux on pratique l'élagage alpha-bêta.
On coupe des branches dont on est sûr qu'elles ne dépasseront pas le maximum ou le minimum (les branches non pertinentes) à l'aide de 2 valeurs temporaires: `alpha` et `beta`.

        fonction alphabeta(nœud, α, β) /* α est toujours inférieur à β */
       si nœud est une feuille alors
           retourner la valeur de nœud
      sinon
                si nœud est de type Min alors
                           v = +∞
                           pour tout fils de nœud faire
                               v = min(v, alphabeta(fils, α, β))                
                               si α ≥ v alors /* coupure alpha */
                                 retourner v
                               β = min(β, v)           
                 sinon
                           v = -∞
                           pour tout fils de nœud faire
                               v = max(v, alphabeta(fils, α, β))                
                               si v ≥ β alors /* coupure beta */
                                  retourner v
                               α = max(α, v)
        retourner v



## Améliorations possibles

 - On peut changer le poids des pièces selon leur position sur le plateau 

<p align="center"> <img height="300" src="/image presentation/valeur fct plateau.png"> </p>

 - Faire jouer 2 joueurs ensemble
 - Machine learning (ajouter une base de données des ouvertures fréquemment jouées) 
  - Consulter le lien: https://levelup.gitconnected.com/improving-minimax-performance-fc82bc337dfd
  
# Codingame

À l'origine, le but de ce projet était de participer aux combats de bots sur le site https://www.codingame.com/ 
On peut retrouver le code `maincoding.py` qui vous permettra de remporter plusieurs parties sur le site, il a le défaut d'être plus lent que le bot discord car il utilise une représentation du plateau avec des matrices du fait de la non possibilité d'utiliser la librairie `chess.py`.
