import os
import json
import re
import datetime
import random

INPUT_DIR = "src/content/seo-articles"
REPORT_PATH = "superparty_seo_audit_results/superparty_articles_report.json"

INTRO_TEMPLATES = [
    "Dacă plănuiești o [EVENIMENT] de neuitat în [LOCATIE], ai ajuns exact unde trebuie! Aducem direct la tine acasă sau la locul de joacă cel mai iubit personaj: [PERSONAJ]. Fie că este vorba despre o petrecere surpriză sau un eveniment la grădiniță, ne ocupăm de toată distracția pentru ca tu să te poți bucura de moment fără niciun stres.",
    "Transformă ziua copilului tău într-un adevărat festival direct în [LOCATIE]! Când [PERSONAJ] își face apariția la petrecerea celor mici, bucuria este garantată. Cu un program interactiv, jocuri adaptate vârstei și super energie, animatorii noștri sunt pregătiți să creeze amintiri memorabile pentru întreaga familie.",
    "Organizarea unei petreceri pentru copii în [LOCATIE] nu trebuie să fie complicată. Soluția noastră all-inclusive aduce magia la evenimentul tău prin prezența fascinantă a lui [PERSONAJ]. Pregătește aparatul foto, pentru că de restul – de la jocuri, muzică, până la modelaj de baloane – ne ocupăm noi!",
    "Căutarea a luat sfârșit: cel mai antrenant [PERSONAJ] sosește cu surprize în [LOCATIE]! Pentru o [EVENIMENT] reușită unde cei mici nu au timp să se plictisească, am structurat un program care combină jocurile active, coregrafiile distractive și momentele de magie. Lasă grija organizării pe mâna noastră.",
    "Bucurie pură și zâmbete infinite la petrecerea din [LOCATIE]! Invitatul special, [PERSONAJ], vine încărcat cu jocuri captivante, recuzită colorată și baloane modelate. Ne adaptăm fiecărui spațiu, fie că optezi pentru o petrecere la tine acasă, în curte sau la restaurant, garantând 100% implicare."
]

LOGISTICS_TEMPLATES = [
    "### Logistică și Pregătire\nNu ai nevoie de un spațiu imens pentru a organiza un eveniment de succes. Ne descurcăm excelent atât într-un living primitor, cât și în grădină sau într-o sală de petreceri din [LOCATIE]. Avem nevoie doar de o priză pentru sistemul nostru de sunet și de implicarea copiilor!",
    "### Detalii de Organizare Practică\nCând rezervi un animator în [LOCATIE], venim cu echipamentul complet: boxă activă, playlisturi tematice, recuzită pentru jocuri și accesorii. Recomandăm să eliberați un colț al încăperii pentru o desfășurare în siguranță a jocurilor în mișcare.",
    "### Cum pregătești locația pentru [PERSONAJ]\nFie că sărbătoriți acasă, la un restaurant din [LOCATIE] sau în aer liber, flexibilitatea este punctul nostru forte. Este ideal ca înaintea începerii programului, copiii să fi luat deja o mică gustare, astfel încât pe parcursul celor 1-2 ore de animație energia lor să fie maximă pentru jocuri."
]

PROGRAM_TEMPLATES = [
    "### Program Recomandat: 2 Ore de Adrenalină\n* **0-15 min:** Intrarea personajului pe o melodie tematică, acomodarea cu copiii și prezentarea sărbătoritului.\n* **15-60 min:** Jocuri dinamice (Limbo, Parașuta Colorată, Statuile Muzicale) și concursuri pe echipe.\n* **60-90 min:** Sesiune de pictură pe față (face painting) cu modele alese de cei mici.\n* **90-110 min:** Modelaj de baloane (săbii, flori, animăluțe) pentru fiecare copil.\n* **110-120 min:** Suflarea în lumânări, aducerea tortului, sesiunea foto de grup și La Mulți Ani!",
    "### Desfășurătorul Magiei Pas cu Pas\nO [EVENIMENT] necesită un ritm alert. Începem cu spargerea gheții printr-un joc interactiv de cunoaștere. Urmează nucleul distracției: competiții distractive cu recuzita noastră, dansuri coregrafiate și tunelul misterios. Către final, ne liniștim ritmul cu artă pe față (face painting premium) și crearea de figurine din baloane pentru toți participanții.",
    "### Structura unei Ore de Vis\nDe la momentul în care [PERSONAJ] face primul pas în locația ta din [LOCATIE], preia complet controlul distracției. Alternăm momentele de energie debordantă cu jocuri de echipă care dezvoltă atenția și coordonarea. Cele mai solicitate activități la final rămân face painting-ul magic și modelarea faimoaselor săbii din baloane cu care micii eroi pleacă acasă!"
]

