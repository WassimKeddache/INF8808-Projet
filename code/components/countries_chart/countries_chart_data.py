import pandas as pd
import json
import pycountry

class CountriesChartData:
    def __init__(self):
        df = pd.read_csv("../data/combined.csv")
        self.preprocess_data(df)

# Fonction pour convertir ISO-2 en ISO-3
    def convert_iso2_to_iso3(self, iso2_code):
        try:
            if pd.isna(iso2_code) or iso2_code == '':
                return None
            country = pycountry.countries.get(alpha_2=iso2_code)
            if country:
                return country.alpha_3
            return None
        except Exception as e:
            return None

    # Prétraitement des données
    def extract_countries(self, countries_json):
        try:
            countries_json = countries_json.replace('""', '"')
            countries_list = json.loads(countries_json)
            # Extraire les codes ISO-2 et les convertir en ISO-3
            iso2_codes = [country['iso_3166_1'] for country in countries_list]
            iso3_codes = [self.convert_iso2_to_iso3(code) for code in iso2_codes]
            # Filtrer les codes None
            return [code for code in iso3_codes if code]
        except Exception as e:
            return []

    def extract_genres(self, genres_json):
        try:
            genres_json = genres_json.replace('""', '"')
            genres_list = json.loads(genres_json)
            return [genre['name'] for genre in genres_list]
        except Exception as e:
            return []
        
    def preprocess_data(self, df):
        df['countries'] = df['production_countries'].apply(self.extract_countries)
        df['genres_list'] = df['genres'].apply(self.extract_genres)

        # Conversion des dates et création de la colonne décennie
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year
        df['decade'] = (df['release_year'] // 10) * 10
        df = df.dropna(subset=['release_year', 'budget', 'revenue', 'popularity', 'vote_average'])

        # Explosion des pays pour avoir une ligne par pays de production
        countries_df = df.explode('countries')
        countries_df = countries_df[countries_df['countries'].notna() & (countries_df['countries'] != '')]

        # Liste des genres uniques pour le filtre
        all_genres = sorted(list(set([genre for sublist in df['genres_list'].dropna() for genre in sublist])))
        
        self.data = {
            'all_genres': all_genres,
            'df': countries_df
        }

    def get_data(self):
        return self.data

data_instance = CountriesChartData()