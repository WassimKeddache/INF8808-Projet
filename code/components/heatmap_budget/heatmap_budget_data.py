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
        self.preprocess_data(df)

    def extract_genres(self, genres_json):
        """
        Extrait et traduit les genres d'un JSON en une liste de genres traduits.
        """
        try:
            genres_json = genres_json.replace('""', '"')
            genres_list = json.loads(genres_json)

            return [genre['name'] for genre in genres_list]
        except Exception as e:
            print(f"Erreur lors de l'extraction des genres: {e}")
            print(f"JSON problématique: {genres_json}")
            return []
        
    def create_heatmap_df(self, df_exploded, complete_index, metric):
        metric_avg = df_exploded.groupby(['genre', 'release_date'])[metric].mean().reset_index()
        metric_df = pd.DataFrame(index=complete_index).reset_index()
        return metric_df.merge(metric_avg, on=['genre', 'release_date'], how='left').fillna(0)

    def preprocess_data(self, df):
        """
        Prétraite les données pour extraire les genres, années et autres colonnes nécessaires.
        """
        df['genres_list'] = df['genres'].apply(self.extract_genres)

        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df = df.dropna(subset=['release_date'])
        df['release_date'] = df['release_date'].dt.year.astype(int)
        df_exploded = df.explode('genres_list').rename(columns={'genres_list': 'genre'})
        df_exploded = df_exploded[(df_exploded['release_date'] >= 1970) & (~df_exploded['genre'].isna())]
        
        # Exclure l'année 2017 en raison d'un manque de données pour cette visualisation
        df_exploded = df_exploded[df_exploded['release_date'] != 2017]

        df_exploded['genre'] = df_exploded['genre'].map(genre_translations)

        all_genre_names = sorted(df_exploded['genre'].dropna().unique())
        # Exclure le genre "Téléfilm" en raison d'un manque de données pour cette visualisation
        all_genre_names = [genre for genre in all_genre_names if genre != 'Téléfilm']

        years = sorted(df_exploded['release_date'].unique())
        complete_index = pd.MultiIndex.from_product([all_genre_names, years], names=['genre', 'release_date'])


        budget_df = self.create_heatmap_df(df_exploded, complete_index, 'budget')
        vote_df = self.create_heatmap_df(df_exploded, complete_index, 'vote_average')
        revenue_df = self.create_heatmap_df(df_exploded, complete_index, 'revenue')

        budget_min_avg = budget_df['budget'].min()
        budget_max_avg = budget_df['budget'].max()
        revenue_min_avg = revenue_df['revenue'].min()
        revenue_max_avg = 400000000  # Valeur constante
        metric_ranges = {
            'revenue': [revenue_min_avg, revenue_max_avg],
            'vote_average': [0, 10]
        }

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