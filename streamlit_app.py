$ pip install -r requirements.txt
$ streamlit run streamlit_app.py
import streamlit as st
from datetime import datetime, date, time
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import requests  # Pour interagir avec l'API CBIP

# Configuration de la page
st.set_page_config(page_title="Gestion des Patients", layout="wide")

# Fonction pour générer un PDF
def generate_pdf(data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(72, 750, "Rapport Patient")
    y = 730
    for key, value in data.items():
        c.drawString(72, y, f"{key}: {value}")
        y -= 15
    c.save()

# Fonction pour calculer l'âge
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# Fonction pour vérifier le médicament dans CBIP
def verifier_medicament_cbip(nom_medicament):
    # URL de l'API CBIP (à remplacer par l'URL réelle)
    url = "https://www.cbip.be/fr/"
    params = {"nom": nom_medicament}
    headers = {"Authorization": "Bearer VOTRE_CLE_API"}  # Remplacez par votre clé API

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)  # Ajout d'un timeout
        if response.status_code == 200:
            data = response.json()
            if data:  # Si le médicament est trouvé
                return True, data
            else:
                return False, "Médicament non trouvé dans CBIP."
        else:
            return False, f"Erreur API CBIP : {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Erreur de connexion à CBIP : {str(e)}"

# Fonction pour formater les détails des dépôts dentaires
def format_depot_details(depot_choix, depot_details):
    if not depot_choix or "Inexistant" in depot_choix:
        return "Inexistant"

    details_string = ", ".join(depot_choix)  # Joindre tous les choix sélectionnés

    if depot_details:
        locations = []
        if "Gen." in depot_details["locations"]:
            locations.append("Gen.")
        if "Collet" in depot_details["locations"]:
            locations.append("Collet")
        if "Préciser" in depot_details["locations"] and depot_details["Préciser"]:
            locations.append(f"Préciser: {depot_details['Préciser']}")
        if "Sext" in depot_details["locations"] and depot_details["Sext"]:
            sext_values = ", ".join(depot_details['Sext'])
            locations.append(f"Sext: {sext_values}")

        if locations:
            details_string += " (" + ", ".join(locations) + ")"

    return details_string.strip()  # Supprime les espaces inutiles

