
# INF8808-Projet

Ce projet est une application interactive développée avec Dash pour analyser les données de films. Elle permet de visualiser des graphiques interactifs basés sur des métriques telles que le budget, le revenu, la popularité, et bien plus encore.

---
## **Comment démarrer le projet**



### 1. **Installer les dépendances**

Assurez-vous d'avoir Python installé sur votre machine. Installez les dépendances nécessaires en exécutant la commande suivante dans le terminal :



```bash

pip install -r requirements.txt

```



### 2. **Prétraiter les données**

Le fichier `preprocess.py` est utilisé pour combiner les deux fichiers de base IMDb (`tmdb_5000_movies.csv` et `tmdb_5000_credits.csv`) en un seul fichier exploitable.



#### Étapes :

1. Placez les fichiers suivants dans le dossier `data` :

   - `tmdb_5000_movies.csv`

   - `tmdb_5000_credits.csv`

2. Exécutez le script `preprocess.py` :

   ```bash

   python preprocess.py

   ```

   Le fichier combiné sera généré sous le nom `combined.csv` dans le dossier `data`.



### 3. **Lancer le serveur**

Pour démarrer l'application Dash, exécutez le fichier `server.py` :

```bash

python server.py

```



Le serveur sera exposé sur le port 80. Vous pouvez accéder à l'application via l'URL suivante dans votre navigateur :

[http://localhost](http://localhost)





## **Structure du projet**

Voici une description des principaux fichiers et dossiers du projet :



### **Fichiers principaux**

- `server.py` : Point d'entrée principal pour démarrer le serveur Dash.

- `preprocess.py` : Script pour combiner les fichiers de données IMDb en un seul fichier exploitable.

- `requirements.txt` : Liste des bibliothèques Python nécessaires pour exécuter le projet.

- `runtime.txt` : Spécifie la version de Python utilisée pour le projet.



### **Dossiers**

- `code/components` : Contient les différents modules Dash pour les graphiques et visualisations.

  - `countries_chart` : Analyse des données par pays.

  - `entities_chart` : Analyse des acteurs, réalisateurs et studios.

  - `heatmap_budget` : Visualisation des heatmaps pour le budget et d'autres métriques.

  - `matrix_diagram` : Analyse des corrélations entre différentes métriques.

- `data` : Contient les fichiers de données bruts et le fichier combiné généré (`combined.csv`).





## **Dépendances**

Les dépendances nécessaires sont listées dans le fichier `requirements.txt`. Voici les principales bibliothèques utilisées :



- **Dash** : Framework pour créer des applications web interactives.

- **Pandas** : Manipulation et analyse des données.

- **Plotly** : Création de graphiques interactifs.



Installez-les avec la commande suivante :

```bash

pip install -r requirements.txt

```





## **Détails supplémentaires**

- **Version de Python** : La version de Python utilisée pour ce projet est spécifiée dans le fichier `runtime.txt`. Assurez-vous d'utiliser cette version pour éviter les incompatibilités.

- **Structure modulaire** : Chaque composant de l'application est organisé dans des modules séparés pour une meilleure maintenabilité.

- **Données** : Les données utilisées proviennent des fichiers IMDb (`tmdb_5000_movies.csv` et `tmdb_5000_credits.csv`).
