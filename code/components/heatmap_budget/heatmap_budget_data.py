import json
import pandas as pd

genre_translations = {
    'Action': 'Action',
    'Adventure': 'Aventure',
    'Animation': 'Animation',
    'Comedy': 'Comédie',
    'Crime': 'Crime',
    'Documentary': 'Documentaire',
    'Drama': 'Drame',
    'Family': 'Famille',
    'Fantasy': 'Fantastique',
    'Foreign': 'Étranger',
    'History': 'Historique',
    'Horror': 'Horreur',
    'Music': 'Musique',
    'Mystery': 'Mystère',
    'Romance': 'Romance',
    'Science Fiction': 'Science-fiction',
    'TV Movie': 'Téléfilm',
    'Thriller': 'Thriller',
    'War': 'Guerre',
    'Western': 'Western'
}

class HeatmapBudgetData:
    def __init__(self):
        df = pd.read_csv("../data/combined.csv")

        df['genres_list'] = df['genres'].apply(self.extract_genres)

        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df = df.dropna(subset=['release_date'])
        df['release_date'] = df['release_date'].dt.year
        df['release_date'] = df['release_date'].astype(int)

        self.preprocess_heatmap_data(df)

    def extract_genres(self, genres_json):
        try:
            # Remplacer les doubles guillemets par des simples guillemets
            genres_json = genres_json.replace('""', '"')
            # Analyser le JSON
            genres_list = json.loads(genres_json)
            # Extraire les noms des genres

            return [genre['name'] for genre in genres_list]
        except Exception as e:
            print(f"Erreur lors de l'extraction des genres: {e}")
            print(f"JSON problématique: {genres_json}")
            return []
        
    def preprocess_heatmap_data(self, df):
        df_exploded = df.explode('genres_list').rename(columns={'genres_list': 'genre'})

        # Filtrer pour n'avoir que les données depuis 1970
        df_exploded = df_exploded[df_exploded['release_date'] >= 1970]

        df_exploded = df_exploded[~df_exploded['genre'].isna()]  # Supprimer les valeurs NaN

        # Mis à jour des noms de genre
        all_genre_names = sorted(df_exploded['genre'].unique())  # Trier les genres par ordre alphabétique
        
        # Appliquer la traduction
        df_exploded['genre'] = df_exploded['genre'].map(genre_translations)
        all_genre_names = sorted(df_exploded['genre'].dropna().unique())  # Mise à jour avec les noms traduits

        # Calculer les moyennes par genre et année pour tout le dataset
        all_budget_avg = df_exploded.groupby(['genre', 'release_date'])['budget'].mean().reset_index()
        all_revenue_avg = df_exploded.groupby(['genre', 'release_date'])['revenue'].mean().reset_index()

        # Calculer les valeurs min et max des MOYENNES pour chaque métrique
        budget_min_avg = all_budget_avg['budget'].min()
        budget_max_avg = all_budget_avg['budget'].max()

        revenue_min_avg = all_revenue_avg['revenue'].min()
        # Définir le max du revenu à 400 millions comme demandé
        revenue_max_avg = 400000000  # 400 millions

        vote_min_avg = 0
        vote_max_avg = 10

        # Dictionnaire des plages de valeurs pour chaque métrique (basé sur les moyennes)
        metric_ranges = {
            'revenue': [revenue_min_avg, revenue_max_avg],
            'vote_average': [vote_min_avg, vote_max_avg]
        }

        # Obtenir toutes les années depuis 1970
        years = sorted(df_exploded['release_date'].unique())

        budget_avg = df_exploded.groupby(['genre', 'release_date'])['budget'].mean().reset_index()
        vote_avg = df_exploded.groupby(['genre', 'release_date'])['vote_average'].mean().reset_index()
        revenue_avg = df_exploded.groupby(['genre', 'release_date'])['revenue'].mean().reset_index()

        complete_index = pd.MultiIndex.from_product(
            [all_genre_names, years],
            names=['genre', 'release_date']
        )
        
        # Créer des DataFrames complets avec des valeurs par défaut de 0
        budget_df = pd.DataFrame(index=complete_index).reset_index()
        budget_df = budget_df.merge(
            budget_avg, on=['genre', 'release_date'], how='left'
        ).fillna(0)
        
        vote_df = pd.DataFrame(index=complete_index).reset_index()
        vote_df = vote_df.merge(
            vote_avg, on=['genre', 'release_date'], how='left'
        ).fillna(0)

        revenue_df = pd.DataFrame(index=complete_index).reset_index()
        revenue_df = revenue_df.merge(
            revenue_avg, on=['genre', 'release_date'], how='left'
        ).fillna(0)

        self.heatmap_data = {
            'all_genre_names': all_genre_names,
            'budget_min_avg': budget_min_avg,
            'budget_max_avg': budget_max_avg,
            'metric_ranges': metric_ranges,
            'years': years,
            'budget_df': budget_df,
            'revenue_df': revenue_df,
            'vote_df': vote_df,
        }


    def get_heatmap_data(self):
        return self.heatmap_data

data_instance = HeatmapBudgetData()