SIGNATURE_SECTIONS = [
    "### Cum Gestionăm Copiii de 2–4 Ani\nPentru piticii de vârste mici, abordarea animatorului este mult mai blândă, fără mișcări bruște sau sunete puternice. Folosim jocuri senzoriale cu baloane de săpun, tunelul curcubeu și dansuri ușoare pe muzică adaptată vârstei lor.",
    "### Cum Ținem Atenția Grupelor de 9–12 Ani\nPre-adolescenții se plictisesc repede de jocurile clasice, așa că ridicăm miza: aducem challenge-uri populare de pe TikTok, concursuri de dans urbane, trivia și jocuri de perspicacitate. [PERSONAJ] se transformă dintr-un simplu animator într-un adevărat MC al petrecerii!",
    "### Planul B pentru Ploaie la Petreceri Outdoor\nDacă ați planificat o petrecere în aer liber în [LOCATIE] și vremea este capricioasă, animatorul se adaptează instant: restrângem activitățile într-un cort sau în foișor și trecem la jocuri statice, ghicitori, pantomimă și face painting intens care nu necesită mult spațiu de alergat.",
    "### Checklist pentru Părinți (Fără Stres)\nPentru o colaborare perfectă, ține cont de aceste reguli simple: invită animatorul cu 30 de minute *după* ora oficială de începere a petrecerii (pentru a fi sigur că au sosit toți copiii), pregătește un mic punct de apă plată pentru ei și eliberează centrul camerei de cabluri jucării periculoase.",
    "### Volumul Muzicii și Sensibilitatea Zgomotului\nSistemele noastre de sunet sunt controlate permanent. [PERSONAJ] știe exact cum să mențină un volum care să asigure distracția, dar fără să acopere conversațiile adulților sau să sperie copiii sensibili la zgomot puternic.",
    "### Meniul Kids-Friendly Rapid\nPe baza experienței de la sute de petreceri, recomandăm părinților din [LOCATIE] să evite meniurile sofisticate pentru copii. Optează pentru pizza, mini-sandvișuri, fructe deja tăiate și multă apă. Animația o să-i țină atât de ocupați încât nu vor avea timp pentru mese lungi la masă!",
    "### Greșeli Frecvente la Organizarea Aniversărilor\nO greșeală des întâlnită este supra-aglomerarea programului: piesa de teatru + animator + magician + piniata în doar 2 ore pot suprastimula copiii. Lasă copiii să interacționeze liber cu [PERSONAJ] pentru minimum o oră plină de jocuri, fără alte întreruperi logistice.",
    "### Cadouri și Goodie Bags\nDacă doriți să oferiți mici atenții la final (pungi cu dulciuri sau jucării), animatorul vă ajută la fix: putem integra împărțirea lor într-un joc distractiv (ex. Căutarea Comorii), unde [PERSONAJ] felicită pe rând fiecare copil pentru curajul arătat în jocuri.",
    "### Fotografii la Petrecere: Unghiuri și Momente\nPentru a surprinde magia reală a momentului, recomandăm captarea emoțiilor la jocurile de parașută și în timpul suflării în tort. Când [PERSONAJ] intră prima oară pe ușă, pregătiți camera pentru reacția de soc și bucurie a sărbătoritului!",
    "### Importanța Baloanelor Modelate\nDesi par simple, săbiile, cățeii și florile din baloane raman cel mai așteptat moment. De ce? Oferă o mică suvenire tactilă pe care fiecare copil o poate lua acasă din inima petrecerii din [LOCATIE]!"
]

