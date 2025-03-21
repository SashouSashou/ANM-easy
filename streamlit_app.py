import streamlit as st
from datetime import datetime, date, time
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import os
import requests  # Pour interagir avec l'API CBIP

# Configuration de la page
st.set_page_config(page_title="Gestion des Patients", layout="wide")

#Fonction pour générer Conseils Patients 
def generate_hygiene_pdf(data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()
    # Réduction de la taille de police pour le PDF
    style_normal = styles['Normal']
    style_normal.fontSize = 10
    style_normal.leading = 12
    style_normal.textColor = colors.black

    style_bold = ParagraphStyle(
        name='Bold',
        fontSize=12,
        leading=14,
        textColor=colors.black,
        spaceAfter=10,
        spaceBefore=10,
        bold=True
    )

    def draw_paragraph(text, x, y, bold=False):
        # Remplacer chaque "- " par un retour à la ligne suivi de "-" pour forcer le saut de ligne.
        # Utilisation de <br/> pour un meilleur rendu avec ReportLab
        text = text.replace("- ", "<br/>- ")
        style = style_bold if bold else style_normal
        p = Paragraph(text, style)
        w, h = p.wrap(width - 2 * x, y)
        if y - h < 30:
            c.showPage()
            y = height - 30
        p.drawOn(c, x, y - h)
        return y - h - 5

    y = height - 30
    y = draw_paragraph("Conseils d’hygiène bucco-dentaire dans les cabinets cabinets dentaires Bettens", 72, y, bold=True)
    y = draw_paragraph(f"Date d'aujourd'hui: {data.get('Date d\'aujourd\'hui', '')}", 72, y, bold=True)
    y = draw_paragraph(f"Nom et Prénom: {data.get('Nom et Prénom', '')}", 72, y, bold=True)
    y = draw_paragraph(f"Prochain Rendez-vous: {data.get('Prochain Rendez-vous', '')}", 72, y, bold=True)
    y = draw_paragraph(f"Praticien: {data.get('Praticien', '')}", 72, y, bold=True)

    # Section Techniques de brossage
    if data.get("IHO Technique de brossage"):
        y = draw_paragraph("Méthode de brossage adaptée à vos besoins:", 72, y, bold=True)
        technique = data.get("IHO Technique de brossage", "")
        technique_texts = {
            "Bass": """Méthode Bass
Pour un brossage optimal avec la méthode Bass, placez votre brosse à dents en l’inclinant à 45° vers la gencive. Ensuite, effectuez de petits mouvements de va-et-vient très courts, presque des vibrations, sans bouger la brosse d’une dent à l’autre. Cette technique permet aux poils de bien pénétrer sous la gencive et d’éliminer la plaque dentaire.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Appliquez la brosse sur un groupe de dents et réalisez les petites vibrations.
<br/>- Face interne : Tenez la brosse droite et réalisez le même mouvement dent par dent.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour bien éliminer les résidus alimentaires.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort afin de ne pas abîmer l’émail des dents et la gencive.""",
            "Bass modifié": """Méthode Bass modifiée
La méthode Bass modifiée suit le même principe que la méthode Bass, mais avec une étape supplémentaire. Après avoir effectué les petits mouvements vibratoires, terminez par un balayage vers le bas pour les dents du haut et vers le haut pour celles du bas. Ce geste permet de mieux éliminer la plaque dentaire et les résidus alimentaires.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Réalisez d’abord les vibrations, puis effectuez le balayage.
<br/>- Face interne : Maintenez la brosse droite et brossez chaque dent une à une.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour bien nettoyer les surfaces.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "45° Circulaire": """Méthode 45° Circulaire
Avec la méthode 45° Circulaire, placez la brosse à 45° contre la gencive et la dent. Ensuite, effectuez de petits cercles réguliers, en veillant à ne pas appuyer trop fort pour éviter d’irriter la gencive. Cette méthode est idéale pour nettoyer les espaces interdentaires.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Réalisez des cercles réguliers tout le long de l’arcade dentaire.
<br/>- Face interne : Tenez la brosse droite pour suivre la courbure des dents et effectuez les mêmes cercles.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour bien éliminer les résidus alimentaires.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "45° Circulaire chassé": """Méthode 45° Circulaire chassé
La méthode 45° Circulaire chassé commence comme la méthode 45° Circulaire, avec de petits cercles. Mais à la fin de chaque série de cercles, la brosse est légèrement tournée vers le bas ou vers le haut pour "chasser" la plaque dentaire hors des espaces interdentaires.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Réalisez des cercles suivis du mouvement de balayage.
<br/>- Face interne : Maintenez la brosse droite et appliquez la même technique.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour bien éliminer les résidus alimentaires.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "Rolling stroke ou Roll": """Méthode Rolling Stroke (ou Roll)
La méthode Rolling Stroke consiste à faire rouler la brosse sur la surface des dents. Placez-la à plat contre la gencive et la dent, puis effectuez un mouvement de rotation vers le bas pour les dents du haut et vers le haut pour celles du bas. Répétez ce mouvement plusieurs fois.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Effectuez le mouvement de roulage progressivement sur toute l’arcade.
<br/>- Face interne : Tenez la brosse droite et appliquez la même technique, dent par dent.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour éliminer les débris alimentaires.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "Stillman’s": """Méthode Stillman’s
Pour la méthode Stillman’s, tenez la brosse à 45° (légèrement inclinée) vers la gencive et appliquez une légère pression jusqu'à ce que la gencive blanchisse légèrement. Effectuez de petits mouvements de va-et-vient avec une rotation d'un quart de tour et répétez 3 à 4 fois.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Appliquez la brosse sur un groupe de dents et réalisez les petites vibrations.
<br/>- Face interne : Tenez la brosse droite et réalisez le même mouvement, dent par dent.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour éliminer les résidus.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "Charter’s": """Méthode Charter’s
La méthode Charter’s consiste à placer la brosse à 45°, avec les poils orientés vers les cuspides (pointes des dents). Appliquez une légère pression sur la gencive et la base de la dent jusqu'à ce que la gencive blanchisse légèrement, puis effectuez de petits mouvements de pression et de relâchement.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Appliquez la brosse sur un groupe de dents et réalisez les petites vibrations.
<br/>- Face interne : Tenez la brosse droite et réalisez le même mouvement, dent par dent.
<br/>- Face masticatoire : Effectuez des mouvements de va-et-vient pour éliminer les résidus.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "90° Circulaire": """Méthode 90° Circulaire
La méthode 90° Circulaire consiste à tenir la brosse perpendiculaire aux dents (90°) et à réaliser de petits cercles réguliers sur chaque dent, permettant un nettoyage efficace tout en préservant l’émail.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Réalisez des cercles réguliers sur toute l’arcade.
<br/>- Face interne : Tenez la brosse droite et effectuez les mêmes cercles.
<br/>- Face masticatoire : Réalisez des cercles pour éliminer les débris.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort.""",
            "Brossage électrique": """Brossage avec une brosse électrique
Avec une brosse électrique, placez la brosse sur chaque dent et laissez-la agir pendant 1 à 3 secondes sans bouger, puis passez à la dent suivante.
Veillez à brosser toutes les faces des dents :
<br/>- Face externe : Laissez la brosse vibrer sur chaque dent.
<br/>- Face interne : Suivez la courbe des dents.
<br/>- Face masticatoire : Laissez la brosse vibrer quelques secondes pour éliminer la plaque.
<br/>Un brossage efficace doit durer au moins deux minutes, matin et soir, en veillant à ne pas appuyer trop fort."""
        }
        y = draw_paragraph(technique_texts.get(technique, data.get("Autre technique de brossage", "")), 72, y)
        
        # Bloc pour "Conseillé de changé de méthode de brossage"
        if data.get("IHO Conseillé de changé de méthode de brossage"):
            type_brosse = data.get("IHO Conseillé de changé de méthode de brossage")
            extra_text = ""
            if type_brosse == "Electrique":
                y = draw_paragraph("Changement de brosse à dents:", 72, y, bold=True)
                extra_text = "Je vous conseille d'envisager d'acheter une brosse à dents électrique."
            elif type_brosse == "Manuel":
                y = draw_paragraph("Changement de brosse à dents:", 72, y, bold=True)
                extra_text = "Je vous conseille de retourner à une méthode de brossage manuel."
            if extra_text:
                y = draw_paragraph(extra_text, 72, y)
                
    # Section Bain de bouche
    if data.get("Bain de bouche"):
        y = draw_paragraph("Bain de bouche:", 72, y, bold=True)
        if "CHX" in data.get("Bain de bouche", ""):
            y = draw_paragraph(f"Je vous conseille d’utiliser un bain de bouche perio Aid. 0.12% trouvable en pharmacie pendant une durée limitée de {data.get('CHX - Combien de jours')}.", 72, y)
        if "O2" in data.get("Bain de bouche", ""):
            y = draw_paragraph(f"Je vous conseille d’utiliser un bain de bouche à base d’eau oxygénée trouvable en pharmacie pendant une durée limitée de {data.get('O2 - Combien de jours')}.", 72, y)
        if "Autre" in data.get("Bain de bouche", ""):
            y = draw_paragraph(data.get("Autre bain de bouche", ""), 72, y)
    
    # Section Conseil de dentifrice
    if data.get("Conseil de dentifrice"):
        y = draw_paragraph("Conseil de dentifrice:", 72, y, bold=True)
        y = draw_paragraph(data.get("Conseil de dentifrice", ""), 72, y)
    
    # Section Autre produits d'hygiène
    if data.get("Produits d'hygiène"):
        y = draw_paragraph("Autre produits d'hygiène:", 72, y, bold=True)
        hygiene_products = data.get("Produits d'hygiène")
        if hygiene_products and "Elmex Gel" in hygiene_products:
            y = draw_paragraph("L’elmex gel, trouvable en pharmacie, est à utiliser 1x par semaine après le brossage. Appliquez environ 1g sur le doigt, étalez-le sur toutes les dents et laissez agir 2 minutes avant de rincer.", 72, y)
        if hygiene_products and "Autre" in hygiene_products:
            y = draw_paragraph(data.get("Autre produits d'hygiène", ""), 72, y)
    
    # Section Espaces interdentaire
    if data.get("Espaces Interdentaires Maxillaire") or data.get("Espaces Interdentaires Mandibulaire"):
        y = draw_paragraph("Espaces interdentaire:", 72, y, bold=True)
        y = draw_paragraph("Il est conseillé d’utiliser les moyens interdentaires le soir. Voici les instructions d'utilisation selon les méthodes sélectionnées :", 72, y)
        interdental_instructions = {
            "Fil dentaire": """Utilisation du fil dentaire
Pour utiliser le fil dentaire de manière efficace, commencez par entourer environ 30 cm de fil autour de votre majeur en enroulant une petite quantité sur chaque doigt (index et pouce) pour que le fil soit tendu. Tenez-le fermement et guidez-le entre les dents. Déplacez-le sous la gencive et autour de chaque dent pour éliminer la plaque.
Effectuez des mouvements de cisaillement pour entrer et sortir entre les dents.
Utilisez-le avant le brossage, de préférence tous les soirs.""",
            "Porte fil": """Utilisation du porte-fil dentaire
Le porte-fil est une petite poignée avec un fil tendu, facilitant l'accès aux espaces difficiles. Placez le fil sous le porte-fil et tendez-le entre les dents sans le couper. Glissez-le sous la gencive en effectuant des mouvements de cisaillement.
Utilisez-le avant le brossage, de préférence tous les soirs.""",
            "Brossettes interdentaires": """Utilisation des brossettes interdentaires
Les brossettes interdentaires sont de petites brosses conçues pour nettoyer les espaces entre les dents. Choisissez une brossette de la taille appropriée à vos espaces interdentaires. Tenez-la comme un pinceau et insérez-la doucement entre les dents, en la déplaçant pour nettoyer la zone sous la gencive et autour de chaque dent. Il est recommandé de faire plusieurs aller-retours pour éliminer toute plaque ou débris.
Lors de l’insertion, utilisez des mouvements de cisaillement pour l'insérer et la retirer en douceur.
Après chaque utilisation, laissez sécher la brossette à l’air libre (sans capuchon) et remplacez-la en moyenne tous les 10 jours ou dès que les poils sont abîmés.
Utilisez-la avant le brossage, de préférence tous les soirs.""",
            "Soft pick": """Utilisation des Soft Picks
Les Soft Picks, dotés de picots en caoutchouc, permettent de nettoyer les espaces interdentaires de manière douce. Insérez délicatement un Soft Pick entre les dents et effectuez des mouvements de cisaillement pour l'introduire et le retirer sans endommager les gencives.
Utilisez-le avant le brossage, idéalement tous les soirs."""
        }
        # Extraction des moyens sélectionnés en vérifiant par mots-clés dans les espaces interdentaire
        selected_methods = set()
        maxillaire = data.get("Espaces Interdentaires Maxillaire", "").split("\n")
        mandibulaire = data.get("Espaces Interdentaires Mandibulaire", "").split("\n")
        for line in maxillaire + mandibulaire:
            lower_line = line.lower()
            if "fil dentaire" in lower_line:
                selected_methods.add("Fil dentaire")
            if "porte fil" in lower_line:
                selected_methods.add("Porte fil")
            if "brossettes" in lower_line:
                selected_methods.add("Brossettes interdentaires")
            if "soft pick" in lower_line:
                selected_methods.add("Soft pick")
        for method in selected_methods:
            if method in interdental_instructions:
                y = draw_paragraph(interdental_instructions[method], 72, y)
        for line in maxillaire:
            if line.strip():
                y = draw_paragraph(line, 72, y)
        for line in mandibulaire:
            if line.strip():
                y = draw_paragraph(line, 72, y)
                
    c.drawString(72, 40, "Les cabinets dentaires Bettens")
    c.save()


# Fonction pour calculer l'âge
def calculate_age(born):
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    st.write(f"Âge: {age}")
    return age

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
	"Âge": calculate_age(date_naissance) if date_naissance else None,
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
	"Usures dentaires": usures_details if usures_details else None,
        "Classe d'angle": classe_angle if classe_angle else None,
        "Articulé Croisé": ", ".join(articule_croise) if articule_croise else None,
        "POST Options": post_options if "POST" in articule_croise else None,
        "Autre POST Details": post_autre_details if post_options == "Autre" else None,
        "DPSI": f"{sext1}/{sext2}/{sext3} | {sext6}/{sext5}/{sext4}" if sext1 and sext2 and sext3 and sext4 and sext5 and sext6 else None,
	"Précisez les poches": precise_les_poches if precise_les_poches else None,
        "BF": format_depot_details(bf_data, bf_details),
        "TR": format_depot_details(tr_data, tr_details),
        "COL": format_depot_details(col_data, col_details),
        "BOI": format_depot_details(boi_data, boi_details),
        "BOP": format_depot_details(bop_data, bop_details),
        "ED": ed if ed else None,
	"Q1": q1_details if q1_details else None,
        "Q2": q2_details if q2_details else None,
        "Q3": q3_details if q3_details else None,
        "Q4": q4_details if q4_details else None,
        "RX": ", ".join(rx_choix) if rx_choix else None,
        "Rétro-alvéolaire": retro_autre if 'retro_autre' in locals() and retro_autre else None,
        "DHD": f"{dhd} - Stade: {stade}, Grade: {grade}" if dhd == "Parodontite" and stade and grade else dhd,
        "Justifier le diagnostique": justifier_diagnostique if justifier_diagnostique else None,
        "IHO Technique de brossage": technique if technique else None,
        "IHO Conseillé de changé de méthode de brossage": type_brosse if type_brosse else None,

	"Bain de bouche": ", ".join(bain_bouche) if bain_bouche else None,
        "CHX - Combien de jours": chx_days if "CHX" in bain_bouche and chx_days else None,
        "O2 - Combien de jours": o2_days if "O2" in bain_bouche and o2_days else None,
        "Autre bain de bouche": autre_text if "Autre" in bain_bouche and autre_text else None,
        "Conseil de dentifrice": conseil_dentifrice if conseil_dentifrice else None,
	"Produits d'hygiène": ", ".join(hygiene_products) if hygiene_products else None,
        "Autre produits d'hygiène": other_hygiene_product if "Autre" in hygiene_products and other_hygiene_product else None,
    


        "Espaces Interdentaires Maxillaire": "\n".join([f"{space}: {all_interdental_data[space]}" for space in maxillaire_spaces if space in all_interdental_data and all_interdental_data[space]]),
        "Espaces Interdentaires Mandibulaire": "\n".join([f"{space}: {all_interdental_data[space]}" for space in mandibulaire_spaces if space in all_interdental_data and all_interdental_data[space]]),
  	"ACJ": ", ".join(acj_choix) if acj_choix else None,  # Include ACJ selections
        "Detartrage Options": ", ".join(detartrage_choix) if detartrage_choix else None,  # Include Detartrage Options
        "Surfaçage Options": ", ".join(surfacage_choix) if surfacage_choix else None,
        "Autre Details": autre_details if "Autre" in acj_choix and autre_details else None,

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
    prochain_rdv_date = st.date_input("Prochain rendez-vous", value=datetime.now(), format="DD.MM.YYYY")
    
    # Use session state to preserve the selected time
    if "heure_rdv" not in st.session_state:
        st.session_state.heure_rdv = datetime.now().time()
    heure_rdv = st.time_input("Heure du prochain rendez-vous", value=st.session_state.heure_rdv)
    st.session_state.heure_rdv = heure_rdv  # Update session state

    prochain_rdv = datetime.combine(prochain_rdv_date, heure_rdv)
    date_aujourdhui = st.date_input("Date d'aujourd'hui", datetime.today())
    num_patient = st.text_input("Numéro du Patient")
    date_naissance = st.date_input("Date de Naissance", min_value=date(1900, 1, 1), max_value=date.today())
    age = calculate_age(date_naissance) if date_naissance else None
    st.write(f"Âge: {age}" if age else "")

    # Section HDD (Heure d'Arrivée)
    st.write("HDD (Heure d'Arrivée):")
    
    # Use session state to preserve the selected time
    if "hdd" not in st.session_state:
        st.session_state.hdd = datetime.now().time()
    hdd = st.time_input("Heure d'arrivée", value=st.session_state.hdd)
    st.session_state.hdd = hdd  # Update session state

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
    alim = st.selectbox("ALIM", ["0", "0 à 1", "1 à 2", "2 à 3", "3", "3 à 4", "+ de 4"])
    
    st.write("Boissons :")
    boissons = st.multiselect("Boissons", ["Eau", "Thé", "Café", "Soda"])
    if "Thé" in boissons:
        the_frequence = st.selectbox("Fréquence de Thé", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4", "+ de 4"])
    if "Café" in boissons:
        cafe_frequence = st.selectbox("Fréquence de Café", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4", "+ de 4"])
    if "Soda" in boissons:
        soda_frequence = st.selectbox("Fréquence de Soda", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4", "+ de 4"])
    
    sucre = st.selectbox("Sucre", ["0", "0 à 1", "1 à 2", "2 à 3", "3 à 4", "+ de 4"])


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

    classe_angle = st.selectbox("Classe d'angle", ["Pas examiné", "Classe I", "Classe II", "Classe II div. I", "Classe II div. II", "Classe III"])
   
# New section for articulé croisé
    articule_croise = st.multiselect("Articulé Croisé", ["ANT", "POST"])
    post_options = None
    post_autre_details = None
    if "POST" in articule_croise:
        post_options = st.selectbox("POST Options", ["Droit", "Gauche", "Bilatéral", "Autre"])
        if post_options == "Autre":
            post_autre_details = st.text_input("Précisez (Autre POST)")
    # Existing code for Onglet 6...

    # New section Usures dentaires
    st.write("### Usures dentaires")
    usures_choices = st.multiselect("Choix Usures dentaires", ["Abrasion", "Attrition", "Érosion", "Abfraction", "Autre"])

    usures_details = {}

    if "Abrasion" in usures_choices:
        abrasion_sexts = st.multiselect("Abrasion Sextants", ["Sext 1", "Sext 2", "Sext 3", "Sext 4", "Sext 5", "Sext 6", "Autre"])
        if "Autre" in abrasion_sexts:
            usures_details["Abrasion Autre"] = st.text_input("Précisez (Abrasion)")
        for sext in ["Sext 1", "Sext 2", "Sext 3"]:
            if sext in abrasion_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Colet dentaire V", "Colet dentaire P", "Autre"])
                if "Autre" in usures_details[sext]:
                    usures_details[f"{sext} Autre"] = st.text_input(f"Précisez ({sext} - Autre)")
        for sext in ["Sext 4", "Sext 5", "Sext 6"]:
            if sext in abrasion_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Colet dentaire V", "Colet dentaire L", "Autre"])
                if "Autre" in usures_details[sext]:
                    usures_details[f"{sext} Autre"] = st.text_input(f"Précisez ({sext} - Autre)")

    if "Attrition" in usures_choices:
        attrition_sexts = st.multiselect("Attrition Sextants", ["Sext 1", "Sext 2", "Sext 3", "Sext 4", "Sext 5", "Sext 6", "Autre"])
        if "Autre" in attrition_sexts:
            usures_details["Attrition Autre"] = st.text_input("Précisez (Attrition)")
        for sext in ["Sext 1", "Sext 2", "Sext 3"]:
            if sext in attrition_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Occlusales", "Bord incisif", "Autre"])
                if "Autre" in usures_details[sext]:
                    usures_details[f"{sext} Autre"] = st.text_input(f"Précisez ({sext} - Autre)")

    if "Érosion" in usures_choices:
        erosion_sexts = st.multiselect("Érosion Sextants", ["Sext 1", "Sext 2", "Sext 3", "Sext 4", "Sext 5", "Sext 6", "Autre"])
        if "Autre" in erosion_sexts:
            usures_details["Érosion Autre"] = st.text_input("Précisez (Érosion)")
        for sext in ["Sext 1", "Sext 2", "Sext 3"]:
            if sext in erosion_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Vestibulaire", "Palatin", "Autre"])
                if "Autre" in usures_details[sext]:
                    usures_details[f"{sext} Autre"] = st.text_input(f"Précisez ({sext} - Autre)")
        for sext in ["Sext 4", "Sext 5", "Sext 6"]:
            if sext in erosion_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Vestibulaire", "Lingual", "Autre"])
                if "Autre" in usures_details[sext]:
                    usures_details[f"{sext} Autre"] = st.text_input(f"Précisez ({sext} - Autre)")

    if "Abfraction" in usures_choices:
        abfraction_sexts = st.multiselect("Abfraction Sextants", ["Sext 1", "Sext 2", "Sext 3", "Sext 4", "Sext 5", "Sext 6", "Autre"])
        if "Autre" in abfraction_sexts:
            usures_details["Abfraction Autre"] = st.text_input("Précisez (Abfraction)")
        for sext in ["Sext 1", "Sext 2", "Sext 3"]:
            if sext in abfraction_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Colet", "Autre"])
                if "Colet" in usures_details[sext]:
                    usures_details[f"{sext} Colet"] = st.multiselect(f"{sext} Colet Choix", ["Vestibulaire", "Palatin", "Autre"])
                    if "Autre" in usures_details[f"{sext} Colet"]:
                        usures_details[f"{sext} Colet Autre"] = st.text_input(f"Précisez ({sext} Colet - Autre)")
        for sext in ["Sext 4", "Sext 5", "Sext 6"]:
            if sext in abfraction_sexts:
                usures_details[sext] = st.multiselect(f"{sext} Choix", ["Colet", "Autre"])
                if "Colet" in usures_details[sext]:
                    usures_details[f"{sext} Colet"] = st.multiselect(f"{sext} Colet Choix", ["Vestibulaire", "Lingual", "Autre"])
                    if "Autre" in usures_details[f"{sext} Colet"]:
                        usures_details[f"{sext} Colet Autre"] = st.text_input(f"Précisez ({sext} Colet - Autre)")

    if "Autre" in usures_choices:
        usures_details["Autre"] = st.text_input("Précisez (Autre Usures dentaires)")

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
	
	# Add new section for "précisé les poches"
    precise_les_poches = st.text_area("Précisez les poches")

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
    

        # Update Q1 input to multi-choice with cascading options
    q1_options = ["Dent manquante", "Suspicion de carie", "Déminéralisation", "Composite", "Amalgamme", "Implant", "Couronne sur dent", "Bridge", "Autre"]
    q1_choice = st.multiselect("Q1", q1_options, key="q1_multiselect")

    q1_details = {}
    if "Autre" in q1_choice:
        other_text = st.text_input("Précisez (Autre)", key="q1_autre")
        q1_details["Autre"] = other_text

    if "Dent manquante" in q1_choice:
        missing_teeth = st.multiselect("Teeth (Dent manquante)", ["18", "17", "16", "15", "14", "13", "12", "11"], key="q1_dent_manquante")
        q1_details["Dent manquante"] = missing_teeth

    if "Suspicion de carie" in q1_choice:
        carie_teeth = st.multiselect("Teeth (Suspicion de carie)", ["18", "17", "16", "15", "14", "13", "12", "11"], key="q1_suspicion_carie")
        q1_details["Suspicion de carie"] = {}
        for tooth in carie_teeth:
            carie_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q1_surface_{tooth}")
            q1_details["Suspicion de carie"][tooth] = {}
            for surface in carie_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q1_precision_{tooth}_{surface}")
                    q1_details["Suspicion de carie"][tooth][surface] = precision_text
                else:
                    q1_details["Suspicion de carie"][tooth][surface] = "Non"
            verify_dentist = st.radio(f"Vérifier par le dentiste (Suspicion de carie) pour {tooth}", ["Oui", "Non"], key=f"q1_verify_{tooth}")
            q1_details["Suspicion de carie"][tooth]["Vérifier par le dentiste"] = verify_dentist

    if "Déminéralisation" in q1_choice:
        demin_teeth = st.multiselect("Teeth (Déminéralisation)", ["18", "17", "16", "15", "14", "13", "12", "11"], key="q1_demineralisation")
        q1_details["Déminéralisation"] = {}
        for tooth in demin_teeth:
            demin_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q1_demin_surfaces_{tooth}")
            q1_details["Déminéralisation"][tooth] = {}
            for surface in demin_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q1_demin_precision_{tooth}_{surface}")
                    q1_details["Déminéralisation"][tooth][surface] = precision_text
                else:
                    q1_details["Déminéralisation"][tooth][surface] = "Non"

    if "Composite" in q1_choice:
        composite_teeth = st.multiselect("Teeth (Composite)", ["18", "17", "16", "15", "14", "13", "12", "11"], key="q1_composite")
        q1_details["Composite"] = {}
        for tooth in composite_teeth:
            composite_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q1_composite_surfaces_{tooth}")
            q1_details["Composite"][tooth] = {}
            for surface in composite_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q1_composite_precision_{tooth}_{surface}")
                    q1_details["Composite"][tooth][surface] = precision_text
                else:
                    q1_details["Composite"][tooth][surface] = "Non"

    if "Amalgamme" in q1_choice:
        amalgamme_teeth = st.multiselect("Teeth (Amalgamme)", ["18", "17", "16", "15", "14", "13", "12", "11"], key="q1_amalgamme")
        q1_details["Amalgamme"] = {}
        for tooth in amalgamme_teeth:
            amalgamme_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q1_amalgamme_surfaces_{tooth}")
            q1_details["Amalgamme"][tooth] = {}
            for surface in amalgamme_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q1_amalgamme_precision_{tooth}_{surface}")
                    q1_details["Amalgamme"][tooth][surface] = precision_text
                else:
                    q1_details["Amalgamme"][tooth][surface] = "Non"
           
       
    if "Implant" in q1_choice:
        implant_teeth = st.multiselect("Teeth (Implant)", ["18", "17", "16", "15", "14", "13", "12", "11"])
        q1_details["Implant"] = {}
        for tooth in implant_teeth:
            implant_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if implant_state == "Risque":
                implant_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"implant_risk_{tooth}")
                q1_details["Implant"][tooth] = {"État": implant_state, "Risque": implant_risk_text}
            else:
                q1_details["Implant"][tooth] = {"État": implant_state}

    if "Couronne sur dent" in q1_choice:
        couronne_teeth = st.multiselect("Teeth (Couronne sur dent)", ["18", "17", "16", "15", "14", "13", "12", "11"])
        q1_details["Couronne sur dent"] = {}
        for tooth in couronne_teeth:
            couronne_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if couronne_state == "Risque":
                couronne_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"couronne_risk_{tooth}")
                q1_details["Couronne sur dent"][tooth] = {"État": couronne_state, "Risque": couronne_risk_text}
            else:
                q1_details["Couronne sur dent"][tooth] = {"État": couronne_state}

    if "Bridge" in q1_choice:
        bridge_teeth = st.multiselect("Teeth (Bridge)", ["18", "17", "16", "15", "14", "13", "12", "11"])
        q1_details["Bridge"] = {}
        for tooth in bridge_teeth:
            bridge_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if bridge_state == "Risque":
                bridge_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"bridge_risk_{tooth}")
                q1_details["Bridge"][tooth] = {"État": bridge_state, "Risque": bridge_risk_text}
            else:
                q1_details["Bridge"][tooth] = {"État": bridge_state}

    # Update Q2 input to multi-choice with cascading options
    q2_choice = st.multiselect("Q2", q1_options, key="q2_multiselect")

    q2_details = {}
    if "Autre" in q2_choice:
        other_text = st.text_input("Précisez (Autre Q2)", key="q2_autre")
        q2_details["Autre"] = other_text

    if "Dent manquante" in q2_choice:
        missing_teeth = st.multiselect("Teeth (Dent manquante)", ["28", "27", "26", "25", "24", "23", "22", "21"], key="q2_dent_manquante")
        q2_details["Dent manquante"] = missing_teeth

    if "Suspicion de carie" in q2_choice:
        carie_teeth = st.multiselect("Teeth (Suspicion de carie)", ["28", "27", "26", "25", "24", "23", "22", "21"], key="q2_suspicion_carie")
        q2_details["Suspicion de carie"] = {}
        for tooth in carie_teeth:
            carie_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q2_surface_{tooth}")
            q2_details["Suspicion de carie"][tooth] = {}
            for surface in carie_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q2_precision_{tooth}_{surface}")
                    q2_details["Suspicion de carie"][tooth][surface] = precision_text
                else:
                    q2_details["Suspicion de carie"][tooth][surface] = "Non"
            verify_dentist = st.radio(f"Vérifier par le dentiste (Suspicion de carie) pour {tooth}", ["Oui", "Non"], key=f"q2_verify_{tooth}")
            q2_details["Suspicion de carie"][tooth]["Vérifier par le dentiste"] = verify_dentist

    if "Déminéralisation" in q2_choice:
        demin_teeth = st.multiselect("Teeth (Déminéralisation)", ["28", "27", "26", "25", "24", "23", "22", "21"], key="q2_demineralisation")
        q2_details["Déminéralisation"] = {}
        for tooth in demin_teeth:
            demin_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q2_demin_surfaces_{tooth}")
            q2_details["Déminéralisation"][tooth] = {}
            for surface in demin_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q2_demin_precision_{tooth}_{surface}")
                    q2_details["Déminéralisation"][tooth][surface] = precision_text
                else:
                    q2_details["Déminéralisation"][tooth][surface] = "Non"

    if "Composite" in q2_choice:
        composite_teeth = st.multiselect("Teeth (Composite)", ["28", "27", "26", "25", "24", "23", "22", "21"], key="q2_composite")
        q2_details["Composite"] = {}
        for tooth in composite_teeth:
            composite_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q2_composite_surfaces_{tooth}")
            q2_details["Composite"][tooth] = {}
            for surface in composite_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q2_composite_precision_{tooth}_{surface}")
                    q2_details["Composite"][tooth][surface] = precision_text
                else:
                    q2_details["Composite"][tooth][surface] = "Non"

    if "Amalgamme" in q2_choice:
        amalgamme_teeth = st.multiselect("Teeth (Amalgamme)", ["28", "27", "26", "25", "24", "23", "22", "21"], key="q2_amalgamme")
        q2_details["Amalgamme"] = {}
        for tooth in amalgamme_teeth:
            amalgamme_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "P", "Collet", "Préciser"], key=f"q2_amalgamme_surfaces_{tooth}")
            q2_details["Amalgamme"][tooth] = {}
            for surface in amalgamme_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q2_amalgamme_precision_{tooth}_{surface}")
                    q2_details["Amalgamme"][tooth][surface] = precision_text
                else:
                    q2_details["Amalgamme"][tooth][surface] = "Non"
      

    if "Implant" in q2_choice:
        implant_teeth = st.multiselect("Teeth (Implant)", ["28", "27", "26", "25", "24", "23", "22", "21"])
        q2_details["Implant"] = {}
        for tooth in implant_teeth:
            implant_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if implant_state == "Risque":
                implant_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q2_implant_risk_{tooth}")
                q2_details["Implant"][tooth] = {"État": implant_state, "Risque": implant_risk_text}
            else:
                q2_details["Implant"][tooth] = {"État": implant_state}

    if "Couronne sur dent" in q2_choice:
        couronne_teeth = st.multiselect("Teeth (Couronne sur dent)", ["28", "27", "26", "25", "24", "23", "22", "21"])
        q2_details["Couronne sur dent"] = {}
        for tooth in couronne_teeth:
            couronne_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if couronne_state == "Risque":
                couronne_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q2_couronne_risk_{tooth}")
                q2_details["Couronne sur dent"][tooth] = {"État": couronne_state, "Risque": couronne_risk_text}
            else:
                q2_details["Couronne sur dent"][tooth] = {"État": couronne_state}

    if "Bridge" in q2_choice:
        bridge_teeth = st.multiselect("Teeth (Bridge)", ["28", "27", "26", "25", "24", "23", "22", "21"])
        q2_details["Bridge"] = {}
        for tooth in bridge_teeth:
            bridge_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if bridge_state == "Risque":
                bridge_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q2_bridge_risk_{tooth}")
                q2_details["Bridge"][tooth] = {"État": bridge_state, "Risque": bridge_risk_text}
            else:
                q2_details["Bridge"][tooth] = {"État": bridge_state}



        # Update Q3 input to multi-choice with cascading options
    q3_choice = st.multiselect("Q3", q1_options, key="q3_multiselect")

    q3_details = {}
    if "Autre" in q3_choice:
        other_text = st.text_input("Précisez (Autre Q3)", key="q3_autre")
        q3_details["Autre"] = other_text

    if "Dent manquante" in q3_choice:
        missing_teeth = st.multiselect("Teeth (Dent manquante)", ["38", "37", "36", "35", "34", "33", "32", "31"], key="q3_dent_manquante")
        q3_details["Dent manquante"] = missing_teeth

    if "Suspicion de carie" in q3_choice:
        carie_teeth = st.multiselect("Teeth (Suspicion de carie)", ["38", "37", "36", "35", "34", "33", "32", "31"], key="q3_suspicion_carie")
        q3_details["Suspicion de carie"] = {}
        for tooth in carie_teeth:
            carie_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q3_surface_{tooth}")
            q3_details["Suspicion de carie"][tooth] = {}
            for surface in carie_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q3_precision_{tooth}_{surface}")
                    q3_details["Suspicion de carie"][tooth][surface] = precision_text
                else:
                    q3_details["Suspicion de carie"][tooth][surface] = "Non"
            verify_dentist = st.radio(f"Vérifier par le dentiste (Suspicion de carie) pour {tooth}", ["Oui", "Non"], key=f"q3_verify_{tooth}")
            q3_details["Suspicion de carie"][tooth]["Vérifier par le dentiste"] = verify_dentist

    if "Déminéralisation" in q3_choice:
        demin_teeth = st.multiselect("Teeth (Déminéralisation)", ["38", "37", "36", "35", "34", "33", "32", "31"], key="q3_demineralisation")
        q3_details["Déminéralisation"] = {}
        for tooth in demin_teeth:
            demin_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q3_demin_surfaces_{tooth}")
            q3_details["Déminéralisation"][tooth] = {}
            for surface in demin_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q3_demin_precision_{tooth}_{surface}")
                    q3_details["Déminéralisation"][tooth][surface] = precision_text
                else:
                    q3_details["Déminéralisation"][tooth][surface] = "Non"

    if "Composite" in q3_choice:
        composite_teeth = st.multiselect("Teeth (Composite)", ["38", "37", "36", "35", "34", "33", "32", "31"], key="q3_composite")
        q3_details["Composite"] = {}
        for tooth in composite_teeth:
            composite_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q3_composite_surfaces_{tooth}")
            q3_details["Composite"][tooth] = {}
            for surface in composite_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q3_composite_precision_{tooth}_{surface}")
                    q3_details["Composite"][tooth][surface] = precision_text
                else:
                    q3_details["Composite"][tooth][surface] = "Non"

    if "Amalgamme" in q3_choice:
        amalgamme_teeth = st.multiselect("Teeth (Amalgamme)", ["38", "37", "36", "35", "34", "33", "32", "31"], key="q3_amalgamme")
        q3_details["Amalgamme"] = {}
        for tooth in amalgamme_teeth:
            amalgamme_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q3_amalgamme_surfaces_{tooth}")
            q3_details["Amalgamme"][tooth] = {}
            for surface in amalgamme_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q3_amalgamme_precision_{tooth}_{surface}")
                    q3_details["Amalgamme"][tooth][surface] = precision_text
                else:
                    q3_details["Amalgamme"][tooth][surface] = "Non"

    if "Implant" in q3_choice:
        implant_teeth = st.multiselect("Teeth (Implant)", ["38", "37", "36", "35", "34", "33", "32", "31"])
        q3_details["Implant"] = {}
        for tooth in implant_teeth:
            implant_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if implant_state == "Risque":
                implant_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q3_implant_risk_{tooth}")
                q3_details["Implant"][tooth] = {"État": implant_state, "Risque": implant_risk_text}
            else:
                q3_details["Implant"][tooth] = {"État": implant_state}

    if "Couronne sur dent" in q3_choice:
        couronne_teeth = st.multiselect("Teeth (Couronne sur dent)", ["38", "37", "36", "35", "34", "33", "32", "31"])
        q3_details["Couronne sur dent"] = {}
        for tooth in couronne_teeth:
            couronne_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if couronne_state == "Risque":
                couronne_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q3_couronne_risk_{tooth}")
                q3_details["Couronne sur dent"][tooth] = {"État": couronne_state, "Risque": couronne_risk_text}
            else:
                q3_details["Couronne sur dent"][tooth] = {"État": couronne_state}

    if "Bridge" in q3_choice:
        bridge_teeth = st.multiselect("Teeth (Bridge)", ["38", "37", "36", "35", "34", "33", "32", "31"])
        q3_details["Bridge"] = {}
        for tooth in bridge_teeth:
            bridge_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if bridge_state == "Risque":
                bridge_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q3_bridge_risk_{tooth}")
                q3_details["Bridge"][tooth] = {"État": bridge_state, "Risque": bridge_risk_text}
            else:
                q3_details["Bridge"][tooth] = {"État": bridge_state}



        # Update Q4 input to multi-choice with cascading options
    q4_choice = st.multiselect("Q4", q1_options, key="q4_multiselect")

    q4_details = {}
    if "Autre" in q4_choice:
        other_text = st.text_input("Précisez (Autre Q4)", key="q4_autre")
        q4_details["Autre"] = other_text

    if "Dent manquante" in q4_choice:
        missing_teeth = st.multiselect("Teeth (Dent manquante)", ["48", "47", "46", "45", "44", "43", "42", "41"], key="q4_dent_manquante")
        q4_details["Dent manquante"] = missing_teeth

    if "Suspicion de carie" in q4_choice:
        carie_teeth = st.multiselect("Teeth (Suspicion de carie)", ["48", "47", "46", "45", "44", "43", "42", "41"], key="q4_suspicion_carie")
        q4_details["Suspicion de carie"] = {}
        for tooth in carie_teeth:
            carie_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q4_surface_{tooth}")
            q4_details["Suspicion de carie"][tooth] = {}
            for surface in carie_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q4_precision_{tooth}_{surface}")
                    q4_details["Suspicion de carie"][tooth][surface] = precision_text
                else:
                    q4_details["Suspicion de carie"][tooth][surface] = "Non"
            verify_dentist = st.radio(f"Vérifier par le dentiste (Suspicion de carie) pour {tooth}", ["Oui", "Non"], key=f"q4_verify_{tooth}")
            q4_details["Suspicion de carie"][tooth]["Vérifier par le dentiste"] = verify_dentist

    if "Déminéralisation" in q4_choice:
        demin_teeth = st.multiselect("Teeth (Déminéralisation)", ["48", "47", "46", "45", "44", "43", "42", "41"], key="q4_demineralisation")
        q4_details["Déminéralisation"] = {}
        for tooth in demin_teeth:
            demin_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q4_demin_surfaces_{tooth}")
            q4_details["Déminéralisation"][tooth] = {}
            for surface in demin_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q4_demin_precision_{tooth}_{surface}")
                    q4_details["Déminéralisation"][tooth][surface] = precision_text
                else:
                    q4_details["Déminéralisation"][tooth][surface] = "Non"

    if "Composite" in q4_choice:
        composite_teeth = st.multiselect("Teeth (Composite)", ["48", "47", "46", "45", "44", "43", "42", "41"], key="q4_composite")
        q4_details["Composite"] = {}
        for tooth in composite_teeth:
            composite_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q4_composite_surfaces_{tooth}")
            q4_details["Composite"][tooth] = {}
            for surface in composite_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q4_composite_precision_{tooth}_{surface}")
                    q4_details["Composite"][tooth][surface] = precision_text
                else:
                    q4_details["Composite"][tooth][surface] = "Non"

    if "Amalgamme" in q4_choice:
        amalgamme_teeth = st.multiselect("Teeth (Amalgamme)", ["48", "47", "46", "45", "44", "43", "42", "41"], key="q4_amalgamme")
        q4_details["Amalgamme"] = {}
        for tooth in amalgamme_teeth:
            amalgamme_surfaces = st.multiselect(f"Surfaces for {tooth}", ["M", "D", "V", "O", "L", "Collet", "Préciser"], key=f"q4_amalgamme_surfaces_{tooth}")
            q4_details["Amalgamme"][tooth] = {}
            for surface in amalgamme_surfaces:
                if surface == "Préciser":
                    precision_text = st.text_input(f"Précision for {surface} {tooth}", key=f"q4_amalgamme_precision_{tooth}_{surface}")
                    q4_details["Amalgamme"][tooth][surface] = precision_text
                else:
                    q4_details["Amalgamme"][tooth][surface] = "Non"
       
     
    if "Implant" in q4_choice:
        implant_teeth = st.multiselect("Teeth (Implant)", ["48", "47", "46", "45", "44", "43", "42", "41"])
        q4_details["Implant"] = {}
        for tooth in implant_teeth:
            implant_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if implant_state == "Risque":
                implant_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q4_implant_risk_{tooth}")
                q4_details["Implant"][tooth] = {"État": implant_state, "Risque": implant_risk_text}
            else:
                q4_details["Implant"][tooth] = {"État": implant_state}

    if "Couronne sur dent" in q4_choice:
        couronne_teeth = st.multiselect("Teeth (Couronne sur dent)", ["48", "47", "46", "45", "44", "43", "42", "41"])
        q4_details["Couronne sur dent"] = {}
        for tooth in couronne_teeth:
            couronne_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if couronne_state == "Risque":
                couronne_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q4_couronne_risk_{tooth}")
                q4_details["Couronne sur dent"][tooth] = {"État": couronne_state, "Risque": couronne_risk_text}
            else:
                q4_details["Couronne sur dent"][tooth] = {"État": couronne_state}

    if "Bridge" in q4_choice:
        bridge_teeth = st.multiselect("Teeth (Bridge)", ["48", "47", "46", "45", "44", "43", "42", "41"])
        q4_details["Bridge"] = {}
        for tooth in bridge_teeth:
            bridge_state = st.selectbox(f"État for {tooth}", ["OK", "Risque"])
            if bridge_state == "Risque":
                bridge_risk_text = st.text_input(f"Précisez le risque for {tooth}", key=f"q4_bridge_risk_{tooth}")
                q4_details["Bridge"][tooth] = {"État": bridge_state, "Risque": bridge_risk_text}
            else:
                q4_details["Bridge"][tooth] = {"État": bridge_state}

     # Section DHD (Diagnostic Hygiène Dentaire)
    st.write("### DHD")
    dhd = st.selectbox("Diagnostic", ["Sain", "Gingivite", "Parodontite"])
    stade = None
    grade = None
    justifier_diagnostique = None  # Initialize the variable

    if dhd == "Parodontite":
        col1, col2 = st.columns(2)
        with col1:
              stade = st.selectbox("Stade", ["I", "II", "III", "IV"])
        with col2:
              grade = st.selectbox("Grade", ["A", "B", "C"])
        justifier_diagnostique = st.text_area("Justifier le diagnostique")


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

    # PF Section
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
    technique = st.selectbox("Technique de brossage", [""] + technique_options, index=0, format_func=lambda x: 'Sélectionner' if x == '' else x)

    if technique == "Bass":
        st.write("Recommandée pour nettoyage bord marginal avec présence importante de biofilm. Lors de parodontite et présence espaces interdentaires importants.")
    elif technique == "Bass modifié":
        st.write("Recommandée idem Bass mais avec présence de biofilm sur le reste de la couronne.")
    elif technique == "45° Circulaire":
        st.write("Recommandée lors de présence de biofilm au bord marginal et patient avec plus faible dextérité.")
    elif technique == "45° Circulaire chassé":
        st.write("Recommandée lors de présence de biofilm au bord marginal + sur la couronne et patient avec plus faible dextérité.")
    elif technique == "Rolling stroke ou Roll":
        st.write("Recommandée lors de retraits importants de gencive et /ou peu de gencive attachée et une table osseuse fine.")
    elif technique == "Stillman’s":
        st.write("Recommandée pour masser et stimuler les gencives et nettoyer les zones cervicales avec efficacité mais à minimiser les traumatismes gingivaux. Cette méthode nécessite de la dextérité.")
    elif technique == "Charter’s":
        st.write("Recommandé pour le massage de la gencive / lors de la présence de brackets.")
    elif technique == "90° Circulaire":
        st.write("Recommandée pour les patients à faible dextérité.")
    elif technique == "Brossage électrique":
        st.write("Recommandée pour les patients à faible dextérité.")
    elif technique == "Autre":
        autre_technique = st.text_input("Précisez la technique de brossage")

    type_brosse_options = ["Manuel", "Electrique", "Non conseillé"]
    type_brosse = st.selectbox("Conseillé de changé de méthode de brossage", type_brosse_options)

    bain_bouche = st.multiselect("Bain de bouche", ["CHX", "O2", "Autre"], default=[])

    chx_days = None
    o2_days = None
    autre_text = None

    if "CHX" in bain_bouche:
        chx_days = st.selectbox("CHX - Combien de jours ?", ["3j", "7j", "14j"])

    if "O2" in bain_bouche:
        o2_days = st.selectbox("O2 - Combien de jours ?", ["3j", "7j", "14j"])

    if "Autre" in bain_bouche:
        autre_text = st.text_input("Précisez")

    conseil_dentifrice = st.text_input("Conseil de dentifrice")

    # New section for "Autre produits d'hygiène"
    st.write("### Autre produits d'hygiène")
    hygiene_products = st.multiselect("Choix produits d'hygiène", ["Elmex Gel", "Autre"], default=[])
    other_hygiene_product = None
    if "Autre" in hygiene_products:
        other_hygiene_product = st.text_input("Précisez (Autre produits d'hygiène)")

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
                brand_options = ["Curaprox", "Interprox", "TePe", "Gum"]
                selected_brand = st.selectbox(f"Marque Brossettes pour {space}", brand_options, key=f"brand_{location}_{space}")
                size_options = ["0.6 mm", "0.7 mm", "0.8mm", "O.9mm", "1.1mm", "1.3mm", "1.5mm", "1.9mm", "2.2mm", "2.7mm"]
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
    if st.button("Générer conseils d'hygiène"):
        data = prepare_data()
        filename = f"Conseils_Hygiene_{nom_prenom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf" if nom_prenom else f"Conseils_Hygiene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        generate_hygiene_pdf(data, filename)
        st.success(f"Document PDF généré : {filename}")

# Display the editable text area
if 'generated_text' in st.session_state:
    editable_text = st.text_area("Texte Modifiable", st.session_state.generated_text, height=500)  # Added text area

    # Option to save the edited text to a file
    if st.button("Sauvegarder le texte modifié"):
        modified_text_filename = f"Rapport_Modifié_{nom_prenom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" if nom_prenom else f"Rapport_Modifié_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(modified_text_filename, "w") as f:
            f.write(editable_text)
        st.success(f"Texte modifié sauvegardé : {modified_text_filename}")