# Fonction pour préparer les données
def prepare_data():
    data = {
        "Nom et Prénom": nom_prenom if nom_prenom else None,
        "Prochain Rendez-vous": prochain_rdv.strftime("%d.%m.%Y %H:%M") if prochain_rdv else None,
        "Date d'aujourd'hui": date_aujourdhui.strftime("%d.%m.%Y") if date_aujourdhui else None,
        "Numéro du Patient": num_patient if num_patient else None,
        "Date de Naissance": date_naissance.strftime("%d.%m.%Y") if date_naissance else None,
        "Praticien": praticien if praticien else None,
        "HDD": hdd.strftime('%H:%M') if hdd else None,
        "RP-P": rpp_details if rpp == "Oui" and rpp_details else None,
        "ANM": f"{anm_type}: {medicament} - {pathologie}" if anm_type and medicament and pathologie else None,
        "Allergies": allergies if allergies else None,
        "Opérations": operations if operations else None,
        "Cigarette": cigarette_details if cigarette != "Non" and cigarette_details else cigarette if cigarette else None,
        "Drogue": drogue_details if drogue != "Non" and drogue_details else drogue if drogue else None,
        "Biphosphonate": biphosphonate_details if biphosphonate != "Non" and biphosphonate_details else biphosphonate if biphosphonate else None,
        "Douleur quelconque": douleur if douleur else None,
        "PDP": pdp if pdp else None,
        "Dernière visite": derniere_visite if derniere_visite else None,
        "Sexe": sexe if sexe else None,
        "Enceinte": enceinte if sexe == "Femme" and enceinte else None,
        "Contraception": contraception_details if sexe == "Femme" and contraception == "Oui" and contraception_details else None,
        "Activité": activite if activite else None,
        "ALIM": f"{alim} x/j" if alim else None,
        "Boissons": ", ".join([f"{boisson} x/j" for boisson in boissons]) if boissons else None,
        "Thé": f"{the_frequence} x/j" if "Thé" in boissons and the_frequence else None,
        "Café": f"{cafe_frequence} x/j" if "Café" in boissons and cafe_frequence else None,
        "Soda": f"{soda_frequence} x/j" if "Soda" in boissons and soda_frequence else None,
        "Sucre": f"{sucre} x/j" if sucre else None,
        "HOD": hod if hod else None,
        "Fréquence de brossage": frequence_brossage if frequence_brossage else None,
        "Moyens aux": ", ".join(moyens_aux) if moyens_aux else None,
        "Fréquence Moyens Aux": frequence_moyens_aux if moyens_aux and frequence_moyens_aux else None,
        "BdB": bdb_details if bdb == "Oui" and bdb_details else None,
        "Dentifrice": dentifrice if dentifrice else None,
        "Type de poils": type_poils if type_poils else None,
        "Temps de brossage": temps_brossage if temps_brossage else None,
        "CVE": cve if cve else None,
        "DCO": dco_details if dco == "Suspicion" and dco_details else None,
        "EO": eo_details if eo == "Suspicion" and eo_details else None,
        "IO": io_details if io == "Suspicion" and io_details else None,
        "Overbite": f"{overbite} - {overbite_value} mm" if overbite and overbite in ["Léger", "Moyen", "Important"] and overbite_value else None,
        "Overjet": f"{overjet} - {overjet_value} mm" if overjet and overjet in ["Léger", "Moyen", "Important"] and overjet_value else None,
        "Classe d'angle": classe_angle if classe_angle else None,
        "DPSI": f"{sext1}/{sext2}/{sext3} | {sext6}/{sext5}/{sext4}" if sext1 and sext2 and sext3 and sext4 and sext5 and sext6 else None,
        "BF": format_depot_details(bf_data, bf_details),
        "TR": format_depot_details(tr_data, tr_details),
        "COL": format_depot_details(col_data, col_details),
        "BOI": format_depot_details(boi_data, boi_details),
        "BOP": format_depot_details(bop_data, bop_details),
        "ED": ed if ed else None,
        "Q1": q1 if q1 else None,
        "Q2": q2 if q2 else None,
        "Q3": q3 if q3 else None,
        "Q4": q4 if q4 else None,
        "RX": ", ".join(rx_choix) if rx_choix else None,
        "Rétro-alvéolaire": retro_autre if 'retro_autre' in locals() and retro_autre else None,
        "DHD": f"{dhd} - Stade: {stade}, Grade: {grade}" if dhd == "Parodontite" and stade and grade else None,
        "IHO Technique de brossage": technique if technique else None,
        "IHO Conseillé de changé de méthode de brossage": type_brosse if type_brosse else None,
        "IHO Bain de bouche": bain_bouche if bain_bouche else None,
        "IHO Conseil de dentifrice": conseil_dentifrice if conseil_dentifrice else None,
         "ACJ": ", ".join(acj_choix) if acj_choix else None,  # Include ACJ selections
        "Detartrage Options": ", ".join(detartrage_choix) if detartrage_choix else None,  # Include Detartrage Options
        "Surfaçage Options": ", ".join(surfacage_choix) if surfacage_choix else None,

        "Espaces Interdentaires Maxillaire": "\n".join([f"{space}: {all_interdental_data[space]}" for space in maxillaire_spaces if space in all_interdental_data and all_interdental_data[space]]),
        "Espaces Interdentaires Mandibulaire": "\n".join([f"{space}: {all_interdental_data[space]}" for space in mandibulaire_spaces if space in all_interdental_data and all_interdental_data[space]]),
   
        "PF": pf if pf else None,
        "PF dentiste": pf_dentiste if pf_dentiste else None,
        "Facturé": facture if facture else None,
    }
    # Supprimer les clés avec des valeurs None
    data = {k: v for k, v in data.items() if v is not None}
    return data

