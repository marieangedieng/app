import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import altair as alt
from urllib.parse import urljoin
import time
import random
import altair as alt


# --- Barre latérale pour la navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", 
                        ["Scraper", "Télécharger données", "Dashboard", "Évaluation de l'app"])

# --- 1. Scraper des données sur plusieurs pages ---
if page == "Scraper":
    st.title("Scraping de données multi-pages")
    category = st.selectbox("Choisissez la catégorie à scraper", ["Villas", "Terrains", "Appartements"])
    # Définition de l'URL de départ en fonction de la catégorie sélectionnée
    base_urls = {
        "Villas": "https://sn.coinafrique.com/categorie/villas",
        "Terrains": "https://sn.coinafrique.com/categorie/terrains",
        "Appartements": "https://sn.coinafrique.com/categorie/appartements"
    }

    start_url = base_urls[category]
    num_pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=100, value=1, step=1)

    if st.button("Lancer le scraping"):
        df = pd.DataFrame()
        for page_num in range(int(num_pages)):
            time.sleep(random.uniform(2, 5))
            current_url = start_url+f'?page={page_num+1}'
            res = requests.get(current_url) # récupération du code html de la page
            soup = bs(res.text, 'html.parser') # stocker le code html dans un objet beautifulsoup
            containers = soup.find_all('div', class_ = 'col s6 m4 l3')#groupe de container
            data = []
            if category == "Villas":
                # --- Scraping pour les Villas ---
                for container in containers:
                    try:
                        link=container.find('a', class_ = 'card-image ad__card-image waves-block waves-light').get('href')#dans chaque container recupere le lien
                        if not link:
                            continue
                        container_url=urljoin(current_url, link)#recupere le lien complet
                        time.sleep(random.uniform(1, 3))
                        res1 = requests.get(container_url)
                        soup1 = bs(res1.text, 'html.parser')
                        type_annonce=soup1.find('h1', class_ = 'title title-ad hide-on-large-and-down').text.strip().split()[0]
                        li_elements = soup1.find_all('li', class_='center')
                        for li in li_elements:
                            if li.find('span') and li.find('span').text.strip() == "Nbre de pièces":
                              nb_piece = li.find('span', class_='qt').text.strip()
                        prix = soup1.find('p', class_ = 'price').text.strip().replace('\u202f', '').replace(' ', '').replace('CFA', '')
                        element = soup1.find("span", attrs={"data-address": True})
                        adresse = element["data-address"]
                        image_lien=container.find('img', class_ = 'ad__card-img').get('src')
                        dic = {"type_annonce": type_annonce,
                            "nb_piece": nb_piece,
                            "prix": prix,
                            "adresse": adresse,
                            "image_lien": image_lien}
                        data.append(dic)
                    except requests.exceptions.RequestException as e:
                        print(f"Grosse erreur sur la page {page_num+1}: {str(e)}")
                        time.sleep(30)
                        continue
            elif category == "Terrains":
                # --- Scraping pour les Terrains ---
                for container in containers:
                    try:
                        link=container.find('a', class_ = 'card-image ad__card-image waves-block waves-light').get('href')
                        if not link:
                            continue
                        container_url=urljoin(current_url, link)
                        time.sleep(random.uniform(1, 3))
                        res1 = requests.get(container_url)
                        soup1 = bs(res1.text, 'html.parser')
                        li_elements = soup1.find_all('li', class_='center')
                        for li in li_elements:
                            if li.find('span') and li.find('span').text.strip() == "Superficie":
                                superficie = li.find('span', class_='qt').text.strip().replace(' m²', '')
                        prix = soup1.find('p', class_ = 'price').text.strip().replace('\u202f', '').replace(' CFA', '')
                        element = soup1.find("span", attrs={"data-address": True})
                        adresse = element["data-address"]
                        image_lien=container.find('img', class_ = 'ad__card-img').get('src')
                        dic = {"superficie": superficie,
                                "prix": prix,
                                "adresse": adresse,
                                "image_lien": image_lien}
                        data.append(dic)
                    except requests.exceptions.RequestException as e:
                        print(f"Grosse erreur sur la page {page_num+1}: {str(e)}")
                        time.sleep(30)
                        continue
            elif category == "Appartements":
                # --- Scraping pour les Appartements ---
                for container in containers:
                    try:
                        link=container.find('a', class_ = 'card-image ad__card-image waves-block waves-light').get('href')
                        if not link:
                            continue
                        container_url=urljoin(current_url, link)
                        time.sleep(random.uniform(1, 3))
                        res1 = requests.get(container_url)
                        soup1 = bs(res1.text, 'html.parser')
                        li_elements = soup1.find_all('li', class_='center')
                        for li in li_elements:
                            if li.find('span') and li.find('span').text.strip() == "Nbre de pièces":
                                nb_piece = li.find('span', class_='qt').text.strip()
                        prix = soup1.find('p', class_ = 'price').text.strip().replace('\u202f', '').replace(' CFA', '')
                        element = soup1.find("span", attrs={"data-address": True})
                        adresse = element["data-address"]
                        image_lien=container.find('img', class_ = 'ad__card-img').get('src')
                        dic = {"nb_piece": nb_piece,
                                "prix": prix,
                                "adresse": adresse,
                                "image_lien": image_lien}
                        data.append(dic)
                    except requests.exceptions.RequestException as e:
                        print(f"Grosse erreur sur la page {page_num+1}: {str(e)}")
                        time.sleep(30)
                        continue
        if data:
            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis = 0).reset_index(drop = True)
            st.write("Données scrappées")
            # Sauvegarde dans un fichier CSV (données non nettoyées)
            df.to_csv("app_donne_scraped.csv", index=False)
            st.success("Scraping terminé et données sauvegardées dans app_donne_scraped.csv.")
        else:
            st.warning("Aucune donnée trouvée. Vérifiez l'URL de départ ou le nombre de pages.")

