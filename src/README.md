# Project Structure
## lsp
Contient l'implementation du Language Server.
Ce module est appele depuis les extensions d'editeur definies dans *extensions*.

* *server.py* contient l'implementation du server, ainsi que le lien vers le Reference Server.
* *__main__.py* contient le script de lancement du server.
* *tests/* contient les tests (en vrai l'ensemble des tests sont fait depuis les extensions, mais on ne sait jamais).

## bdd
Contient l'implementation du Reference Server (marque deposee).
En gros c'est ici que l'on manipule les projets, que l'on reference (variables, fonctions, classes, imports, dependences...) et que l'on les enregistre dans une BDD. C'est l'implementation de l'ORM.

* Les fichiers commencant par une majuscule definisse une table dans la BDD, ils contiennent egalement des Manager (Singleton) qui permmettent la gestion des dites tables.
* *bdd.py* permet d'initialiser l'ORM (on pourra ajouter un fichier de config plus tard).

## daemon

Une premiere idee de comment fonctionnerait le systeme d'autocompletion AVANT d'utiliser le LSP.

## parser

Une boite a outils (a renommer)