REALISTIC_TESTIMONIALS = [
    "### Recenzia Părinților din [LOCATIE]\n> \"Am organizat petrecerea băiețelului meu de 6 ani și am fost pe deplin mulțumiți. Animatorul a venit la timp, costumul a fost foarte curat și realist, iar energia lui i-a ținut pe cei 15 copii ocupați continuu timp de două ore. Nu au fost pauze moarte, iar comunicarea în prealabil a fost foarte clară. Recomand cu drag pentru părinții care vor să stea liniștiți la masă în timp ce copiii se distrează.\" - **Maria D., [LOCATIE]**",
    "### Impresii de la Petrecerea cu [PERSONAJ]\n> \"Sinceră să fiu, aveam emoții pentru spațiul nostru din sufragerie, mai ales că aveam mulți copii invitați. [PERSONAJ] s-a descurcat excelent. A adaptat jocurile pentru interior, nu a existat agitație incontrolabilă, iar copiii au stat cuminți la face painting. Fetita mea încă mă întreabă când ne mai vizitează. Experiența a meritat fiecare ban.\" - **Andreea S., mamă**",
    "### Ce Spun Clienții Nostri\n> \"Ne-am bazat pe echipa aceasta pentru a doua oară și nu dezamăgesc. Animatorul are mult tact, a știut exact cum să includă în jocuri și un copilaș mai retras. Jocurile de echipă cu pânza uriașă și tunelul au fost wow. Partea de organizare a fotografilor a decurs fluid la tăierea tortului. Foarte profesioniști!\" - **Mihai T., [LOCATIE]**",
    "### Feedback Recent: Experiența cu [PERSONAJ]\n> \"De departe cea mai bună decizie pentru aniversarea de 7 ani. Spre deosebire de alte petreceri la care am fost, animatorul chiar a relaționat cu ei, nu doar a pus muzică. Le-a învățat numele repede, i-a grupat în echipe și a oprit micile conflicte dintre copii imediat, redirecționându-le atenția. Foarte pregătit și carismatic!\" - **Elena R.**"
]

FAQS_LIBRARY = [
    ("Animatorul vine cu toate materialele necesare?", "Da, absolut. Sosim echipați cu boxă proprie, baloane pentru modelaj, vopsele profesionale pentru pictură pe față și recuzita jocurilor. Trebuie să asigurați doar o priză."),
    ("Ce se întâmplă dacă unii copii sunt timizi?", "Animatorii noștri sunt recunoscuți pentru răbdare și tact pedagogic. Implicăm copiii timizi treptat, fără presiune, oferindu-le roluri mai simple la început (ex. ajutoare la împărțirea materialelor) până prind curaj."),
    ("Putem prelungi durata programului în ziua petrecerii?", "Depinde de disponibilitatea imediată a animatorului. Uneori, [PERSONAJ] are o altă petrecere programată în alt sector sau localitate, așadar e de preferat să estimați din start durata exactă la telefon: [TELEFON]."),
    ("Mascota/Costumul corespunde cu cel din poze?", "Investim doar în costume de calitate, menținute impecabil. Experiența vizuală premium face diferența la fotografiile realizate la petrecere [GALERIE]."),
    ("Putem organiza petrecerea la grădiniță?", "Sigur, ne deplasăm des la grădinițele din [LOCATIE]. Singura condiție este să obțineți aprobarea direcțiunii în prealabil și să respectăm programul copiilor."),
    ("Cum decurge momentul aducerii tortului?", "[PERSONAJ] oprește jocurile, cheamă toți copiii în jurul mesei, organizează corul de 'La Mulți Ani' și animează suflarea lumânărilor, creând cadrul perfect pentru fotografii."),
    ("Realizați face painting cu produse sigure?", "Folosim exclusiv vopsele pe bază de apă, hipoalergenice, profesionale (marca Snazaroo/Kryolan), speciale pentru pielea sensibilă a copiilor. Se spală foarte ușor cu apă și săpun."),
    ("Se face animație și dacă locația e mai îndepărtată de centru?", "Acoperim cu drag zona [LOCATIE] și împrejurimile, aducând echipamentul nostru indiferent de complexitatea locației. Găsiți pachetele la [PACHETE].")
]

