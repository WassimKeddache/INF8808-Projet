import pandas as pd

def load(movies_file_path, credits_file_path):
    # Chargement des données
    movies_df = pd.read_csv(movies_file_path)
    credits_df = pd.read_csv(credits_file_path)
    
    # Renommer la colonne 'id' dans movies_df pour correspondre à 'movie_id' dans credits_df
    movies_df = movies_df.rename(columns={'id': 'movie_id'})
    
    # Fusion des DataFrames sur movie_id
    combined_df = pd.merge(movies_df, credits_df, on='movie_id', how='left', suffixes=('', '_credits'))
    
    print(f"Nombre de films dans le dataset original: {len(movies_df)}")
    print(f"Nombre de films dans le dataset de crédits: {len(credits_df)}")
    print(f"Nombre de films dans le dataset combiné: {len(combined_df)}")
    print(combined_df.head())
    return combined_df

if __name__ == '__main__':
    movies_file_path = 'data/tmdb_5000_movies.csv'
    credits_file_path = 'data/tmdb_5000_credits.csv'
    combined_df = load(movies_file_path, credits_file_path)
    combined_df.to_csv('data/combined.csv', index=False)
