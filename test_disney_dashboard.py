import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


# CSV-Dateien laden und bereinigen
movies_df = pd.read_csv('disney_movies.csv')
characters_df = pd.read_csv('disney-characters.csv')


# Bereinigen der movie_title Spalten
movies_df['movie_title'] = (movies_df['movie_title'].str.strip().str.replace
                            (r'\n', '', regex=True))
characters_df['movie_title'] = (characters_df['movie_title'].str.strip().
                                str.replace(r'\n', '', regex=True))


# Konvertieren der release_date Spalten zu datetime
movies_df['release_date'] = pd.to_datetime(movies_df['release_date'])
characters_df['release_date'] = pd.to_datetime(characters_df['release_date'],
                                               errors='coerce')


# Liste aller verfügbaren Jahre von den ersten bis zum letzten Film
min_year = movies_df['release_date'].dt.year.min()
max_year = movies_df['release_date'].dt.year.max()
available_years = list(range(min_year, max_year + 1))


# MPAA Ratings mit ihrer Bedeutung
ratings = {
    "G": "Geeignet für alle Altersgruppen.",
    "PG": "Geeignet für Kinder ab 5 Jahren, jedoch möglicherweise enthalten leichtes Sprachgut oder Themen.",
    "PG-13": "Geeignet für Kinder ab 13 Jahren, jedoch möglicherweise enthalten reifere Themen, Sprachgut oder Gewalt.",
    "R": "Geeignet für Erwachsene ab 17 Jahren, jedoch möglicherweise enthalten starker Sprachgut, Gewalt oder reifere Themen.",
    "NC-17": "Nur für Erwachsene geeignet, aufgrund expliziten Inhalts, wie z.B. graphischer Gewalt, starkem Sprachgut oder sexualisierten Themen."
}


# Dash-Anwendung initialisieren
app = dash.Dash(__name__)


# Farben und Stile definieren
colors = {
    'background': '#f9f9f9',
    'text': '#111111',
    'accent': '#4285F4',  # Google Blue
    'primary': '#FFD700'  # Disney Golden Yellow
}


# Erstellen eines Bar-Charts für MPAA Ratings
rating_counts = movies_df['mpaa_rating'].value_counts()
fig_rating_counts = px.bar(rating_counts,
                           x=rating_counts.index,
                           y=rating_counts.values,
                           labels={'x': 'Rating', 'y': 'Count'},
                           title='MPAA Rating Frequencies')


# Genre-Verteilung im gesamten Datensatz finden
genre_counts = movies_df['genre'].value_counts()
fig_genre_counts = px.bar(genre_counts,
                          x=genre_counts.index,
                          y=genre_counts.values,
                          labels={'x': 'Genre', 'y': 'Number of Films'},
                          title='Distribution of Disney Film Genres')


