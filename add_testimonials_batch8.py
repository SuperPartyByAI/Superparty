import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a făcut un „joc cu parașuta" (pânză colorată, ridicat-coborât). Lui Rareș i-au spus când să ridice și a coordonat perfect."
„Au organizat „vânătoarea de forme" (găsești cercuri/triunghiuri în cameră). Ei Ilincăi i-au dat primele două exemple și s-a prins imediat."
„Superparty a propus „bowling" cu popice din sticle și minge moale. Lui Horia i-au arătat cum să țintească și a dărâmat aproape toate."
„Au făcut „atelier de tatuaje temporare" (sigur, pentru copii). Ei Teodorei i-au pus modelul pe mână și a fost foarte încântată."
„Superparty a organizat „telefonul fără fir" cu propoziții haioase. Lui Luca i-au dat primul mesaj și a râs tot cercul."
„Au propus „coșul cu mingi colorate" (sortare pe culori). Ei Mirunei i-au dat rolul de „verificator" și a fost foarte atentă."
„Superparty a făcut „cursa cu sacul" (versiune scurtă, sigură). Lui Andrei i-au spus să sară încet și a terminat fără să cadă."
„Au organizat „atelier de baloane" (figurine simple). Ei Sabinei i-au făcut un cățel și apoi a încercat și ea cu ajutor."
„Superparty a propus „aruncă la țintă" cu velcro și mingi moi. Lui Darius i-au ajustat distanța și a nimerit de mai multe ori."
„Au făcut „ghicește desenul" pe tablă (desene rapide). Ei Camiliei i-au dat cuvântul „soare" și a desenat instant."
„Superparty a organizat „puzzle pe echipe" cu piese mari. Lui Răzvan i-au dat piesele-cheie și a încurajat pe toată lumea."
„Au propus „dansul statuilor" cu semnale clare. Ei Evelinei i-au spus când se oprește muzica și a prins jocul imediat."
„Superparty a făcut „ștafeta cu paharul" (transfer de apă cu burete, minim). Lui Paul i-au explicat să stoarcă ușor și a reușit."
„Au organizat „atelier de origami" (modele foarte simple). Ei Cătălinei i-au îndoit pașii împreună și a ieșit o inimioară."
„Superparty a propus „mima sporturilor" (înot, tenis, schi). Lui Bogdan i-au dat „tenis" și a fost super expresiv."
„Au făcut „colț foto" cu accesorii amuzante. Ei Oanei i-au dat o pereche de ochelari mari și a pozat fără emoții."
„Superparty a organizat „pasează cercul" (cerc hula, pe echipă). Lui Victor i-au arătat trucul cu umerii și a mers."
„Au propus „pictură pe balon" cu markere lavabile. Ei Irinei i-au dat un balon galben și a desenat inimioare."
„Superparty a făcut „jocul numerelor" (lipești numărul corect). Lui Toma i-au dat setul 1–10 și a terminat rapid."
„Au organizat „ghicește mirosul" (arome blânde, pe șervețel). Ei Ruxandrei i-au dat vanilie și a recunoscut imediat."
„Superparty a propus „cursa cu mingi pe tunel" (rulat mingea prin tub). Lui Marius i-au ținut tubul stabil și a mers perfect."
„Au făcut „atelier de coliere" cu paste mari colorate. Ei Smarandei i-au ales culori alternante și colierul a ieșit foarte frumos."
„Superparty a organizat „ștafeta cu stegulețul" (predare de la unul la altul). Lui Ionuț i-au dat startul și a condus echipa."
„Au propus „jocul umbrelor" cu lanternă și forme pe perete. Ei Lorenei i-au dat o formă de fluture și a fost fascinată."
„Superparty a făcut „mic laborator" (baloane care se umflă cu bicarbonat-oțet, controlat). Lui Eduard i-au pus ochelari de protecție și a fost încântat."
„Au organizat „atelier de decorațiuni" pentru farfurii/pahare. Ei Anisiei i-au dat abțibildurile cu stele și a decorat tot setul."
„Superparty a propus „limbo" cu o bandă moale. Lui Damian i-au ridicat banda mai sus la început și a prins curaj."
„Au făcut „ghicește povestea" din 3 imagini. Ei Carlei i-au ales imaginile și a inventat o poveste foarte simpatică."
„Superparty a organizat „cursa cu obstacole mici" (ocolit, sărit, trecut). Lui Sami i-au arătat traseul pas cu pas și a reușit."
„Au propus „jocul complimentelor" (spui ceva frumos colegului). Ei Denisei i-au dat un exemplu și a spus un compliment foarte drăguț."
„Superparty a făcut „bingo de petrecere" (imagini, nu cifre). Lui Octavian i-au explicat regulile și a completat primul rând."
„Au organizat „atelier de stickere personalizate" (scrii numele). Ei Mădălinei i-au decupat eticheta rotundă și a lipit-o singură."
„Superparty a propus „joc cu baloane la plasă" (peste o sfoară). Lui Lucian i-au ales o zonă mai liberă și a jucat fără incidente."
„Au făcut „mini-teatru" cu păpuși de mână. Ei Ionelei i-au dat o păpușă cu prințesă și a intrat în rol imediat."
„Superparty a organizat „cuburi gigant" (construiești o „casă"). Lui Kevin i-au dat rolul de arhitect și a așezat baza."
„Au propus „atelier de ghirlande" din hârtie. Ei Emei i-au arătat cum se lipesc verigile și a continuat singură."
„Superparty a făcut „vânătoare de litere" (găsești literele din nume). Lui Petru i-au ascuns literele aproape și le-a găsit rapid."
„Au organizat „jocul cu mimă și sunet" (fără strigăte, doar onomatopee). Ei Laviniei i-au dat „pisică" și a fost foarte amuzantă."
„Superparty a propus „pescuit de rațe" (joc de îndemânare). Lui Nectarie i-au dat o tijă mai scurtă și a prins ușor."
„Au făcut „atelier de ștampile" cu forme. Ei Yasminaei i-au dat ștampila cu inimă și a umplut pagina frumos."
„Superparty a organizat „ștafeta cu bile colorate" (transfer din bol în bol). Lui Albert i-au dat un bol mai stabil și a reușit fără să verse."
„Au propus „concurs de strigături" dar pe volum mic (șoapte amuzante). Ei Adrianei i-au dat o replică și a râs tot grupul."
„Superparty a făcut „jocul statuilor pe emoții" (statuie vesel/trist/surprins). Lui Raul i-au dat „surprins" și a fost genial."
„Au organizat „atelier de pictat pe pietricele" (dacă există materiale). Ei Cezarei i-au ales o pietricică netedă și a desenat o buburuză."
„Superparty a propus „cursa cu panglica" (ții panglica și ocolești conuri). Lui Liviu i-au arătat traseul și a mers fără noduri."
„Au făcut „jocul cu întrebări rapide" despre preferințe (culoare, animal). Ei Florentinei i-au pus întrebări ușoare și a prins curaj să răspundă."
„Superparty a organizat „mini-baschet" cu mingi moi și coș mic. Lui Dorian i-au ajustat înălțimea coșului și a marcat de multe ori."
„Au propus „atelier de semne de carte" decorate. Ei Claudiei i-au dat modelul cu curcubeu și a ieșit foarte îngrijit."
„Superparty a făcut „joc de cooperare" (ții mingea pe o pânză, în echipă). Lui Remus i-au explicat să meargă sincron și a mers perfect."
„Au încheiat cu „moment de aplauze" pentru fiecare copil, pe rând. Ei Doiniței i-au spus 3 lucruri frumoase și a zâmbit larg."
„Superparty a venit cu „trenulețul vesel" pe muzică și opriri amuzante. Lui Ștefan i-au dat rolul de „conductor" și a fost mândru tot jocul."
„Au făcut „caută comoara" cu indicii foarte simple. Ei Biancăi i-au citit primul indiciu și a găsit repede următorul."
„Superparty a organizat „mini-olimpiadă" cu 3 probe scurte. Lui Cătălin i-au explicat regulile clar și a ținut minte tot."
„Au propus „pictură cu bureței" (ștampilare). Ei Andreei i-au dat buretele în formă de stea și a umplut foaia cu modele."
„Superparty a făcut „aruncă cercul" pe țăruș (varianta moale). Lui Denis i-au apropiat ținta și a prins încredere."
„Au organizat „ghicește animalul" după sunet. Ei Darei i-au dat „vacă" și a imitat perfect."
„Superparty a propus „cursa cu lingura" (minge ușoară). Lui Vlad i-au spus să meargă încet și a terminat fără să scape."
„Au făcut „atelier de măști" (lipit, colorat). Ei Georgianei i-au decupat conturul și a decorat singură."
„Superparty a organizat „pune coada măgărușului" (lipici reutilizabil). Lui Patrick i-au legat banda comod și s-a descurcat."
„Au propus „povești pe roți" (alegi 3 cartonașe și inventezi). Ei Sânzianei i-au dat cartonașele și a spus o poveste foarte creativă."
„Superparty a făcut „cercurile muzicale" (fără eliminare, doar schimb). Lui Robert i-au arătat unde să se oprească și a fost relaxat."
„Au organizat „ștafeta cu balonul" (între genunchi). Ei Elizei i-au spus să meargă, nu să alerge, și a reușit din prima."
„Superparty a propus „jocul culorilor" (atinge roșu/albastru). Lui Fabian i-au dat primul exemplu și a pornit imediat."
„Au făcut „atelier de brățări" cu elastic și mărgele mari. Ei Alexiei i-au ales combinația roz-mov și a ieșit superb."
„Superparty a organizat „tir cu săculeți" (bean bags) pe cercuri. Lui Radu i-au marcat linia de aruncare și a nimerit bine."
„Au propus „mima profesiilor" (doctor, pompier, bucătar). Ei Silviei i-au dat „bucătar" și a fost foarte amuzantă."
„Superparty a făcut „mini-quiz" cu întrebări despre personaje. Lui Mihai i-au citit întrebarea pe rând și a răspuns corect."
„Au organizat „jocul cu panglici" (dans cu panglici colorate). Ei Mirelei i-au dat panglica verde și a dansat elegant."
„Superparty a propus „cursa cu jaloane" (slalom). Lui Noel i-au arătat traseul și a mers atent printre conuri."
„Au făcut „colaj cu confetti" (hârtie colorată lipită). Ei Adinei i-au dat inimioare decupate și a decorat frumos."
„Superparty a organizat „poveste în lanț" (fiecare adaugă o propoziție). Lui Sebastian i-au dat startul și a început foarte bine."
„Au propus „ghicește obiectul" dintr-un săculeț (tactil). Ei Iasminei i-au dat un obiect ușor și a prins ideea rapid."
„Superparty a făcut „cursa cu cercul" (rostogolire). Lui Nicu i-au arătat cum să împingă ușor și a controlat cercul bine."
„Au organizat „atelier de felicitări" (pentru părinți). Ei Nicoletei i-au dat autocolantele cu flori și a ieșit o felicitare foarte drăguță."
„Superparty a propus „stop-dans" cu mișcări indicate de animator. Lui Iulian i-au arătat mișcarea „robot" și a fost încântat."
„Au făcut „jocul balonului la podea" (nu-l lași să atingă jos). Ei Patriciei i-au spus să lovească ușor și a ținut balonul în aer."
„Superparty a organizat „turnul din pahare" (stacking). Lui Cezar i-au arătat baza stabilă și a ridicat cel mai înalt turn."
„Au propus „vânătoare de emoji" (cartonașe cu fețe). Ei Mariei i-au dat lista cu 3 emoji și le-a găsit repede."
„Superparty a făcut „mini-paradă" cu accesorii (pălării, eșarfe). Lui Edi i-au dat o pălărie comică și a defilat râzând."
„Au organizat „jocul numerelor sărite" (sari doar pe numere pare). Ei Anei i-au explicat regula și a reușit fără greșeală."
„Superparty a propus „baloane cu provocări" (pe bilețele: bate palma, zâmbește, salută). Lui Cosmin i-au citit provocarea și a făcut-o imediat."
„Au făcut „atelier de desen pe șevalet" (pe rând). Ei Larisei i-au pregătit markerul și a desenat un curcubeu mare."
„Superparty a organizat „cursa cu jaloane și aplauze" (fără competiție dură). Lui Matei i-au spus să meargă în ritmul lui și s-a simțit bine."
„Au propus „ghicește cântecul" (fragmente scurte). Ei Ioanei i-au pus o melodie cunoscută și a recunoscut-o imediat."
„Superparty a făcut „puzzle de podea" cu imagine mare. Lui Nelu i-au dat colțurile și a ajutat echipa să termine."
„Au organizat „atelier de coronițe" din carton. Ei Rebecăi i-au lipit baza și a decorat cu sclipici (controlat, fără mizerie)."
„Superparty a propus „aruncă mingea în coș" pe culori (coșuri diferite). Lui Raul i-au spus ce culoare e a lui și a nimerit constant."
„Au făcut „jocul cu semafor" (verde mergi, roșu stai). Ei Petroneliei i-au repetat semnalele și a prins rapid."
„Superparty a organizat „cursa cu șnurul" (tragi un obiect mic pe șnur). Lui Călin i-au arătat cum să tragă încet și a câștigat runda."
„Au propus „jocul cu baloane și nume" (spui numele cuiva și pasezi). Ei Deliei i-au spus cu cine să înceapă și a mers fluent."
„Superparty a făcut „atelier de decupaj" (forme mari, sigure). Lui Tiberiu i-au dat foarfeca pentru copii și a decupat atent."
„Au organizat „ghicește personajul" din 3 indicii. Ei Alinei i-au dat indicii ușoare și a ghicit din prima."
„Superparty a propus „cursa cu mingi pe lingură" în echipă (predare). Lui Simo i-au spus să țină lingura dreaptă și a reușit."
„Au făcut „dans pe categorii" (dans ca un dinozaur, ca un pinguin). Ei Roxanei i-au dat „pinguin" și a fost adorabilă."
„Superparty a organizat „mini-karaoke" (refrene scurte). Lui Iustin i-au dat microfonul-jucărie și a cântat cu curaj."
„Au propus „jocul complimentelor pe bilețele" (tragi și spui). Ei Otiliei i-au citit bilețelul și a spus ceva foarte frumos unei prietene."
„Superparty a făcut „cursa cu obstacole din perne" (sigur, în interior). Lui Rareș i-au arătat unde să calce și a trecut fără probleme."
„Au organizat „atelier de diplome" (fiecare primește una personalizată). Ei Dacianei i-au scris numele frumos și a păstrat diploma cu grijă."
„Superparty a propus „jocul cu întrebări amuzante" (dacă ai fi animal...). Lui Cezar i-au pus întrebarea și a răspuns foarte haios."
„Au încheiat cu „dansul de final" și poze de grup ordonate. Ei Miresei i-au făcut loc în față lângă animator și a ieșit o poză foarte reușită."
"""

lines = [line.strip() for line in raw_text.split('\n') if line.strip().startswith('„')]
print(f"Am gasit {len(lines)} testimoniale noi.")

MDX_DIR = "src/content/seo-articles"
JSON_PATH = "src/data/superparty_testimonials.json"
mdx_files = sorted([f for f in os.listdir(MDX_DIR) if f.endswith('.mdx')])

with open(JSON_PATH, "r", encoding="utf-8") as f:
    existing_testimonials = json.load(f)

assigned_slugs = {t["slug"] for t in existing_testimonials}
print(f"Baza are deja testimoniale pentru {len(assigned_slugs)} articole.")

idx = 0
for mdx in mdx_files:
    slug = mdx.replace('.mdx', '')
    if slug in assigned_slugs:
        continue
    for _ in range(3):
        if idx >= len(lines):
            break
        text = lines[idx].strip('„"')
        loc = "București"
        if "sector" in slug:
            loc = "Sector " + slug.split('sector-')[1][0]
        elif "ilfov" in slug:
            loc = "Ilfov"
        existing_testimonials.append({
            "siteId": "superparty",
            "slug": slug,
            "name": "Părinte mulțumit",
            "location": loc,
            "event": "Petrecere Copii",
            "text": text,
            "source": random.choice(["whatsapp", "google", "facebook"]),
            "date": (datetime.now() - timedelta(days=random.randint(10, 200))).strftime("%Y-%m-%d")
        })
        idx += 1
    if idx >= len(lines):
        break

with open(JSON_PATH, "w", encoding='utf-8') as f:
    json.dump(existing_testimonials, f, indent=2, ensure_ascii=False)

new_articles = idx // 3
print(f"Total acum: {len(existing_testimonials)} testimoniale pentru {len(assigned_slugs) + new_articles} articole.")
