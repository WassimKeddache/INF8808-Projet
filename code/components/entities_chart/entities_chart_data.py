import pandas as pd
import json
import re


class EntitiesChartData:
    def __init__(self):
        df = pd.read_csv("../data/combined.csv")
        self.preprocess_data(df)
            
    def aggregate_data(self, entity_df):
        """Agrège les données par entité et calcule les métriques moyennes"""
        for col in ["revenue", "vote_average", "popularity"]:
            entity_df[col] = pd.to_numeric(entity_df[col], errors="coerce")

        agg_df = (
            entity_df.groupby(["entity_id", "entity_name"])
            .agg(
                {
                    "revenue": "mean",
                    "vote_average": "mean",
                    "popularity": "mean",
                    "title": "count",
                }
            )
            .reset_index()
        )

        agg_df.rename(
            columns={
                "revenue": "avg_revenue",
                "vote_average": "avg_rating",
                "popularity": "avg_popularity",
                "title": "film_count",
            },
            inplace=True,
        )

        return agg_df

    def clean_json_string(self, json_str):
        """Nettoie une chaîne JSON potentiellement malformée"""
        if pd.isna(json_str):
            return "[]"

        json_str = json_str.replace('""', '"')

        if not json_str.startswith("["):
            json_str = "[" + json_str
        if not json_str.endswith("]"):
            json_str = json_str + "]"

        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            return "[]"
    
    def extract_cast(self, cast_json):
        """Extrait les 5 premiers acteurs du JSON de casting avec gestion d'erreurs améliorée"""
        try:
            if pd.isna(cast_json):
                return []

            # Utiliser une approche par expression régulière pour extraire les informations
            # Cette méthode est plus robuste face aux JSON malformés
            actors = []

            cleaned_json = self.clean_json_string(cast_json)

            try:
                # Essayer de parser le JSON nettoyé
                cast_list = json.loads(cleaned_json)

                # Extraire les informations des acteurs (seulement les 5 premiers)
                for i, actor in enumerate(cast_list):
                    if i >= 5:  # Limiter à 5 acteurs par film
                        break
                    if isinstance(actor, dict) and "name" in actor and "id" in actor:
                        actors.append({"id": actor.get("id"), "name": actor.get("name")})

                return actors
            except json.JSONDecodeError:
                # Si le parsing échoue malgré le nettoyage, utiliser regex
                # Rechercher les motifs de nom et d'ID dans la chaîne
                name_pattern = r'"name":\s*"([^"]+)"'
                id_pattern = r'"id":\s*(\d+)'

                names = re.findall(name_pattern, cast_json)
                ids = re.findall(id_pattern, cast_json)

                # Associer les noms et les IDs si possible (seulement les 5 premiers)
                for i in range(min(len(names), len(ids), 5)):  # Limiter à 5 acteurs
                    actors.append({"id": int(ids[i]), "name": names[i]})

                return actors
        except Exception as e:
            return []
    
    def extract_directors(self, crew_json):
        """Extrait les réalisateurs du JSON d'équipe avec gestion d'erreurs améliorée"""
        try:
            if pd.isna(crew_json):
                return []

            cleaned_json = self.clean_json_string(crew_json)

            try:
                crew_list = json.loads(cleaned_json)

                directors = [
                    {"id": member.get("id"), "name": member.get("name")}
                    for member in crew_list
                    if isinstance(member, dict)
                    and member.get("job") == "Director"
                    and "name" in member
                    and "id" in member
                ]

                return directors
            except json.JSONDecodeError:

                director_pattern = (
                    r'"job":\s*"Director"[^}]*"name":\s*"([^"]+)"[^}]*"id":\s*(\d+)'
                )
                directors_matches = re.findall(director_pattern, crew_json)

                directors = []
                for name, id_str in directors_matches:
                    directors.append({"id": int(id_str), "name": name})

                return directors
        except Exception as e:
            return []


    def extract_studios(self, companies_json):
        """Extrait les studios du JSON de compagnies avec gestion d'erreurs améliorée"""
        try:
            if pd.isna(companies_json):
                return []

            cleaned_json = self.clean_json_string(companies_json)

            try:
                companies_list = json.loads(cleaned_json)

                studios = [
                    {"id": company.get("id"), "name": company.get("name")}
                    for company in companies_list
                    if isinstance(company, dict) and "name" in company and "id" in company
                ]

                return studios
            except json.JSONDecodeError:
                studio_pattern = r'"name":\s*"([^"]+)"[^}]*"id":\s*(\d+)'
                studio_matches = re.findall(studio_pattern, companies_json)

                studios = []
                for name, id_str in studio_matches:
                    studios.append({"id": int(id_str), "name": name})

                return studios
        except Exception as e:
            return []
    
    def preprocess_data(self, df):
        """
        Prétraite les données pour extraire et agréger les informations sur les acteurs, réalisateurs et studios.
        """
        min_films = 10

        # Convertir les colonnes numériques et vérifier les valeurs aberrantes
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
        df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
        df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")

        # Correction des valeurs aberrantes pour les revenus (si nécessaire)
        # Si les revenus sont en centimes au lieu de dollars, diviser par 100
        if df["revenue"].max() > 10_000_000_000:  # Si le max est supérieur à 10 milliards
            print("Correction des valeurs de revenus (conversion en dollars)...")
            df["revenue"] = df["revenue"] / 100
            print(f"Nouvelle valeur maximale de revenue: {df['revenue'].max()}")
            print(f"Nouvelle valeur moyenne de revenue: {df['revenue'].mean()}")

        # Application des fonctions d'extraction avec gestion d'erreurs
        df["cast_list"] = df["cast"].apply(self.extract_cast)
        df["directors_list"] = df["crew"].apply(self.extract_directors)
        df["studios_list"] = df["production_companies"].apply(self.extract_studios)

        # Explode des données pour avoir une ligne par acteur/réalisateur/studio
        actors_df = df.explode("cast_list")
        actors_df = actors_df[actors_df["cast_list"].notna()]
        actors_df["entity_id"] = actors_df["cast_list"].apply(
            lambda x: x.get("id") if isinstance(x, dict) else None
        )
        actors_df["entity_name"] = actors_df["cast_list"].apply(
            lambda x: x.get("name") if isinstance(x, dict) else None
        )
        actors_df = actors_df[actors_df["entity_name"].notna()]

        directors_df = df.explode("directors_list")
        directors_df = directors_df[directors_df["directors_list"].notna()]
        directors_df["entity_id"] = directors_df["directors_list"].apply(
            lambda x: x.get("id") if isinstance(x, dict) else None
        )
        directors_df["entity_name"] = directors_df["directors_list"].apply(
            lambda x: x.get("name") if isinstance(x, dict) else None
        )
        directors_df = directors_df[directors_df["entity_name"].notna()]

        studios_df = df.explode("studios_list")
        studios_df = studios_df[studios_df["studios_list"].notna()]
        studios_df["entity_id"] = studios_df["studios_list"].apply(
            lambda x: x.get("id") if isinstance(x, dict) else None
        )
        studios_df["entity_name"] = studios_df["studios_list"].apply(
            lambda x: x.get("name") if isinstance(x, dict) else None
        )
        studios_df = studios_df[studios_df["entity_name"].notna()]

        actors_agg = self.aggregate_data(actors_df)
        directors_agg = self.aggregate_data(directors_df)
        studios_agg = self.aggregate_data(studios_df)

        # Filtrer pour ne garder que les entités ayant participé à au moins 10 films
        
        actors_agg = actors_agg[actors_agg["film_count"] >= min_films]
        directors_agg = directors_agg[directors_agg["film_count"] >= min_films]
        studios_agg = studios_agg[studios_agg["film_count"] >= min_films]

        self.data = {
            'actors_agg': actors_agg,
            'directors_agg': directors_agg,
            'studios_agg': studios_agg,
            'actors_df': actors_df,
            'directors_df': directors_df,
            'studios_df': studios_df,
        }

    def get_data(self):
        return self.data

data_instance = EntitiesChartData()