def generate_text_report(data):
    report = f"Rapport Patient\n\n"
    for key, value in data.items():
        report += f"{key}: {value}\n"  # Simplest way to add all key-value pairs
    return report

# Interface utilisateur
st.title("Gestion des Patients")

# Onglets
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Informations Patient", "Praticien", "Anamnèse", "Habitudes Alimentaires",
    "Hygiène à Domicile", "Examens", "IHO"
])

# Onglet 1 : Informations Patient
with tab1:
    nom_prenom = st.text_input("Nom et Prénom")
    prochain_rdv = st.date_input("Prochain rendez-vous", value=datetime.now(), format="DD.MM.YYYY")
    heure_rdv = st.time_input("Heure du prochain rendez-vous", value=datetime.now().time())
    prochain_rdv = datetime.combine(prochain_rdv, heure_rdv)
    date_aujourdhui = st.date_input("Date d'aujourd'hui", datetime.today())
    num_patient = st.text_input("Numéro du Patient")
    date_naissance = st.date_input("Date de Naissance", min_value=date(1900, 1, 1), max_value=date.today())
    age = calculate_age(date_naissance) if date_naissance else None
    st.write(f"Âge: {age}" if age else "")

    # Section HDD (Heure d'Arrivée)
    st.write("HDD (Heure d'Arrivée):")
    hdd = st.time_input("Heure d'arrivée", value=datetime.now().time())

# Onglet 2 : Praticien
with tab2:
    praticien = st.selectbox("Praticien", ["Claessens Sasha", "Autre"])
    if praticien == "Autre":
        praticien = st.text_input("Entrez le nom du praticien")

# Onglet 3 : Anamnèse
with tab3:
    anm_type = st.selectbox("Type", ["ANM", "ANM-R", "PRP"])
    if anm_type:
        medicament = st.text_input("Nom du médicament")
        if medicament:
            medicament_valide, message = verifier_medicament_cbip(medicament)
            if not medicament_valide:
                st.error(f"Erreur : {message}")
            else:
                st.success("Médicament validé dans CBIP.")
        pathologie = st.text_input("Pathologie associée")
    allergies = st.text_input("Allergies")
    operations = st.text_input("Opérations")

    # Ajout des onglets Cigarette, Drogue, Biphosphonate
    cigarette = st.radio("Cigarette", ["Non", "Oui", "Antécédent"])
    cigarette_details = ""
    if cigarette != "Non":
        cigarette_details = st.text_input("Précisez (Cigarette)")

    drogue = st.radio("Drogue", ["Non", "Oui", "Antécédent"])
    drogue_details = ""
    if drogue != "Non":
        drogue_details = st.text_input("Précisez (Drogue)")

    biphosphonate = st.radio("Biphosphonate", ["Non", "Oui", "Antécédent"])
    biphosphonate_details = ""
    if biphosphonate != "Non":
        biphosphonate_details = st.text_input("Précisez (Biphosphonate)")

    douleur = st.text_input("Douleur quelconque")
    pdp = st.text_input("PDP")
    derniere_visite = st.selectbox("Dernière visite", ["1 mois", "2 mois", "3 mois", "6 mois", "1 an", "+ d'un an"])
    sexe = st.radio("Sexe", ["Homme", "Femme"])
    if sexe == "Femme":
        enceinte = st.radio("Enceinte", ["Oui", "Non"])
        contraception = st.radio("Moyen de contraception", ["Oui", "Non"])
        if contraception == "Oui":
            contraception_details = st.text_input("Précisez le moyen de contraception")
    activite = st.text_input("Activité")

    # Section RP-P
    rpp = st.radio("RP-P", ["Oui", "Non"])
    if rpp == "Oui":
        rpp_details = st.text_input("Détails RP-P", value="0.12% CHX")

