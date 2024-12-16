import time
from typing import Counter
import requests

# id du compte roblox 
id_j1 = "2221792753" 
id_j2 = "2662313535" 

# compatibilité minimal du genre apprécié.
poid = 0.07

def recu_genre_by_id(genre_j1, id_game) :
    try :
        genre = genre_j1
        # Parcourir les jeux pour récupérer leur genre
        url_1 = f"https://games.roproxy.com/v1/games?universeIds={id_game}"

        # Utilisation de la session pour maintenir l'authentification
        response = requests.get(url_1)

        if response.status_code == 200:
            data = response.json()
            # print(data["data"][0]["genre"])
            genre = data["data"][0]["genre"]
            # Recherche de l'élément du genre
            if genre:
                # print(f"Genre trouvé : {genre}")
                genre_j1.append(genre)
            else:
                # print("Élément du genre non trouvé.")
                ok = "rien"

            genre = data["data"][0]["genre_l1"]
            # Recherche de l'élément du genre
            if genre:
                # print(f"Genre_l1 trouvé : {genre}")
                genre_j1.append(genre)
            else:
                # print("Élément du genre non trouvé.")
                ok = "rien"

            genre = data["data"][0]["genre_l2"]
            # Recherche de l'élément du genre
            if genre:
                # print(f"Genre_l2 trouvé : {genre}")
                genre_j1.append(genre)
            else:
                # print("Élément du genre non trouvé.")
                ok = "rien"
        
        else:
            print(f"Erreur lors de la récupération de la page du jeu {id_game} : {response.status_code}")
        return genre_j1
    except :
            print(f"Erreur lors de la récupération de la page")
    return []


def donne_poids(genre_j1) :
    # Étape 1 : Compter les occurrences
    genre_counts = Counter(genre_j1)

    # Étape 2 : Calculer les poids (normalisation)
    total_count = sum(genre_counts.values())
    genre_weights = {genre: count / total_count for genre, count in genre_counts.items()}

    # Étape 3 : Créer une liste contenant le genre et son poids
    weighted_genres = [(genre, weight) for genre, weight in genre_weights.items()]
    return weighted_genres

def recup_genre_weighted(id_j) :
    # L'URL cible
    url = f"https://www.roblox.com/fr/users/favorites/list-json?assetTypeId=9&itemsPerPage=100&pageNumber=1&userId={id_j}"

    # Utilisation de la session authentifiée
    response = requests.get(url)

    # Vérifier que la requête s'est bien passée (code 200)
    if response.status_code == 200:
        # Charger les données JSON
        data = response.json()

        # Afficher les données récupérées
        # print(json.dumps(data, indent=4))
    else:
        print("Erreur lors de la récupération des données:", response.status_code)

    game_j1 = []

    if "Data" in data and "Items" in data["Data"]:
        for game in data["Data"]["Items"]:
            game_j1.append(game["Item"]["UniverseId"])

    print("Liste des IDs de jeux :", game_j1)

    genre_j1 = []
    for id_game in game_j1:
        genre_j1 = recu_genre_by_id(genre_j1, id_game)
        time.sleep(1)  # Attendre 1 seconde avant d'envoyer la prochaine requête


    print("Genres récupérés :", genre_j1)

    weighted_genres = donne_poids(genre_j1)

    return weighted_genres


genre_j1 = recup_genre_weighted(id_j1)
genre_j2 = recup_genre_weighted(id_j2)


genre_j1 = dict(genre_j1)
genre_j2 = dict(genre_j2)

# Identifier les genres en commun
common_genres = set(genre_j1.keys()) & set(genre_j2.keys())


common_genres_analysis = sorted(
    [
        {
            "genre": genre,
            "weight_list1": genre_j1[genre],
            "weight_list2": genre_j2[genre],
            "combined_weight": (genre_j1[genre] + genre_j2[genre]) / 2
        }
        for genre in common_genres
    ],
    key=lambda x: x["combined_weight"],
    reverse=True
)

# Filtrer les genres avec un poids combiné >= 0.07
common_genres_analysis = [
    entry for entry in common_genres_analysis if entry["combined_weight"] >= poid
]

# Affichage des résultats
print("Genres en commun et leurs poids :")
for entry in common_genres_analysis:
    print(f"{entry['genre']}: List1 = {entry['weight_list1']:.2f}, List2 = {entry['weight_list2']:.2f}, en duo = {entry['combined_weight']:.2f}")

genre_commun = []
for i in range(len(common_genres_analysis)) : 
    genre_commun.append(common_genres_analysis[i]["genre"])

print(genre_commun)



# On récup les jeux populaires

url = "https://apis.roblox.com/explore-api/v1/get-sorts"
params = {
    "sessionId": "013d0529-13f3-4ed4-a7cb-aeb044e875b8",  # Peut être généré dynamiquement
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    jeu_genres = {}

    for game in data["sorts"][1]["games"] :
        genre = []
        game_name = game["name"]  # Nom du jeu
        genres = recu_genre_by_id(genre, game["universeId"])  # Récupérer les genres pour ce jeu
        jeu_genres[game_name] = genres  # Associer le jeu à ses genres
else:
    print(f"Erreur : {response.status_code} - {response.text}")

# print(jeu_genres)

# Liste pour stocker les jeux correspondant au genre recherché
jeux_trouves = []

# Parcourir le dictionnaire pour filtrer les jeux qui ont le genre recherché
for jeu, genres in jeu_genres.items():
    for genre_target in genre_commun :
        if genre_target in genres:
            jeux_trouves.append(jeu)

# Afficher les jeux trouvés
for jeu in jeux_trouves:
    print(jeu)

game_sorted = donne_poids(jeux_trouves)

game_sorted = sorted(game_sorted, key=lambda x: x[1], reverse=True)

for entry in game_sorted:
    print(f"{entry[0]}: score = {entry[1]:.2f}")