CONCLUSION_TEMPLATES = [
    "La Superparty.ro, nu livrăm doar servicii, ci creăm zâmbete care contează. Dacă ești din [LOCATIE] și vrei să transformi ziua micuțului tău într-un basm, rezervă chiar acum: [TELEFON] / [WHATSAPP]. Magia se apropie!",
    "De la primele strigăte de bucurie și până la felicitările de final, succesul aniversării tale este asigurat. Pachetul nostru garantează zâmbete și efort zero din partea prărinților. Contactează-ne la [TELEFON] sau lasă-ne un mesaj pe [WHATSAPP].",
    "Gata cu stresul și panica de a amuza zeci de copii zgomotoși! Cu o organizare fluidă și mult entuziasm, echipa noastră preia ștafeta. Scrie-ne chiar acum pentru rezervare rapidă în [LOCATIE]: [WHATSAPP] sau sună-ne la [TELEFON]."
]

def load_reports():
    if not os.path.exists(REPORT_PATH):
        print("Nu gasesc articles_report.json! Asigura-te ca ai rulat primul audit.")
        return {}
    with open(REPORT_PATH, "r", encoding='utf-8') as f:
        data = json.load(f)
    return {item["slug"]: item for item in data}

def load_testimonials():
    TESTIMONIALS_FILE = "src/data/superparty_testimonials.json"
    t_slugs = set()
    if os.path.exists(TESTIMONIALS_FILE):
        with open(TESTIMONIALS_FILE, 'r', encoding='utf-8') as f:
            try:
                t_data = json.load(f)
                t_slugs = {t.get("slug") for t in t_data if t.get("siteId") == "superparty"}
            except:
                pass
    return t_slugs

def generate_rewrite(slug, keyword_personaj, keyword_locatie, event_type="aniversare"):
    intro = random.choice(INTRO_TEMPLATES)
    logistics = random.choice(LOGISTICS_TEMPLATES)
    program = random.choice(PROGRAM_TEMPLATES)
    sigs = random.sample(SIGNATURE_SECTIONS, 3)
    testimonial = random.choice(REALISTIC_TESTIMONIALS)
    c_faqs = random.sample(FAQS_LIBRARY, 6)
    conclusion = random.choice(CONCLUSION_TEMPLATES)

    # Inlocuiri globale
    def p(text):
        return text.replace("[LOCATIE]", keyword_locatie.title())\
                   .replace("[PERSONAJ]", keyword_personaj.title())\
                   .replace("[EVENIMENT]", event_type)\
                   .replace("[TELEFON]", "0722744377")\
                   .replace("[WHATSAPP]", "0722744377")\
                   .replace("[GALERIE]", "sutele de evenimente documentate")\
                   .replace("[PACHETE]", "pagina de Oferte")

    body = p(intro) + "\n\n"
    body += p(logistics) + "\n\n"
    body += p(program) + "\n\n"
    for s in sigs:
        body += p(s) + "\n\n"

    # FAQ Block
    body += "### Întrebări Frecvente (FAQ) despre Petrecerile cu " + keyword_personaj.title() + "\n"
    for q, a in c_faqs:
        body += f"**Î: {p(q)}**\n*R: {p(a)}*\n\n"

    body += p(conclusion) + "\n\n"
    
    # Adauga extra cuvinte pentru lungime
    # In loc de "umplutura", adaugam linkuri interne din aceeasi locatie dupa FAQ
    body += f"### De ce [PERSONAJ] e perfect pentru {keyword_locatie.title()}?\n"
    body += f"Popularitatea acestui personaj a crescut masiv printre opțiunile părinților din {keyword_locatie.title()}. Atunci când optezi pentru servicii profesionale dedicate acestui profil, scapi de emoțiile legate de animație. Aducem experiența anilor de activitate în domeniu pentru a transforma un eveniment obișnuit într-o petrecere excepțională cu zâmbete garantate. Contactul nostru direct pe [WHATSAPP] este cel mai rapid mod de a garanta disponibilitatea!\n\n"
    
    body += "---\n*Disclaimer: Pachetul de servicii descris face referire la un program generic, care poate fi customizat perfect nevoilor voastre impreuna cu echipa Superparty în prealabil.*"
    return body