# --- 2. Télécharger les données déjà scrappées (non nettoyées) ---
elif page == "Télécharger données":
    st.title("Télécharger les données non nettoyées")
    
    # Dictionnaire associant chaque catégorie à son fichier CSV
    file_mapping = {
        "Villas": "villas_web.csv",
        "Terrains": "terrains_web.csv",
        "Appartements": "apart_web.csv"
    }

    for category, file_name in file_mapping.items():
        try:
            df = pd.read_csv(file_name)
            st.write(f"### Aperçu des données - {category}")
            st.dataframe(df.head(10))  # Affichage des 5 premières lignes
            
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"Télécharger les données {category}",
                data=csv_data,
                file_name=file_name,
                mime="text/csv"
            )
        except FileNotFoundError:
            st.warning(f"Aucune donnée disponible pour {category}. Veuillez lancer le scraping d'abord.")

# --- 3. Dashboard des données nettoyées ---
elif page == "Dashboard":
    st.title("Dashboard des données nettoyées")

    # Dictionnaire associant chaque catégorie à son fichier nettoyé
    file_mapping = {
        "Villas": "villas_web_cleaned.csv",
        "Terrains": "terrains_web_cleaned.csv",
        "Appartements": "apart_web_cleaned.csv"
    }

    for category, file_name in file_mapping.items():
        try:
            df = pd.read_csv(file_name)
            st.write(f"### Données nettoyées - {category}")
            st.dataframe(df.head(10))  # Affichage des 5 premières lignes
        except FileNotFoundError:
            st.warning(f"Aucune donnée nettoyée disponible pour {category}.")
        except Exception as e:
            st.error(f"Erreur lors du traitement des données {category} : {e}")

# --- 4. Formulaire d’évaluation de l’app ---
elif page == "Évaluation de l'app":
    st.title("Évaluation de l'application")
    with st.form("evaluation_form"):
        name = st.text_input("Nom")
        email = st.text_input("Email")
        rating = st.slider("Note de satisfaction", min_value=0, max_value=10, value=5)
        feedback = st.text_area("Commentaires")
        submitted = st.form_submit_button("Envoyer l'évaluation")
        
    if submitted:
        st.success("Merci pour votre évaluation !")
        # Sauvegarde de l'évaluation dans un fichier CSV
        evaluation = {"Nom": name, "Email": email, "Note": rating, "Commentaires": feedback}
        try:
            eval_df = pd.read_csv("evaluations.csv")
            # Ajout de la nouvelle évaluation
            eval_df = eval_df.append(evaluation, ignore_index=True)
        except Exception:
            eval_df = pd.DataFrame([evaluation])
        eval_df.to_csv("evaluations.csv", index=False)