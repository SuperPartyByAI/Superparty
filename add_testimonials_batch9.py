import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a făcut „atelier de baloane modelate" (căței, săbii, flori). Lui Darius i-au făcut o sabie albastră și s-a jucat toată petrecerea."
„Au organizat „pictură pe față" cu modele discrete. Ei Sofiei i-au desenat un fluturaș și a stat cuminte până s-a uscat."
„Superparty a propus „jocul statuilor" cu muzică veselă. Lui Paul i-au arătat semnalul de stop și a intrat imediat în joc."
„Au făcut „atelier de slime" în variantă curată (recipient, șervețele, ordine). Ei Carlei i-au dat culorile preferate și a plecat cu slime-ul la cutie."
„Superparty a organizat „vânătoare de indicii" pe camere (cu adult prezent). Lui Luca i-au dat harta simplă și a condus echipa."
„Au propus „cutia surpriză" cu întrebări amuzante. Ei Iuliei i-au citit întrebarea și a răspuns fără emoții."
„Superparty a făcut „mini-show de magie" cu monede și eșarfă. Lui Răzvan i-au ales rolul de asistent și s-a simțit special."
„Au organizat „dans cu panglici" pe melodii scurte. Ei Teodorei i-au dat panglica mov și a dansat până la final."
„Superparty a propus „tir la țintă" cu mingi moi pe panou cu puncte. Lui Emanoil i-au explicat cum se numără punctele și a fost super motivat."
„Au făcut „jocul cu baloane pe echipe" (ridică, pasează, nu scăpa). Ei Ilincăi i-au spus unde să stea și a colaborat perfect."
„Superparty a organizat „pinata" cu reguli clare (pe rând, distanță). Lui Alex i-au dat rândul când era pregătit și nu a fost haos."
„Au propus „atelier de cornete de confetti" (hârtie rulată, autocolante). Ei Anei-Maria i-au arătat cum să lipească marginile și a reușit."
„Superparty a făcut „jocul cu emoji pe expresii" (imită fața de pe cartonaș). Lui Bogdan i-au dat emoji-ul „wow" și a ieșit genial."
„Au organizat „povești cu păpuși" (mini-teatru). Ei Danei i-au dat o păpușă și a vorbit cu ea fără rușine."
„Superparty a propus „cursa cu saci" în variantă sigură (saci mici, spațiu liber). Lui Șerban i-au arătat cum să sară încet și a terminat fără căzături."
„Au făcut „atelier de origami" cu forme simple. Ei Irinei i-au îndoit primul colț și apoi a continuat singură."
„Superparty a organizat „jocul cu litere" (formezi un cuvânt din cartonașe). Lui Robert i-au dat literele ușoare și a făcut cuvântul repede."
„Au propus „mini-escape" pentru copii (3 ghicitori ușoare). Ei Amaliei i-au dat primul indiciu și a prins imediat ritmul."
„Superparty a făcut „bule uriașe" afară, cu cerc mare. Lui Andrei i-au arătat cum să stea nemișcat și a intrat într-o bulă perfectă."
„Au organizat „atelier de stickere" (decorat pahare/semne de carte). Ei Darei i-au dat stickerele cu inimioare și a decorat tot."
„Superparty a propus „jocul șoaptelor" (mesajul trece pe rând). Lui Matei i-au spus să șoptească încet și s-a amuzat de rezultat."
„Au făcut „cursa cu cărți pe cap" (mers încet, echilibru). Ei Oanei i-au arătat poziția corectă și a ajuns până la capăt."
„Superparty a organizat „bingo cu imagini" (animale, fructe). Lui David i-au dat planșa și a strigat „Bingo!" primul."
„Au propus „atelier de pictat pietricele" (modele simple). Ei Larei i-au dat un model cu curcubeu și a ieșit foarte frumos."
„Superparty a făcut „jocul cu șnururi colorate" (găsește perechea). Lui George i-au explicat regula și a găsit rapid perechile."
„Au organizat „mini-disco" cu lumini discrete și reguli de spațiu. Ei Biancăi i-au oferit un loc în față și a dansat fericită."
„Superparty a propus „cursa cu mingi pe traseu" (rostogolire printre jaloane). Lui Florin i-au arătat slalomul și a controlat mingea excelent."
„Au făcut „jocul de memorie" cu cartonașe mari. Ei Cătălinei i-au dat primul exemplu și a început să găsească perechi."
„Superparty a organizat „atelier de mini-coroane" cu numele copilului. Lui Rares i-au scris numele cu marker auriu și a fost încântat."
„Au propus „telefonul cu gesturi" (fără cuvinte). Ei Mădălinei i-au dat un gest ușor și a transmis corect."
„Superparty a făcut „jocul cu umbre" (forme pe perete cu lanternă). Lui Ionuț i-au arătat cum să facă „iepurașul" și a tot repetat."
„Au organizat „atelier de biscuiți decorați" (glazură simplă, șervețele). Ei Patriciei i-au dat sprinkles colorate și a decorat minunat."
„Superparty a propus „cursa cu obstacole și misiuni" (atinge conul, revino). Lui Raul i-au explicat pe pași și a fost foarte atent."
„Au făcut „jocul cu culori pe muzică" (când se oprește, alegi o culoare). Ei Alexiei i-au arătat culoarea de start și a intrat rapid în joc."
„Superparty a organizat „atelier de cartonase cu mesaje" (pentru sărbătorit). Lui Tudor i-au dat șabloane și a scris un mesaj foarte frumos."
„Au propus „jocul cu balonul pe ștafetă" (pasezi cu palma). Ei Emei i-au spus să paseze încet și nu s-a speriat deloc."
„Superparty a făcut „mini-trivia Superparty" (întrebări despre petrecere). Lui Călin i-au dat o întrebare ușoară și a răspuns sigur."
„Au organizat „pictură pe tricou" (șabloane, vopsea textilă). Ei Ralucăi i-au oferit un șablon cu stea și a ieșit wow."
„Superparty a propus „jocul cu semne" (sus, jos, stânga, dreapta). Lui Mario i-au arătat semnele și a urmat perfect instrucțiunile."
„Au făcut „atelier de mini-fotobooth" cu accesorii (ochelari, mustăți). Ei Iasminei i-au dat o coroniță și a făcut poze superbe."
„Superparty a organizat „cursa cu prietenul" (legat ușor la gleznă, foarte lent). Lui Sebastian i-au ales un partener potrivit și a mers fără stres."
„Au propus „jocul cu baloane numerotate" (cauți numărul strigat). Ei Mariei i-au dat numărul ei și l-a găsit imediat."
„Superparty a făcut „atelier de magnet de frigider" (spumă EVA). Lui Eric i-au dat un model cu dinozaur și a lipit piesele singur."
„Au organizat „dansul personajelor" (supererou, prinț, astronaut). Ei Nicoletei i-au dat „prințesă" și a dansat cu grație."
„Superparty a propus „jocul cu mingi în cerc" (pasezi pe ritm). Lui Adi i-au spus ritmul și a pasat fără să scape."
„Au făcut „mini-atelier de știință" (vulcan cu bicarbonat, controlat). Ei Dorianei i-au pus ochelarii de protecție și a fost fascinată."
„Superparty a organizat „ghicește mirosul" (fructe/condimente ușoare). Lui Marius i-au dat un miros simplu și a ghicit repede."
„Au propus „jocul cu balonul pe ventilator" (ține balonul în aer cu carton). Ei Elenei i-au dat cartonul și a râs non-stop."
„Superparty a făcut „atelier de puzzle personalizat" (lipit imagine pe carton). Lui Denis i-au dat piesele mari și a terminat rapid."
„Au încheiat cu „cercul recunoștinței" (fiecare spune ce i-a plăcut). Ei Larisei i-au dat timp să se gândească și a spus ceva foarte drăguț."
„Superparty a venit cu jocul „parașuta colorată" (pânză mare, mingi ușoare). Lui Vlad i-au arătat cum să țină marginea și a fost cel mai entuziasmat."
„Au făcut „atelier de măști" (carton, elastic, stickere). Ei Evelinei i-au ales o mască de pisicuță și a plecat cu ea pe față."
„Superparty a organizat „karaoke pentru copii" cu refrene scurte. Lui Cezar i-au dat microfonul pe rând și a cântat fără emoții."
„Au propus „turnul din pahare" (cât mai înalt, fără grabă). Ei Sorinei i-au arătat baza stabilă și a reușit un turn perfect."
„Superparty a făcut „jocul detectivului" (găsește obiectul după indiciu). Lui Mihnea i-au dat primul indiciu și a ghicit imediat."
„Au organizat „atelier de brățări" (mărgele mari, șnur). Ei Georgiei i-au arătat nodul de început și a făcut două brățări."
„Superparty a propus „cursa cu lingura și mingea" (mers încet). Lui Octavian i-au explicat să nu alerge și a terminat fără să scape mingea."
„Au făcut „povești pe cartonașe" (alegi 3 imagini și inventezi). Ei Adrianei i-au dat cartonașele cu animale și a inventat o poveste amuzantă."
„Superparty a organizat „provocarea LEGO" (construiești după model). Lui Patrick i-au dat modelul simplu și a construit rapid."
„Au propus „jocul cu balonul între genunchi" (ștafetă). Ei Ramonei i-au arătat cum să țină balonul și a reușit din prima."
„Superparty a făcut „atelier de felicitări pop-up" (îndoituri simple). Ei Sabinei i-au arătat primul pas și a ieșit o inimă 3D."
„Au organizat „mima meseriilor" (doctor, bucătar, pompier). Lui Silviu i-au dat „pompier" și a fost genial."
„Superparty a propus „jocul cu numere ascunse" prin cameră. Ei Cristinei i-au dat lista și a găsit toate numerele."
„Au făcut „mini-olimpiadă" cu 3 probe scurte. Lui Horia i-au cronometrat corect și a fost super motivat."
„Superparty a organizat „atelier de mini-avioane" din hârtie. Lui Damian i-au arătat plierea aripilor și avionul a zburat cel mai departe."
„Au propus „jocul culorilor pe podea" (pășești doar pe culoarea strigată). Ei Mirelei i-au spus culoarea de start și a intrat imediat în joc."
„Superparty a făcut „ghicește sunetul" (instrumente mici). Lui Rareș i-au dat un sunet de maracas și a ghicit din prima."
„Au organizat „atelier de insignă" cu numele copilului. Ei Lorenei i-au scris numele frumos și a purtat insigna toată petrecerea."
„Superparty a propus „cursa cu jaloane" (slalom). Lui Sergiu i-au arătat traseul și a făcut slalom fără să dărâme nimic."
„Au făcut „jocul cu cutia misterioasă" (pipăi și ghicești obiectul). Ei Laviniei i-au dat un obiect ușor și a ghicit repede."
„Superparty a organizat „atelier de pictat pe canvas" (mini-pânze). Ei Rebecăi i-au dat un șablon cu stea și a ieșit foarte curat."
„Au propus „ștafeta cu mesaj" (duci un bilețel la echipă). Lui Filip i-au dat rolul de „mesager" și s-a simțit important."
„Superparty a făcut „jocul cu semafor" (verde-alergi încet, roșu-oprești). Lui Cătălin i-au explicat regulile și a respectat perfect."
„Au organizat „atelier de păpuși din șosete" (ochi lipiți, lână). Ei Alinei i-au ales o lână roz și păpușa a ieșit super."
„Superparty a propus „quiz cu imagini" (personaje, animale). Lui Beniamin i-au dat tableta cu imagini și a răspuns corect la multe."
„Au făcut „jocul cu cercurile" (sari din cerc în cerc). Ei Doiniței i-au arătat distanța bună și a sărit fără probleme."
„Superparty a organizat „atelier de rame foto" (bețe, lipici, paiete). Ei Roxanei i-au dat paietele aurii și rama a ieșit wow."
„Au propus „vânătoare de culori" (găsești în cameră ceva verde, roșu etc.). Lui Nectarie i-au dat lista și a găsit tot."
„Superparty a făcut „dans pe ziare" (spațiu mic, atenție). Ei Danei i-au arătat cum să stea pe foaie și s-a distrat mult."
„Au organizat „atelier de mini-robot" din carton (lipit piese simple). Lui Ovidiu i-au dat piesele deja tăiate și a asamblat rapid."
„Superparty a propus „pălării haioase" (decorat pălării de hârtie). Ei Loredanei i-au dat stickere cu stele și pălăria a ieșit superbă."
„Au făcut „jocul cu traseu pe frânghie" (mergi pe linie). Lui Cosmin i-au arătat echilibrul și a mers până la capăt."
„Superparty a organizat „atelier de plastilină" cu figurine tematice. Ei Aurorei i-au sugerat o floricică și a modelat-o perfect."
„Au propus „jocul cu balonul pe cap" (ștafetă lentă). Lui Daniel i-au arătat cum să meargă încet și balonul nu a căzut."
„Superparty a făcut „puzzle pe echipe" (piese mari). Ei Selenei i-au dat colțurile și a ajutat echipa să termine."
„Au organizat „atelier de semne de carte" (laminare simplă/folie). Lui Eduard i-au pus numele frumos și a fost încântat."
„Superparty a propus „jocul cu mingi la coș" (distanțe diferite). Lui Iacob i-au ales distanța potrivită și a marcat de mai multe ori."
„Au făcut „ghicește personajul" (întrebări cu da/nu). Ei Carinei i-au dat un personaj ușor și a ghicit rapid."
„Superparty a organizat „atelier de colaj" (revistă, lipici, formă). Ei Florentinei i-au dat o formă de inimă și colajul a ieșit foarte colorat."
„Au propus „jocul cu prinderea eșarfei" (reflexe). Lui Iulian i-au arătat când să prindă și s-a prins imediat."
„Superparty a făcut „petrecerea inversă" (când zic „sus", faci „jos"). Lui Teo i-au explicat regula și a râs continuu."
„Au organizat „atelier de mini-pompom" (lână, carton). Ei Mihaelei i-au arătat cum să taie pe margine și pompomul a ieșit pufos."
„Superparty a propus „cursa cu bile pe tub" (sufli ușor). Lui Damian i-au arătat intensitatea și bila a ajuns prima."
„Au făcut „jocul cu întrebări amuzante" (preferi...?). Ei Monicăi i-au citit întrebarea și a răspuns super creativ."
„Superparty a organizat „atelier de puzzle cu nume" (litere din spumă). Lui Claudiu i-au dat literele numelui și le-a aranjat singur."
„Au propus „dans cu scaune" în variantă blândă (fără alergat). Ei Andreei i-au găsit un scaun aproape și a fost foarte ok."
„Superparty a făcut „jocul cu indicii pe culori" (urmezi culoarea corectă). Lui Remus i-au dat primul indiciu și a condus echipa."
„Au organizat „atelier de mini-lanțuri" (agățători cu forme). Ei Melisei i-au dat o formă de inimă și a decorat-o frumos."
„Superparty a propus „pantomimă cu animale" (fără sunete). Lui Doru i-au dat „maimuță" și toți au ghicit imediat."
„Au încheiat cu „poza de grup + diplome" pentru copii. Ei Deliei i-au înmânat diploma cu numele ei și a fost foarte mândră."
„Superparty a început cu „dansul statuilor" și a făcut pauze scurte ca să nu obosească nimeni. Lui Robert i-au spus exact când să înghețe și s-a distrat maxim."
„Au adus un „tunel pliabil" pentru jocul de aventură. Ei Iasminăi i-au ținut tunelul stabil și a trecut de câteva ori, râzând."
„Superparty a făcut „atelier de slime" în variantă curată (cutiuțe, șervețele, reguli). Lui Denis i-au dat mănuși mici și a fost încântat."
„Au organizat „bingo cu personaje" (cartonașe mari, ușor de urmărit). Ei Mădălinei i-au arătat cum bifează și a completat prima."
„Superparty a propus „jocul cu umbre" pe perete (lanternă + forme). Lui Luca i-au făcut o umbră de dinozaur și a vrut să încerce și el."
„Au făcut „mini-cursă de saci" cu distanță mică. Ei Biancăi i-au ales un sac potrivit și a terminat fără să cadă."
„Superparty a pregătit „vânătoare de comori" cu harta camerei. Lui Ionuț i-au dat busola-jucărie și a condus echipa."
„Au organizat „atelier de magneți de frigider" (spumă EVA, forme). Ei Anitei i-au dat forme cu unicorni și le-a decorat atent."
„Superparty a făcut „balonul nu cade" (lovituri ușoare, pe rând). Lui Dragoș i-au arătat cum să lovească fin și a ținut balonul mult."
„Au propus „jocul cu litere" (găsești litera din numele tău). Ei Irinei i-au găsit litera „I" pe un cartonaș și a aplaudat."
„Superparty a organizat „atelier de coronițe" (hârtie + pietricele). Lui Tiberiu i-au lipit o stea în față și a purtat coroana toată petrecerea."
„Au făcut „micul laborator" cu reacție sigură (bicarbonat + oțet, în tavă). Ei Dacianei i-au pus ochelari de protecție de jucărie și a fost fascinată."
„Superparty a propus „ștafeta cu apă" (pahare mici, fără haos). Lui Paul i-au ales un traseu scurt și a reușit să nu verse."
„Au organizat „atelier de desen pe șabloane" (forme clare). Ei Ameliei i-au oferit șablon cu fluture și a ieșit foarte frumos."
„Superparty a făcut „jocul cu șoapta" (mesaj pe rând). Lui Sebastian i-au pus un mesaj amuzant și finalul a fost o glumă generală."
„Au propus „cursa cu balonul pe paletă" (farfurie de carton). Ei Oanei i-au arătat cum să țină farfuria dreaptă și a mers perfect."
„Superparty a organizat „atelier de pictat pietricele" (model simplu, markere). Lui Vladislav i-au dat o piatră rotundă și a făcut un smiley."
„Au făcut „jocul cu semne" (imitați liderul fără cuvinte). Ei Emei i-au pus rolul de lider 30 de secunde și a fost încântată."
„Superparty a propus „construcții cu paie și conectori" (structuri). Lui Kevin i-au arătat triunghiul de bază și a construit un turn."
„Au încheiat un moment cu „aplaudă pe ritm" (coordonare). Ei Mariei i-au prins ritmul ușor și a bătut din palme corect."
„Superparty a făcut „atelier de etichete pentru cadouri" (decupat, lipit). Lui Liviu i-au scris numele cu litere mari și a ieșit super."
„Au organizat „pescuitul de rațe" (magneți, pe rând). Ei Ștefaniei i-au arătat undița și a prins prima rață."
„Superparty a propus „jocul cu microfonul imaginar" (prezinți un talent). Lui Răzvan i-au dat curaj și a spus o glumă scurtă."
„Au făcut „atelier de mini-pictură pe farfurii" (decor de petrecere). Ei Andei i-au dat un model cu curcubeu și a ieșit foarte vesel."
„Superparty a organizat „jocul cu cifre pe spate" (desenezi o cifră cu degetul). Lui Sorin i-au făcut cifra 8 și a ghicit imediat."
„Au propus „aruncă inelul" (inele din carton pe sticle). Ei Ralucăi i-au ajustat distanța și a nimerit de trei ori."
„Superparty a făcut „povestea cu final ales de copii". Lui Emanuel i-au cerut finalul și a inventat unul foarte amuzant."
„Au organizat „atelier de steaguri mici" (bețișor + hârtie colorată). Ei Teodorei i-au dat culori pastel și a ieșit un steag foarte frumos."
„Superparty a propus „jocul cu sărituri pe numere" (1–10 pe podea). Lui Norbert i-au arătat ordinea și a sărit corect."
„Au făcut „roata complimentelor" (spui ceva frumos colegului). Ei Elizei i-au șoptit un exemplu și a spus un compliment sincer."
„Superparty a organizat „atelier de mini-puzzle personalizat" (imagine lipită pe carton). Lui Matei i-au dat puzzle-ul cu dinozaur și l-a completat."
„Au propus „jocul cu mingi colorate" (strigi culoarea și o prinzi). Ei Iuliei i-au ales o minge ușoară și a prins-o fără teamă."
„Superparty a făcut „micul show de baloane" (forme simple). Lui Andrei i-au făcut o sabie din balon și a fost în extaz."
„Au organizat „atelier de corăbii din hârtie" și le-au pus pe apă într-un lighean. Ei Patriciei i-au arătat cum să plieze prova și barca a plutit."
„Superparty a propus „ghicește mirosul" (condimente ușoare, fără riscuri). Lui Șerban i-au dat scorțișoară și a recunoscut-o."
„Au făcut „jocul cu mingi la țintă" (cercuri pe perete). Ei Darei i-au setat ținta mai aproape și a lovit-o."
„Superparty a organizat „atelier de mini-fotoliu" pentru pluș (carton, bandă). Lui Raul i-au ținut piesele și a asamblat rapid."
„Au propus „dans cu panglici" (panglici colorate, mișcări lente). Ei Cătălinei i-au dat o panglică mov și s-a mișcat elegant."
„Superparty a făcut „jocul cu întrebări rapide" (ce preferi: înghețată sau pizza?). Lui Adrian i-au pus întrebări pe rând și a răspuns amuzant."
„Au organizat „atelier de tablouri cu amprente" (degete + vopsea lavabilă). Ei Denisei i-au șters repede mâinile și a ieșit un copăcel superb."
„Superparty a propus „cursa cu obstacole moi" (perne, jaloane). Lui Silas i-au arătat drumul și a trecut fără emoții."
„Au făcut „jocul cu cutii sonore" (scuturi mici, scuturat și ghicit). Ei Evelinei i-au dat o cutie cu boabe și a ghicit."
„Superparty a organizat „atelier de bentițe cu urechi" (lipit, decupat). Lui Tudor i-au făcut urechi de lup și i-au stat perfect."
„Au propus „jocul cu comenzi amuzante" (bate din palme, sare o dată). Ei Norei i-au dat comenzi ușoare și a ținut pasul."
„Superparty a făcut „ștafeta cu puzzle" (duci o piesă pe rând). Lui George i-au dat piesa finală și a pus-o cu mândrie."
„Au organizat „atelier de globuri" (pentru decor, din carton). Ei Larei i-au dat sclipici argintiu și globul a arătat superb."
„Superparty a propus „jocul cu ghicitori" pe vârste. Lui Radu i-au citit una simplă și a răspuns imediat."
„Au făcut „mic teatru de păpuși" cu voci diferite. Ei Sofiei i-au oferit o păpușă-iepuraș și a intrat în rol."
„Superparty a organizat „atelier de mini-medalii" (carton + panglică). Lui Darius i-au pus medalia la gât și a zâmbit larg."
„Au încheiat cu „dansul preferat al sărbătoritului" și un cerc de aplauze. Ei Corinei i-au făcut loc în față și a dansat fără rușine."
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
total_articles = len(assigned_slugs) + new_articles
print(f"Total acum: {len(existing_testimonials)} testimoniale pentru {total_articles} articole.")