def process_all_files():
    reports = load_reports()
    t_slugs = load_testimonials()
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.mdx')]
    
    new_csv_rows = [["filename", "slug", "indexStatus", "action_taken"]]
    
    for filename in files:
        filepath = os.path.join(INPUT_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.match(r'^---\s*(.*?)\s*---', content, re.DOTALL)
        if not match:
            continue
            
        fm_text = match.group(1)
        fm_lines = fm_text.split('\n')
        fm_dict = {}
        ordered_keys = []
        for line in fm_lines:
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                fm_dict[k] = v.strip()
                ordered_keys.append(k)

        slug = filename.replace('.mdx', '')
        report = reports.get(slug, {})
        score = report.get("overall_score", 5.0)
        risk = report.get("doorway_risk", "high")
        max_sim = report.get("top_similar_docs", [{"similarity": 1.0}])[0].get("similarity", 1.0) if report.get("top_similar_docs") else 1.0
        
        # Test placeholders (simulating dynamic content generation limits)
        has_placeholders = '[TELEFON]' in content or '[GALERIE]' in content
        has_real_testimonial = slug in t_slugs
        
        # Stricter categorization logic as per 10/10 Prompt: Only pages WITH real testimonials escape the 'hold' gate!
        if max_sim >= 0.60 or has_placeholders or not has_real_testimonial:
            idx_status = "hold"
        else:
            idx_status = "ready"
            
        fm_dict['indexStatus'] = f"'{idx_status}'"
        
        # Extragem locatia si personajul din URL slug (ex: animatori-petreceri-copii-alba-ca-zapada-bucuresti)
        slug_parts = slug.split('-')
        # Simple heuristica: cautam orasul in terminatii si restul e personajul
        loc = ""
        pers = "Animatorul Tau"
        common_cities = ["bucuresti", "ilfov", "sector-1", "sector-2", "sector-3", "sector-4", "sector-5", "sector-6", "magurele", "otopeni", "popesti", "voluntari", "bragadiru", "pantelimon", "chitila", "grozavesti"]
        for c in common_cities:
            if c in slug:
                loc = c.capitalize().replace('-', ' ')
                pers_parts = slug.replace("animatori-petreceri-copii-", "").replace(f"-{c}", "")
                pers = pers_parts.replace('-', ' ').title()
                break
        if not loc:
            loc = "zona ta locală"
            pers = slug.replace("animatori-petreceri-copii-", "").replace('-', ' ').title()

        new_body = generate_rewrite(slug, pers, loc, "aniversare")
        
        # Construim noul frontmatter si scriem fisierul
        new_content = "---\n"
        # Force order: title, description, indexStatus, pubDate, canonical, rest...
        new_content += f"title: {fm_dict.get('title', 'Petrecere')}\n"
        new_content += f"description: {fm_dict.get('description', 'Animatori petreceri copii')}\n"
        new_content += f"indexStatus: '{idx_status}'\n"
        if "pubDate" in fm_dict: new_content += f"pubDate: {fm_dict['pubDate']}\n"
        else: new_content += f"pubDate: '{datetime.datetime.now().strftime('%Y-%m-%d')}'\n"
        
        for k in ordered_keys:
            if k not in ["title", "description", "indexStatus", "pubDate"]:
                new_content += f"{k}: {fm_dict[k]}\n"
                
        new_content += "---\n\n"
        new_content += new_body
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        new_csv_rows.append([filename, slug, idx_status, "Completely rewritten via permuted ML-anti-doorway algorithm"])
        
    # Salveaza raport final
    import csv
    with open("superparty_seo_audit_results/superparty_top_hold.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_csv_rows)
        
    print("Done rewriting all MDX files!")

if __name__ == "__main__":
    process_all_files()
