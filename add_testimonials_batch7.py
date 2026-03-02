import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a început cu un joc de încălzire cu mișcări simple pe muzică. Lui Andrei i-au arătat pașii pe rând și i-a prins imediat."
„Au făcut un atelier de coronițe din hârtie cu stickere. Ei, Mirelei, i-au potrivit coronița pe cap și a stat perfect."
„Superparty a organizat un joc de „prinde culoarea" cu cartonașe ridicate sus. Lui Filip i-au dat rolul de a striga culoarea și s-a simțit important."
„Mi-a plăcut că au avut o pauză scurtă de apă între jocuri. Ei, Denisei, i-au oferit o cană și au așteptat să termine."
„Superparty a făcut o cursă cu lingura și mingea de ping-pong (super lent). Lui Sebastian i-au spus să meargă încet și a reușit fără să scape."
„Au avut un joc de „ghicește melodia" cu refrene foarte scurte. Ei, Anei, i-au fredonat prima notă și a recunoscut imediat."
„Superparty a adus o mini-șaradă cu animale din fermă. Lui Cezar i-au dat „calul" și a imitat foarte bine."
„Mi-a plăcut că animatorii au ținut copiii în cerc, ca să nu se împingă. Ei, Rebecăi, i-au făcut loc lângă animator și a fost liniștită."
„Superparty a făcut un joc de „pasează balonul cu capul" (fără alergat). Lui Vladislav i-au arătat cum să împingă ușor și a mers perfect."
„Au făcut o activitate cu „desene pe post-it" și lipit pe un panou. Ei, Ralucăi, i-au dat post-it-uri colorate și a umplut panoul."
„Superparty a organizat un joc de memorie cu perechi de imagini. Lui Marius i-au dat primele două întoarceri și a găsit o pereche."
„Au avut un moment de „dans cu opriri" la semnal din palme. Ei, Florentinei, i-au arătat semnalul și a înghețat exact la timp."
„Superparty a propus un joc de „șoapte amuzante" cu cuvinte ușoare. Lui Radu i-au dat cuvântul „pinguin" și a stârnit râsete."
„Mi-a plăcut că au încurajat copiii mai timizi fără presiune. Ei, Iuliei, i-au oferit o sarcină mică și a prins curaj."
„Superparty a făcut „turnul prieteniei" din cuburi mari. Lui David i-au dat cubul de bază și a construit stabil."
„Au organizat o mini-ștafetă cu „du mingea în coș" pe rând. Ei, Georgianei, i-au arătat traseul și a mers atentă."
„Superparty a adus un joc de „cine lipsește?" (un copil iese, ceilalți ghicesc). Lui Petru i-au explicat regula și a ghicit rapid."
„Mi-a plăcut că au folosit și jocuri fără premii, doar pentru distracție. Ei, Carinei, i-au spus „bravo" pentru implicare și a zâmbit."
„Superparty a făcut un concurs de „balonul între genunchi" (mers încet). Lui Șerban i-au arătat poziția și a ajuns la final."
„Au avut un atelier de „semne de carte" cu abțibilduri. Ei, Danei, i-au tăiat colțurile rotunjit și a ieșit frumos."
„Superparty a început o poveste interactivă cu întrebări scurte. Lui Cristian i-au dat rolul de „erou" și a răspuns cu entuziasm."
„Au făcut un joc de „bule de săpun" cu rând pe rând. Ei, Amaliei, i-au dat bagheta prima și a fost încântată."
„Superparty a organizat „șotron" cu bandă pe podea (interior). Lui Nico i-au arătat unde sare și a respectat liniile."
„Mi-a plăcut că au respectat preferințele copiilor la muzică. Ei, Andreei, i-au pus o melodie preferată și a dansat imediat."
„Superparty a adus „pescuit magnetic" și puncte pe cartonașe. Lui Iosif i-au dat undița mai scurtă și a prins mai ușor."
„Au făcut un joc de „îmbrățișare de echipă" la finalul rundelor (opțional). Ei, Biancăi, i-au oferit alternativă cu „high-five" și a ales high-five."
„Superparty a propus „caută forma" (cerc, pătrat) prin cameră. Lui Teodor i-au dat prima provocare și a găsit un cerc rapid."
„Mi-a plăcut că au ținut ritmul fără să obosească copiii. Ei, Sânzianei, i-au oferit pauză scurtă și a revenit veselă."
„Superparty a făcut „baloane pe melodie" (când se oprește muzica, toți stau). Lui Gabriel i-au arătat semnul și a fost atent."
„Au avut o activitate de „colaj cu hârtie creponată". Ei, Laviniei, i-au ales culorile împreună și a ieșit un curcubeu."
„Superparty a organizat un joc de „aruncă inelul" pe sticle din plastic. Lui Denis i-au apropiat ținta și a prins din prima."
„Au făcut „ghicește mirosul" cu arome blânde (vanilie, lămâie). Ei, Darei, i-au dat o aromă ușoară și a ghicit corect."
„Superparty a propus „cursa cu obstacole" cu perne (foarte sigur). Lui Matteo i-au arătat unde calcă și a terminat fără probleme."
„Mi-a plăcut că animatorii au inclus și părinții 2 minute, la poză și aplauze. Ei, Otiliei, i-au dat o insignă mică și a fost mândră."
„Superparty a făcut un joc de „repede-încet" cu mișcări. Lui Adrian i-au dat exemplu și a schimbat ritmul corect."
„Au organizat „mini karaoke" cu versuri ușoare. Ei, Elizei, i-au ținut microfonul-jucărie și a cântat fără emoții."
„Superparty a adus „cărți cu provocări" (sari de 3 ori, bate din palme). Lui Paul i-au dat o provocare simplă și a executat perfect."
„Mi-a plăcut că au avut un colț de desen pentru cei care vor pauză. Ei, Mariei, i-au dus foi și creioane și a stat liniștită."
„Superparty a făcut „vânătoare de comori" cu indicii pe imagini. Lui Cosmin i-au dat indiciul cu „stea" și a găsit următorul punct."
„Au încheiat cu „felicitări pe rând" pentru fiecare copil. Ei, Adrianei, i-au spus o calitate concretă și a fost foarte fericită."
„Superparty a organizat un joc de „pasează cercul" fără să-ți dai drumul la mâini. Lui Valentin i-au explicat trucul și a mers din prima."
„Au făcut un atelier de „punguțe cu confetti" (hârtie, fără mizerie mare). Ei, Iasminei, i-au arătat cum să le sigileze și a reușit."
„Superparty a propus „cine imită sunetul?" (ploaie, vânt, tren). Lui Edi i-au dat „trenul" și a fost foarte amuzant."
„Mi-a plăcut că au folosit un limbaj foarte clar pentru copii mici. Ei, Ilincăi, i-au repetat regula pe calm și a înțeles."
„Superparty a făcut un joc de „numărătoare și sărituri" pe loc. Lui Iulian i-au ținut ritmul cu palme și a ținut pasul."
„Au organizat „puzzle rapid" cu imagini mari. Ei, Dacianei, i-au dat piesele potrivite și a terminat repede."
„Superparty a adus un joc de „mima obiectului" (periuță, umbrelă, carte). Lui Răzvan i-au dat „umbrelă" și a mimat perfect."
„Mi-a plăcut că au verificat din când în când dacă toți se distrează. Ei, Sofiei, i-au întrebat dacă vrea alt joc și a ales altceva."
„Superparty a făcut „cursa balonului pe sfoară" (tras ușor). Lui Damian i-au dat startul și a câștigat fără agitație."
„Au încheiat cu un moment de „poza de grup" și aplauze pentru sărbătorit. Ei, Doiniței, i-au aranjat coronița pentru poză și a ieșit superb."
„Superparty a făcut un joc de „statui muzicale" cu semnal de fluier. Lui Luca i-au arătat semnalul înainte și a reacționat perfect."
„Au organizat un atelier de „brățări din mărgele mari". Ei, Alinei, i-au ales mărgelele pe culori și a ieșit o brățară superbă."
„Superparty a propus „aruncă la țintă" cu bile moi în cutii numerotate. Lui Darius i-au pus o țintă mai aproape și a prins încredere."
„Au făcut o mini-vânătoare de comori cu indicii desenate. Ei, Irinei, i-au dat primul indiciu și a condus echipa."
„Superparty a avut un joc de „telefonul fără fir" cu propoziții scurte. Lui Victor i-au dat mesajul de început și s-a amuzat de rezultat."
„Au pus un colț de pictat cu bureței pe hârtie mare. Ei, Mirelei, i-au dat bureței în formă de inimă și a umplut foaia."
„Superparty a organizat „pasează mingea" doar pe sub picioare, în cerc. Lui Rareș i-au arătat mișcarea încet și a ținut ritmul."
„Au făcut un joc de „ghicește personajul" din desene, cu cartonașe. Ei, Ioanei, i-au arătat cartonașul discret și a ghicit imediat."
„Superparty a propus o cursă „cu pași de pitic" până la linie. Lui Ștefan i-au demonstrat pașii și a câștigat fără alergat."
„Au încheiat o rundă cu „aplauze în val" pentru fiecare copil. Ei, Emei, i-au spus pe nume și a fost foarte încântată."
„Superparty a adus un joc de „construiește un pod" din paie și bandă. Lui Patrick i-au dat rolul de „inginer" și a luat în serios."
„Au făcut „pictură pe balon" cu carioci lavabile. Ei, Biancăi, i-au desenat o față zâmbitoare și a păstrat balonul."
„Superparty a organizat „caută litera" (litere mari pe pereți). Lui Andrei i-au dat litera A și a găsit-o primul."
„Au avut un joc de „împarte echipele" cu panglici colorate. Ei, Danei, i-au prins panglica la mână și s-a simțit în echipă."
„Superparty a propus „aruncă și prinde" cu un cub de burete. Lui Călin i-au exersat prinderea de două ori și apoi a mers ușor."
„Au făcut un mini-show de „bule uriașe" și copiii le-au urmărit. Ei, Teodorei, i-au oferit loc în față ca să vadă bine."
„Superparty a organizat „ștafeta cu paharul" (transfer de apă cu linguriță, puțin). Lui Bogdan i-au spus să meargă încet și a reușit."
„Au propus „desenează cu ochii închiși" un animal simplu. Ei, Elenei, i-au dat „pisică" și desenul a ieșit amuzant."
„Superparty a făcut un joc de „pălăria care circulă" pe muzică. Lui Mihai i-au spus când să oprească muzica și a nimerit perfect."
„Au avut o activitate de „origami simplu" (avion). Ei, Larisei, i-au pliat colțurile împreună și avionul a zburat."
„Superparty a organizat „ghicește obiectul" dintr-un săculeț (fără sperieturi). Lui Ionuț i-au dat primul săculeț și a recunoscut mingea."
„Au făcut un joc de „spune o calitate" despre coleg (ghidat). Ei, Roxanei, i-au dat un exemplu și a spus ceva foarte frumos."
„Superparty a propus „cercul complimentelor" pentru sărbătorit. Lui Alex i-au dat primul compliment și s-a luminat la față."
„Au avut un atelier de „mini-poster" cu autocolante tematice. Ei, Patriciei, i-au oferit stickere extra și a decorat tot."
„Superparty a făcut „baloane la coș" cu aruncări ușoare. Lui Robert i-au ținut coșul mai jos și a marcat de mai multe ori."
„Au organizat un joc de „numărătoare pe ritm" cu bătăi din palme. Ei, Cătălinei, i-au ținut ritmul aproape și a ținut pasul."
„Superparty a propus „împarte cartonașele" (fiecare primește o misiune). Lui Mario i-au dat misiunea de a strânge cartonașele și a fost mândru."
„Au făcut „colaj cu forme" (triunghiuri, cercuri, pătrate). Ei, Oanei, i-au ales un șablon și a ieșit un soare perfect."
„Superparty a organizat „jocul liniștii" 20 de secunde, ca pauză. Lui Răzvan i-au spus că e o provocare și a fost super atent."
„Au încheiat cu un „dans în perechi" simplu, cu pași repetați. Ei, Anei, i-au ales o pereche potrivită și s-a simțit confortabil."
„Superparty a făcut un joc de „schimbă locul dacă..." (îți place înghețata). Lui Tudor i-au dat prima întrebare și a pornit jocul."
„Au organizat „mini-bowling" cu sticle și o minge moale. Ei, Nicoletei, i-au arătat cum să împingă mingea și a doborât 5."
„Superparty a propus „puzzle de echipă" pe podea, cu piese mari. Lui Emanuel i-au dat colțurile și a construit rapid cadrul."
„Au făcut un atelier de „măști" din carton cu elastic. Ei, Georgiei, i-au decupat ochii frumos și masca a stat perfect."
„Superparty a organizat „ghicește sunetul" (clopoțel, hârtie, tobă mică). Lui Șerban i-au dat toba și a bătut ritmul corect."
„Au propus „scrie-ți numele" cu litere din spumă. Ei, Mariei, i-au găsit toate literele și le-a lipit pe rând."
„Superparty a făcut „transportă balonul cu paleta" (farfurie de carton). Lui Denis i-au arătat echilibrul și a ajuns fără să-l scape."
„Au organizat „jocul umbrelor" cu lanterne pe perete (scurt și sigur). Ei, Iasminei, i-au făcut o inimă din mâini și a fost încântată."
„Superparty a propus „cine e liderul?" (toți copiază mișcările). Lui Florin i-au dat rolul de lider 30 de secunde și a fost fericit."
„Au încheiat cu „medalii" simbolice din hârtie pentru fiecare. Ei, Darei, i-au scris numele frumos și a păstrat medalia."
„Superparty a făcut un joc de „traseu cu culori" (pășești pe banda roșie, apoi albastră). Lui Sergiu i-au explicat traseul și a reușit fără greșeală."
„Au avut un atelier de „felicitare pentru sărbătorit" semnată de toți. Ei, Ilincăi, i-au dat un marker special și a scris cu grijă."
„Superparty a organizat „aruncă mingea la literă" (litere mari pe cutii). Lui Raul i-au dat litera din numele lui și a nimerit."
„Au propus „ghicește emoția" (fericit, surprins, somnoros) pe cartonașe. Ei, Evelinei, i-au arătat un exemplu și a imitat perfect."
„Superparty a făcut „cursa cu panglica" (tragi ușor panglica până vine premiul simbolic). Lui Cezar i-au dat panglica verde și a tras atent."
„Au organizat „joc cu baloane fără mâini" (doar cu umeri). Ei, Mihaelei, i-au arătat cum să împingă ușor și s-a descurcat."
„Superparty a propus „povestea pe rând" (fiecare adaugă un cuvânt). Lui Paul i-au dat începutul și povestea a ieșit foarte amuzantă."
„Au făcut „atelier de stele" din bețe și ață (simplificat). Ei, Amandei, i-au ținut bețele fixe și a înfășurat ața frumos."
„Superparty a organizat „jocul semaforului" (roșu-stai, verde-mergi). Lui Damian i-au dat rolul de semafor și a condus jocul."
„Au încheiat cu un „moment de mulțumire" și aplauze pentru sărbătorit. Ei, Sarei, i-au dat ultima îmbrățișare/alternativ high-five și a plecat zâmbind."
„Superparty a pornit un joc de „urmează liderul" cu mișcări simple. Lui Cătălin i-au dat rolul de lider 20 de secunde și a fost foarte mândru."
„Au făcut un atelier de „coroane" din carton și stickere. Ei Mariei i-au lipit elasticul la final și coroana a stat perfect."
„Superparty a organizat „ștafeta cu conuri" (ocolit conuri pe rând). Lui Iulian i-au arătat traseul o dată și a mers din prima."
„Au propus „ghicește animalul" după mimă. Ei Anastasiei i-au șoptit o idee și a imitat un iepuraș foarte amuzant."
„Superparty a făcut „pescuit" cu peștișori magnetici. Lui Sebastian i-au dat undița mai ușoară și a prins cei mai mulți."
„Au avut un colț de „pictat pe șabloane" cu fluturi și stele. Ei Daciei i-au ales un fluture mare și l-a colorat superb."
„Superparty a organizat „cursa cu balonul între genunchi". Lui Matei i-au spus să meargă încet și a ajuns fără să-l scape."
„Au făcut un joc de „recunoaște culoarea" cu cartonașe ridicate sus. Ei Aurorei i-au dat culoarea mov și a fost atentă tot jocul."
„Superparty a propus „aruncă inele" pe sticle de plastic. Lui Vlad i-au apropiat sticlele puțin și a reușit rapid."
„Au organizat „dans pe ziare" (spațiul se micșorează). Ei Deliei i-au explicat regula clar și s-a distrat fără stres."
„Superparty a făcut „construiește turnul" din pahare de carton. Lui Cosmin i-au dat primele pahare și a ridicat cel mai înalt turn."
„Au avut „atelier de slime" sigur (mini porții, supravegheat). Ei Rebecăi i-au oferit mănuși și a fost încântată."
„Superparty a organizat „căutarea comorii" cu indicii în rime. Lui Radu i-au dat primul indiciu și a condus echipa."
„Au propus „baloane pe ritm" (lovești balonul când bate muzica). Ei Andreei i-au arătat ritmul și a prins imediat."
„Superparty a făcut „mini-fotbal" cu porți mici din conuri. Lui Sorin i-au dat rolul de portar și s-a simțit important."
„Au organizat „pictură cu degetele" pe o foaie mare comună. Ei Larisei i-au dat colțul ei și a desenat o floare mare."
„Superparty a propus „ghicește personajul" dintr-o descriere scurtă. Lui Nicolae i-au dat descrierea și a ghicit super rapid."
„Au făcut „atelier de felicitări" cu sclipici lipit (controlat, fără mizerie). Ei Ioanei i-au pus lipiciul în puncte și a ieșit curat."
„Superparty a organizat „ștafeta cu lingura" (minge de ping-pong). Lui Denis i-au dat o lingură mai mare și a reușit."
„Au propus „jocul emoțiilor" cu fețe desenate pe cartonașe. Ei Cristinei i-au dat „surprinsă" și a jucat perfect rolul."
„Superparty a făcut „labirint din bandă" pe podea (mers pe linie). Lui Adrian i-au arătat startul și a mers până la capăt fără să iasă."
„Au organizat „colaj cu autocolante" pe temă de petrecere. Ei Ralucăi i-au dat setul cu stele și a decorat tot posterul."
„Superparty a propus „aruncă la coș" cu mingi moi. Lui Teodor i-au coborât coșul și a marcat de mai multe ori."
„Au făcut „jocul culorilor" cu eșarfe (ridică eșarfa când auzi culoarea). Ei Sofiei i-au dat eșarfa roz și a fost super atentă."
„Superparty a organizat „pantomimă în echipă" cu cuvinte ușoare. Lui Gabriel i-au dat „tren" și a fost foarte comic."
„Au avut un „atelier de măști" cu elastice moi. Ei Biancăi i-au fixat elasticul corect și masca nu a deranjat-o."
„Superparty a făcut „cursa cu obstacole" (treci peste pernuțe). Lui Florin i-au arătat obstacolul pe rând și a prins curaj."
„Au organizat „povești pe imagini" (alegi o imagine și continui povestea). Ei Daniellei i-au ales imaginea cu curcubeu și a inventat frumos."
„Superparty a propus „puzzle rapid" cu piese mari. Lui Ilias i-au dat piesele de margine și a terminat repede."
„Au făcut „dans cu panglici" pe muzică lentă. Ei Mirelei i-au dat panglica mov și a arătat ca într-un spectacol."
„Superparty a organizat „prinde coada" (panglică la brâu, joc blând). Lui Ovidiu i-au prins panglica bine și a alergat cu grijă."
„Au propus „ghicește obiectul" din imagine mărită. Ei Elizei i-au dat prima imagine și a ghicit corect."
„Superparty a făcut „turn de cuburi" pe timp (fără presiune). Lui Dorian i-au pus cronometrul ca joacă și s-a motivat."
„Au organizat „atelier de brățări" cu șnur și mărgele mari. Ei Iuliei i-au ales culorile preferate și brățara a ieșit superbă."
„Superparty a propus „ștafeta cu balonul pe paletă" (farfurie carton). Lui Emanuel i-au arătat echilibrul și nu l-a scăpat deloc."
„Au făcut „desene pe asfalt" cu cretă (dacă spațiul permite). Ei Alinei i-au dat creta albastră și a desenat un nor uriaș."
„Superparty a organizat „jocul semaforului" cu comenzi clare. Lui Robert i-au dat rolul de „verde" și a condus cu seriozitate."
„Au propus „mini-karaoke" cu versuri foarte scurte. Ei Antoniai i-au ales un refren ușor și a cântat cu zâmbetul pe buze."
„Superparty a făcut „aruncă bilele în cutii" numerotate. Lui Cristian i-au pus cutia mai aproape și a prins încredere."
„Au organizat „atelier de confetti" din hârtie colorată (tăiat sigur). Ei Iasminei i-au dat perforatorul și a fost încântată."
„Superparty a propus „mima meseriilor" (doctor, pompier, bucătar). Lui Patrick i-au dat „pompier" și a fost foarte convingător."
„Au făcut „pictură cu bureței" pe un banner mare. Ei Nicoletei i-au dat buretele în formă de inimă și a umplut spațiul frumos."
„Superparty a organizat „cursa cu sărituri mici" pe cercuri desenate. Lui Ștefan i-au arătat ritmul și a terminat fără să se împiedice."
„Au propus „ghicește sunetul" cu instrumente mici. Ei Georgiei i-au dat clopoțelul și a recunoscut sunetul imediat."
„Superparty a făcut „transportă mingea" cu o cupă de plastic (ușor). Lui Bogdan i-au explicat să meargă încet și a reușit perfect."
„Au organizat „jocul culorilor" cu cercuri pe podea. Ei Patriciei i-au arătat cercul verde și a prins regula rapid."
„Superparty a propus „îngheață-dezgheață" pe muzică. Lui Mihnea i-au dat semnalul de „stop" și s-a amuzat enorm."
„Au făcut „atelier de decupaj" (forme simple) cu lipici. Ei Dorei i-au pregătit formele și le-a lipit foarte ordonat."
„Superparty a organizat „pasează obiectul" pe muzică, în cerc. Lui Valentin i-au dat startul și jocul a mers fluent."
„Au încheiat cu „diplome" simbolice pentru fiecare copil. Ei Alessiei i-au scris numele frumos și a plecat super fericită."
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
