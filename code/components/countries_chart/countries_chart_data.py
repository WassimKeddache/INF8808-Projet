import pandas as pd
import json

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

translated_countries = {
    'Afghanistan': 'Afghanistan',
    'Algeria': 'Algérie',
    'Argentina': 'Argentine',
    'Aruba': 'Aruba',
    'Australia': 'Australie',
    'Austria': 'Autriche',
    'Bahamas': 'Bahamas',
    'Belgium': 'Belgique',
    'Bhutan': 'Bhoutan',
    'Bolivia': 'Bolivie',
    'Bosnia and Herzegovina': 'Bosnie-Herzégovine',
    'Brazil': 'Brésil',
    'Bulgaria': 'Bulgarie',
    'Canada': 'Canada',
    'Cameroon': 'Cameroun',
    'China': 'Chine',
    'Cyprus': 'Chypre',
    'Czech Republic': 'République tchèque',
    'Denmark': 'Danemark',
    'Dominican Republic': 'République dominicaine',
    'Ecuador': 'Équateur',
    'Finland': 'Finlande',
    'France': 'France',
    'Germany': 'Allemagne',
    'Greece': 'Grèce',
    'Guadaloupe': 'Guadeloupe',
    'Guyana': 'Guyana',
    'Hong Kong': 'Hong Kong',
    'Hungary': 'Hongrie',
    'Iceland': 'Islande',
    'India': 'Inde',
    'Indonesia': 'Indonésie',
    'Iran': 'Iran',
    'Ireland': 'Irlande',
    'Israel': 'Israël',
    'Italy': 'Italie',
    'Jamaica': 'Jamaïque',
    'Japan': 'Japon',
    'Kenya': 'Kenya',
    'Kyrgyz Republic': 'Kirghizistan',
    'Lebanon': 'Liban',
    'Libyan Arab Jamahiriya': 'Libye',
    'Luxembourg': 'Luxembourg',
    'Malaysia': 'Malaisie',
    'Malta': 'Malte',
    'Mexico': 'Mexique',
    'Morocco': 'Maroc',
    'Netherlands': 'Pays-Bas',
    'New Zealand': 'Nouvelle-Zélande',
    'Norway': 'Norvège',
    'Pakistan': 'Pakistan',
    'Panama': 'Panama',
    'Peru': 'Pérou',
    'Philippines': 'Philippines',
    'Poland': 'Pologne',
    'Romania': 'Roumanie',
    'Russia': 'Russie',
    'Singapore': 'Singapour',
    'Slovenia': 'Slovénie',
    'South Africa': 'Afrique du Sud',
    'South Korea': 'Corée du Sud',
    'Spain': 'Espagne',
    'Sweden': 'Suède',
    'Switzerland': 'Suisse',
    'Thailand': 'Thaïlande',
    'Turkey': 'Turquie',
    'United Arab Emirates': 'Émirats arabes unis',
    'United Kingdom': 'Royaume-Uni',
    'United States of America': 'États-Unis',
}


class CountriesChartData:
    def __init__(self):
        df = pd.read_csv("../data/combined.csv")
        self.preprocess_data(df)

    # Prétraitement des données
    def extract_countries(self, countries_json):
        try:
            countries_json = countries_json.replace('""', '"')
            countries_list = json.loads(countries_json)
            return [translated_countries.get(country['name'], country['name']) for country in countries_list]
        except Exception as e:
            return []

    def extract_genres(self, genres_json):
        try:
            genres_json = genres_json.replace('""', '"')
            genres_list = json.loads(genres_json)
            genres = [genre['name'] for genre in genres_list]
            return [genre_translations.get(genre, genre) for genre in genres]
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