# Onglet 4 : Habitudes Alimentaires
with tab4:
    st.write("Nombre de repas par jour :")
    alim = st.selectbox("ALIM", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4"])
    
    st.write("Boissons :")
    boissons = st.multiselect("Boissons", ["Eau", "Thé", "Café", "Soda"])
    if "Thé" in boissons:
        the_frequence = st.selectbox("Fréquence de Thé", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4"])
    if "Café" in boissons:
        cafe_frequence = st.selectbox("Fréquence de Café", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4"])
    if "Soda" in boissons:
        soda_frequence = st.selectbox("Fréquence de Soda", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4"])
    
    sucre = st.selectbox("Sucre", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4"])

# Onglet 5 : Hygiène à Domicile
with tab5:
    hod = st.radio("HOD", ["BàD-e", "BàD-m"])
    frequence_brossage = st.selectbox("Fréquence de brossage", ["0 à 1", "1 à 2", "2", "2 à 3"])
    moyens_aux = st.multiselect("Moyens aux", ["Aucun", "Brossettes", "Fil dentaire", "Porte fil", "Soft pick", "Autre"])

    frequence_moyens_aux = ""
    if moyens_aux:
        frequence_moyens_aux = st.text_input("Fréquence d'utilisation des moyens aux")

    if "Autre" in moyens_aux:
        autre_moyen = st.text_input("Précisez l'autre moyen")
    bdb = st.radio("BdB", ["Oui", "Non"])
    if bdb == "Oui":
        bdb_details = st.text_input("Détails BdB")
    dentifrice = st.text_input("Dentifrice")
    type_poils = st.selectbox("Type de poils", ["Soft", "Medium", "Hard"])
    temps_brossage = st.selectbox("Temps", ["1min", "2min", "3min"])

# Onglet 6 : Examens
with tab6:
    st.write("Examens :")
    cve = st.radio("CVE", ["Oui", "RVE"])
    dco = st.radio("DCO", ["RAS", "Suspicion"])
    if dco == "Suspicion":
        dco_details = st.text_input("Détails DCO")
    eo = st.radio("EO", ["RAS", "Suspicion"])
    if eo == "Suspicion":
        eo_details = st.text_input("Détails EO")
    io = st.radio("IO", ["RAS", "Suspicion"])
    if io == "Suspicion":
        io_details = st.text_input("Détails IO")

    st.write("### Occlusion")
    overbite = st.selectbox("Overbite", ["Normal", "Léger", "Moyen", "Important"])
    overbite_value = ""
    if overbite in ["Léger", "Moyen", "Important"]:
        overbite_value = st.text_input("Valeur Overbite (mm)")

    overjet = st.selectbox("Overjet", ["Normal", "Léger", "Moyen", "Important"])
    overjet_value = ""
    if overjet in ["Léger", "Moyen", "Important"]:
        overjet_value = st.text_input("Valeur Overjet (mm)")

    classe_angle = st.selectbox("Classe d'angle", ["Classe I", "Classe II", "Classe II div. I", "Classe II div. II", "Classe III"])
    
    # Nouvelle section RX
    st.write("### RX")
    rx_choix = st.multiselect("Choix RX", ["2 BW", "Pan", "Rétro-alvéolaire"])
    if "Rétro-alvéolaire" in rx_choix:
        retro_autre = st.text_input("Précisez les rétro-alvéolaires")
    
    # Section DPSI (Disposition spécifique)
    st.write("### DPSI (Disposition spécifique):")
    col1, col2, col3 = st.columns(3)
    with col1:
        sext1 = st.selectbox("Sext 1", ["1", "2", "3-", "3+", "4"])
    with col2:
        sext2 = st.selectbox("Sext 2", ["1", "2", "3-", "3+", "4"])
    with col3:
        sext3 = st.selectbox("Sext 3", ["1", "2", "3-", "3+", "4"])
    
    col4, col5, col6 = st.columns(3)
    with col4:
        sext6 = st.selectbox("Sext 6", ["1", "2", "3-", "3+", "4"])
    with col5:
        sext5 = st.selectbox("Sext 5", ["1", "2", "3-", "3+", "4"])
    with col6:
        sext4 = st.selectbox("Sext 4", ["1", "2", "3-", "3+", "4"])

    # Section Dépôts Dentaires
    st.write("### Dépôts dentaires")

    def add_depot_section(label):
        depot_options = ["Inexistant", "+", "++", "+++", "++++"]
        depot_choix = st.multiselect(f"{label}", depot_options, key=f"{label}_multiselect")
        details = {}
        location_choices = []

        if depot_choix and any(choice in ["+", "++", "+++", "++++"] for choice in depot_choix):
            location_options = ["Gen.", "Collet", "Préciser", "Sext"]
            location_choices = st.multiselect(f"Localisation {label}", location_options, key=f"{label}_location")

            if "Préciser" in location_choices:
                details["Préciser"] = st.text_input(f"Précision {label}", key=f"{label}_preciser")

            if "Sext" in location_choices:
                sext_options = ["1", "2", "3", "4", "5", "6"]
                details["Sext"] = st.multiselect(f"Sextants {label}", sext_options, key=f"{label}_sext")

            details["locations"] = location_choices
        return depot_choix, details

    bf_data, bf_details = add_depot_section("BF")
    tr_data, tr_details = add_depot_section("TR")
    col_data, col_details = add_depot_section("COL")
    boi_data, boi_details = add_depot_section("BOI")
    bop_data, bop_details = add_depot_section("BOP")

    ed = st.text_input("ED")
    
    q1 = st.text_input("Q1")
    q2 = st.text_input("Q2")
    q3 = st.text_input("Q3")
    q4 = st.text_input("Q4")

    # Section DHD (Diagnostic Hygiène Dentaire)
    st.write("### DHD")
    dhd = st.selectbox("Diagnostic", ["Sain", "Gingivite", "Parodontite"])
    stade = None
    grade = None

    if dhd == "Parodontite":
        col1, col2 = st.columns(2)
        with col1:
            stade = st.selectbox("Stade", ["I", "II", "III", "IV"])
        with col2:
            grade = st.selectbox("Grade", ["A", "B", "C"])
            
    # ACJ Section
    st.write("### ACJ")
    acj_options = ["ANM", "RX", "EO", "IO", "ED", "IHO", "AirFlow", "Detartrage", "Surfaçage"]
    acj_choix = st.multiselect("ACJ Options", acj_options)

    if "Detartrage" in acj_choix:
        detartrage_options = ["4Q", "Q1 et Q4", "Q2 et Q3", "Q1", "Q2", "Q3", "Q4"]
        detartrage_choix = st.multiselect("Detartrage Options", detartrage_options)
    else:
        detartrage_choix = []

    if "Surfaçage" in acj_choix:
        surfacage_options = ["4Q", "Q1 et Q4", "Q2 et Q3", "Q1", "Q2", "Q3", "Q4"]
        surfacage_choix = st.multiselect("Surfaçage Options", surfacage_options)
    else:
        surfacage_choix = []

    # Section PF (Plan de Formation)
    st.write("### PF")
    pf = st.text_input("PF")
    pf_dentiste = st.text_input("PF dentiste")
    facture = st.text_input("Facturé")

# Onglet 7 : IHO
with tab7:
    st.write("### IHO")
    technique_options = [
        "Bass", "Bass modifié", "45° Circulaire", "45° Circulaire chassé", "Rolling stroke ou Roll",
        "Stillman’s", "Charter’s", "90° Circulaire", "Appareil orthodontique 3 phases", "Brossage électrique"
    ]
    technique = st.selectbox("Technique de brossage", technique_options)
    type_brosse_options = ["Manuel", "Electrique", "Non conseillé"]
    type_brosse = st.selectbox("Conseillé de changé de méthode de brossage", type_brosse_options)
    bain_bouche = st.text_input("Bain de bouche")
    conseil_dentifrice = st.text_input("Conseil de dentifrice")

    # Espaces interdentaires
    st.write("### Espaces interdentaires")

    # Maxillaire Spaces
    st.write("#### Maxillaire")
    maxillaire_spaces = [
        "18-17", "17-16", "16-15", "15-14", "14-13", "13-12", "12-11", "11-21",
        "21-22", "22-23", "23-24", "24-25", "25-26", "26-27", "27-28"
    ]

    # Mandibulaire Spaces
    st.write("#### Mandibulaire")
    mandibulaire_spaces = [
        "48-47", "47-46", "46-45", "45-44", "44-43", "43-42", "42-41", "41-31",
        "31-32", "32-33", "33-34", "34-35", "35-36", "36-37", "37-38"
    ]

    def interdental_space_section(space_list, location):
        interdental_data = {}
        for space in space_list:
            st.write(f"##### Espace {space}")
            cleaning_methods = ["Brossettes interdentaires", "Fil dentaire", "Porte fil", "Soft pick", "Aucun"]
            selected_methods = st.multiselect(f"Méthodes pour {space}", cleaning_methods, key=f"interdental_{location}_{space}")

            method_details = []

            if "Brossettes interdentaires" in selected_methods:
                brand_options = ["Curaprox", "Interprox", "TeePee", "Gum"]
                selected_brand = st.selectbox(f"Marque Brossettes pour {space}", brand_options, key=f"brand_{location}_{space}")
                size_options = ["0.6 mm", "0.7 mm", "0.8mm", "1.1mm", "1.3mm", "1.5mm", "1.9mm", "2.2mm", "2.7mm"]
                selected_size = st.selectbox(f"Taille Brossettes pour {space}", size_options, key=f"size_{location}_{space}")
                method_details.append(f"Brossettes: {selected_brand}, {selected_size}")

            if "Soft pick" in selected_methods:
                size_options_soft_pick = ["Small", "Medium", "Large"]
                selected_size_soft_pick = st.selectbox(f"Taille Soft-Pick pour {space}", size_options_soft_pick, key=f"soft_pick_size_{location}_{space}")
                method_details.append(f"Soft pick: {selected_size_soft_pick}")

            other_methods = [method for method in selected_methods if method not in ["Brossettes interdentaires", "Soft pick"]]
            method_details.extend(other_methods)

            interdental_data[space] = ", ".join(method_details) if method_details else "Aucun"

        return interdental_data

    maxillaire_data = interdental_space_section(maxillaire_spaces, "maxillaire")
    mandibulaire_data = interdental_space_section(mandibulaire_spaces, "mandibulaire")

    # Combine the dictionaries
    all_interdental_data = {**maxillaire_data, **mandibulaire_data}

# Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Générer texte"):  # Changed button text
        data = prepare_data()
        report_text = generate_text_report(data)
        st.session_state.generated_text = report_text  # Store in session state

with col2:
    if st.button("Générer rapport PDF"):
        data = prepare_data()
        filename = f"Rapport_{nom_prenom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf" if nom_prenom else f"Rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        generate_pdf(data, filename)
        st.success(f"Rapport PDF généré : {filename}")

with col3:
    if st.button("Générer rapport Text"):
        data = prepare_data()
        report_text = generate_text_report(data)
        text_filename = f"Rapport_{nom_prenom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" if nom_prenom else f"Rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_filename, "w") as f:
            f.write(report_text)
        st.success(f"Rapport Text généré : {text_filename}")

with col4:
    if st.button("Effacer les données"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.success("Données effacées")

# Display the editable text area
if 'generated_text' in st.session_state:
    editable_text = st.text_area("Texte Modifiable", st.session_state.generated_text, height=300)  # Added text area

    # Option to save the edited text to a file
    if st.button("Sauvegarder le texte modifié"):
        modified_text_filename = f"Rapport_Modifié_{nom_prenom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" if nom_prenom else f"Rapport_Modifié_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(modified_text_filename, "w") as f:
            f.write(editable_text)
        st.success(f"Texte modifié sauvegardé : {modified_text_filename}")