# Layout der Anwendung
app.layout = html.Div(style={'backgroundColor': colors['background'],
                             'fontFamily': 'Arial, sans-serif'},
                      children=[html.H1("Disney Filme Dashboard",
                                style={'textAlign': 'center',
                                       'color': colors['accent']}),


# Charts über dem Dropdown-Menü platzieren
    html.Div([
        dcc.Graph(id='rating_counts_chart',
                  figure=fig_rating_counts,
                  style={'width': '49%', 'display': 'inline-block',
                         'verticalAlign': 'top'}),
        html.Div([
            dcc.Graph(id='genre_distribution_chart',
                      figure=fig_genre_counts,
                      style={'width': '100%', 'display': 'inline-block',
                             'verticalAlign': 'top'}),
            html.Img(id='funny_image_3',
                     src='/assets/funny_image_3.png',
                     style={'width': '400px', 'height': 'auto',
                            'position': 'absolute', 'top': '50%', 'left': '50%',
                            'transform': 'translate(-50%, -50%)',
                            'display': 'none'})
        ], style={'position': 'relative', 'width': '49%',
                  'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'marginTop': 30, 'padding': '10px', 'fontSize': 16}),


    html.Div([
        html.Label("Wählen Sie ein Jahr aus:",
                   style={'color': colors['text'], 'fontSize': 18}),
        dcc.Dropdown(
            id='year_dropdown',
            options=[{'label': year, 'value': year} for year in available_years],
            style={'marginBottom': 20, 'marginTop': 10,
                   'padding': '10px', 'fontSize': 16, 'width': '100%'}
        ),
        html.Div(id='film_list',
                 style={'marginTop': 30, 'padding': '10px', 'fontSize': 16}),

        # Hier wird das Audio-Element hinzugefügt
        html.Audio(id='music',
                   controls=True,
                   autoPlay=True,
                   style={'width': '100%', 'marginTop': 20}),
    ], style={'marginTop': 30, 'padding': '10px', 'fontSize': 16}),
])


# Sad Trombone Sound Datei
sad_trombone_file = "assets/Sad Trombone - Sound Effect (HD).mp3"


# Callback-Funktion zur Verarbeitung der Eingabe und Ausgabe der Ergebnisse
@app.callback(
    [Output('film_list', 'children'),
     Output('genre_distribution_chart', 'figure'),
     Output('music', 'src'),
     Output('music', 'key'),
     Output('funny_image_3', 'style')],
    [Input('year_dropdown', 'value')]
)
def update_output(selected_year):
    if selected_year is None:
        return ["Wählen Sie ein Jahr aus."], fig_genre_counts, '', '', {'display': 'none'}

    # Filme im ausgewählten Jahr finden
    films = movies_df[movies_df['release_date'].dt.year == selected_year]

    if (films.empty or films['genre'].isnull().all()
            or films['mpaa_rating'].isnull().all()):

        film_titles = films['movie_title'].tolist()
        film_list = [html.Div(html.H3(title)) for title in film_titles]
        fig_genre = fig_genre_counts
        music_src = sad_trombone_file
        music_key = f'{selected_year}_sad_trombone'
        image_style = {'width': '500px', 'height': '360px',
                       'position': 'absolute', 'top': '50%',
                       'left': '50%',
                       'transform': 'translate(-50%, -50%)',
                       'display': 'block'}  # Bild anzeigen
    else:
        film_list = []
        for index, row in films.iterrows():

            # Charaktere und Titelmusik für den Film
            character_info = characters_df[characters_df['movie_title'] ==
                                           row['movie_title']]
            if not character_info.empty:
                hero = character_info['hero'].values[0]
                villain = character_info['villian'].values[0]
                song = character_info['song'].values[0]
            else:
                hero = villain = song = 'nicht bekannt'

            # MPAA Rating um die Bedeutung erweitern
            mpaa_rating = f"{row['mpaa_rating']} - {ratings.get(row['mpaa_rating'], 'nicht bekannt')}"

            film_info = html.Div([
                html.H3(row['movie_title']),
                html.P(f"Genre: {row['genre']}"),
                html.P(f"Hero: {hero}"),
                html.P(f"Villain: {villain}"),
                html.P(f"Title Song: {song}"),
                html.P(f"MPAA Rating: {mpaa_rating}"),
                html.P(f"Total Gross: ${row['total_gross']:,.2f}"),
                html.P(f"Inflation Adjusted Gross: ${row['inflation_adjusted_gross']:,.2f}")
            ])
            film_list.append(film_info)

        # Genre-Verteilung im Jahr finden
        genre_counts = films['genre'].value_counts()
        fig_genre = px.bar(genre_counts,
                           x=genre_counts.index,
                           y=genre_counts.values,
                           labels={'x': 'Genre', 'y': 'Number of Films'},
                           title=f'Distribution of Disney Film Genres in '
                                 f'{selected_year}')

        # Musikdatei basierend auf dem Genre auswählen
        genre = genre_counts.idxmax() if not genre_counts.empty else None
        if genre == 'Drama':
            music_src = '/assets/Disney 05.mp3'
        elif genre == 'Adventure':
            music_src = '/assets/Disney 10.mp3'
        elif genre == 'Comedy':
            music_src = '/assets/Disney D.mp3'
        else:
            music_src = '/assets/Disney_03.mp3'

        music_key = f'{selected_year}_{genre}'
        image_style = {'width': '555px',
                       'height': '350px',
                       'position': 'absolute',
                       'top': '50%',
                       'left': '50%',
                       'transform': 'translate(-50%, -50%)',
                       'display': 'none'}  # Bild verstecken

    # Bild anzeigen, wenn die Sad Trombone Datei abgespielt wird
    if music_src == sad_trombone_file:
        image_style = {'width': '555px',
                       'height': '350px',
                       'position': 'absolute',
                       'top': '50%',
                       'left': '50%',
                       'transform': 'translate(-50%, -50%)',
                       'display': 'block'}

    return film_list, fig_genre, music_src, music_key, image_style

# Anwendung starten
if __name__ == '__main__':
    app.run_server(debug=True)
