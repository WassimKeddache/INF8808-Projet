import json
import pandas as pd

class MatrixData:
    def __init__(self):
        df = pd.read_csv("../data/combined.csv")
        self.preprocess_data(df)

    def extract_genres(self, genres_json):
        try:
            genres_json = genres_json.replace('""', '"')
            return [genre['name'] for genre in json.loads(genres_json)]
        except Exception:
            return []

        
    def preprocess_data(self, df):
        df['genres_list'] = df['genres'].apply(self.extract_genres)
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year

        df = df.dropna(subset=['budget', 'revenue', 'popularity', 'vote_count', 'vote_average', 'runtime'])
        df = df[(df['budget'] > 0) & (df['revenue'] > 0)]

        self.matrix_data = {
            'df': df,
        }

    def get_matrix_data(self):
        return self.matrix_data

data_instance = MatrixData()