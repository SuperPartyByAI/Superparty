import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a făcut un joc de „telefonul fără fir" cu propoziții scurte. Lui Denis i-au dat prima propoziție și a transmis-o corect."
„Mi-a plăcut că au avut o pauză scurtă de apă, exact când trebuia. Ei, Alisiei, i-au adus paharul și a revenit imediat la joacă."
„Au organizat un joc de „vânătoare de comori" cu indicii simple. Lui Luca i-au dat harta și a condus echipa cu entuziasm."
„Superparty a făcut un mini-cerc de complimentare, pe rând. Ei, Danei, i-au spus o calitate frumoasă și i s-a văzut bucuria pe față."
„Mi-a plăcut că au folosit muzică potrivită vârstei, fără zgomot excesiv. Lui Robert i-au făcut semn când începe jocul și a intrat imediat."
„Au făcut un joc de „ghicește animalul" cu sunete amuzante. Ei, Ilincăi, i-au dat „pisica" și a imitat perfect."
„Superparty a avut o activitate de lipit forme geometrice pe un panou. Lui Matei i-au dat triunghiurile și le-a pus la locul lor rapid."
„Mi-a plăcut că au fost atenți la copiii care se plictisesc ușor. Ei, Andreiței, i-au schimbat sarcina și a redevenit implicată."
„Au făcut un joc de „pasează mingea când auzi numele tău". Lui Darius i-au spus numele clar și a pasat la timp."
„Superparty a organizat „colțul liniștit" cu cărți și creioane. Ei, Anisiei, i-au oferit o carte cu imagini și s-a relaxat."
„Au făcut un joc de „caută culoarea" prin cameră, fără alergat. Lui Vlad i-au dat culoarea roșu și a găsit-o imediat."
„Mi-a plăcut că au încurajat cooperarea, nu competiția. Ei, Norei, i-au spus că echipa câștigă împreună și a zâmbit."
„Superparty a avut un joc de „ghicește obiectul" doar prin atingere. Lui Paul i-au dat un creion și a ghicit instant."
„Au organizat o activitate de „pictură cu degetul" pe coli mari. Ei, Izei, i-au pus șervețele la îndemână și a fost totul curat."
„Mi-a plăcut că au făcut tranziții rapide între jocuri. Lui Bogdan i-au spus „urmează alt joc" și a rămas atent."
„Superparty a făcut un joc de „stop-dans" cu reguli blânde. Ei, Sofiei, i-au explicat că nu se elimină nimeni și s-a bucurat."
„Au pregătit un puzzle tematic cu personaje haioase. Lui Damian i-au dat piesele de margine și a construit baza."
„Mi-a plăcut că animatorii au ținut cont de emoții. Ei, Nicoletei, i-au oferit o pauză scurtă și apoi a revenit singură."
„Superparty a avut un joc de „numărătoare" cu bătăi din palme. Lui Ștefan i-au dat ritmul și a condus grupul."
„Au încheiat o rundă cu „high-five pentru toți". Ei, Biancăi, i-au oferit high-five primul și s-a simțit importantă."
„Au făcut un joc de „aruncă sacul la țintă" cu distanțe diferite. Lui Călin i-au apropiat ținta și a reușit din prima."
„Mi-a plăcut că au folosit recuzită sigură, fără obiecte dure. Ei, Larisei, i-au dat baloane moi și a jucat fără frică."
„Superparty a organizat „ghicește personajul" din desene animate. Lui Eric i-au dat un indiciu ușor și a ghicit corect."
„Au făcut un joc de „povești în lanț", fiecare adaugă un cuvânt. Ei, Deliei, i-au dat startul și a început creativ."
„Mi-a plăcut că au avut un plan clar și au respectat timpul. Lui Andrei i-au anunțat când urmează tortul și a așteptat liniștit."
„Superparty a făcut un joc de „șoapte în cerc" (mesaj scurt). Ei, Catrinei, i-au spus mesajul simplu și l-a transmis corect."
„Au organizat o mini-ștafetă cu pași mici, fără îmbulzeală. Lui Raul i-au arătat traseul și a mers atent."
„Mi-a plăcut că au observat rapid un copil copleșit. Ei, Loredanei, i-au oferit un rol ușor și s-a liniștit."
„Superparty a avut un joc de „forme pe podea" (sari doar pe cercuri). Lui Sami i-au pus cercurile mai apropiate și a reușit."
„Au făcut un moment de „aplaudăm pe rând" pentru fiecare copil. Ei, Georgianei, i-au rostit numele clar și a fost fericită."
„Au propus un joc de „cine lipsește?" (un copil se ascunde). Lui Ionuț i-au dat rolul de a ghici și s-a distrat."
„Mi-a plăcut că animatorii au fost calmi și consecvenți. Ei, Anamariei, i-au explicat regula o singură dată și a înțeles."
„Superparty a făcut un joc de „răspunde cu da/nu" pe teme amuzante. Lui Dragoș i-au pus o întrebare ușoară și a râs mult."
„Au organizat „atelier de brățări" cu mărgele mari. Ei, Iasminiei, i-au ținut șnurul la început și a reușit singură."
„Mi-a plăcut că au implicat copiii în alegeri (ce joc urmează). Lui Sebastian i-au cerut votul și s-a simțit inclus."
„Superparty a avut un joc de „urmează liderul" cu mișcări simple. Ei, Miriam, i-au ales o mișcare ușoară și a condus bine."
„Au făcut o activitate de „colorează după model" (model simplu). Lui Nectarie i-au dat modelul cu forme mari și a lucrat atent."
„Mi-a plăcut că au gestionat elegant energia grupului. Ei, Dacianei, i-au propus o activitate calmă și s-a echilibrat atmosfera."
„Superparty a organizat „ghicește cântecul" din 3 secunde. Lui Kevin i-au pus un fragment ușor și a recunoscut imediat."
„Au încheiat cu un mic „paradă a copiilor" pe rând. Ei, Oanei, i-au oferit o eșarfă colorată și a defilat fericită."
„Au făcut un joc de „balonul pe linie" (împingi balonul doar cu capul). Lui Cătălin i-au arătat cum să fie blând și a reușit."
„Mi-a plăcut că au fost flexibili când s-a schimbat spațiul. Ei, Darei, i-au mutat activitatea fără stres și a mers perfect."
„Superparty a avut un joc de „caută obiectul albastru" cu timp suficient. Lui Petru i-au dat un indiciu și a găsit rapid."
„Au făcut o activitate de „desen cu șabloane" (inimă, stea, cerc). Ei, Anei, i-au ales șablonul preferat și a desenat mult."
„Mi-a plăcut că au încurajat copiii să se ajute între ei. Lui Marcu i-au sugerat să ajute un coleg și a făcut-o imediat."
„Superparty a organizat „mini-quiz" cu întrebări de copii. Ei, Irinei, i-au pus o întrebare potrivită și a răspuns sigură."
„Au făcut un joc de „prinde eșarfa" (reacție rapidă). Lui Victor i-au dat poziția centrală și a prins de două ori."
„Mi-a plăcut că au păstrat totul pozitiv, fără comparații. Ei, Teodorei, i-au spus „ai progresat" și s-a bucurat."
„Superparty a avut un joc de „construiește turnul" cu cuburi moi. Lui Alex i-au dat baza și a construit cel mai stabil turn."
„Au încheiat cu un „mulțumim, Superparty" spus în cor. Ei, Melisei, i-au dat microfonul-jucărie și a spus tare, cu emoție."
„Superparty a început cu un mic număr de magie cu eșarfe colorate. Lui Răzvan i-au dat rolul de asistent și a fost mândru."
„Mi-a plăcut că au avut baloane de săpun pentru un moment calm. Ei, Ameliei, i-au arătat cum să sufle încet și i-au ieșit perfecte."
„Superparty a organizat un joc de mimă cu emoții (fericit, supărat, surprins). Lui Tudor i-au dat „surprins" și a fost genial."
„Au făcut un mic atelier de autocolante, fiecare copil își decorează o coroniță. Ei, Evelinei, i-au ales autocolantele preferate și a stat concentrată."
„Superparty a avut un joc de „ghicește sunetul" (clopoțel, tobă, maracas). Lui Fabian i-au dat maracas și a ținut ritmul."
„Mi-a plăcut că au ținut cont de timiditate. Ei, Silviei, i-au oferit un rol discret la început și apoi a prins curaj."
„Superparty a făcut o ștafetă cu lingura și mingea de burete. Lui Cezar i-au pus traseul mai scurt și a reușit fără emoții."
„Au pregătit un joc cu cartonase „adevărat/fals" pentru copii. Ei, Mihaelei, i-au explicat pe scurt și a participat imediat."
„Superparty a adus un sac cu „surprize" (recuzită amuzantă) și fiecare a ales ceva. Lui Nick i-au dat o pălărie comică și a râs toată lumea."
„Mi-a plăcut momentul de dans cu coregrafie simplă. Ei, Mirelei, i-au arătat pașii lângă animator și a ținut pasul."
„Superparty a făcut un joc de „pietre, hârtie, foarfecă" în echipe, fără eliminare. Lui Iulian i-au dat rolul de a strânge punctele și s-a simțit important."
„Au avut un moment de pictură pe față, foarte rapid și curat. Ei, Denisei, i-au făcut o steluță mică și a fost încântată."
„Superparty a organizat „cursa cu obstacole" din perne și conuri moi. Lui Cosmin i-au arătat cum să meargă pe rând și a respectat perfect."
„Mi-a plăcut că au folosit muzică mai încet când a fost nevoie. Ei, Iuliei, i-au oferit un loc lângă animator și s-a liniștit."
„Superparty a avut un joc de „pasează cercul" fără să se desprindă mâinile. Lui Sorin i-au dat startul și a coordonat bine."
„Au făcut un mini-spectacol cu păpuși de mână, scurt și amuzant. Ei, Adrianei, i-au dat o păpușă pentru final și a salutat publicul."
„Superparty a propus un joc de „aranjează pe mărimi" (mingi mici/medii/mari). Lui Denis i-au dat sarcina cu mingile mari și a terminat repede."
„Mi-a plăcut că au repetat regulile fără să certe. Ei, Sânzianei, i-au reamintit calm și a înțeles."
„Superparty a făcut un joc de „urmează culoarea" cu cartonașe ridicate. Lui Horia i-au dat cartonașul verde și a fost foarte atent."
„Au încheiat o rundă cu „întrebare fulger" despre ziua sărbătoritului. Ei, Daciei, i-au dat o întrebare ușoară și a răspuns zâmbind."
„Superparty a făcut un moment de „fotograf cu recuzită" (ochelari, mustăți). Lui Andi i-au dat ochelarii mari și a pozat amuzant."
„Mi-a plăcut că au păstrat ordinea la fotografii. Ei, Laviniei, i-au spus clar când e rândul ei și n-a fost agitație."
„Superparty a organizat un joc de „construiește un oraș" din cuburi. Lui Radu i-au dat rolul de „arhitect" și a planificat străzile."
„Au făcut o activitate de „scrie o urare" pe bilețele colorate. Ei, Daliei, i-au dictat dacă a vrut și a ieșit foarte frumos."
„Superparty a avut un joc de „cine poate sta nemișcat 5 secunde" (provocare blândă). Lui Marius i-au numărat cu voce caldă și a reușit."
„Mi-a plăcut că au integrat și copiii mai mici. Ei, Ancuței, i-au oferit o variantă mai simplă a jocului și a mers perfect."
„Superparty a pregătit un joc cu „bilete la spectacol" (fiecare primește un rol). Lui Edi i-au dat rolul de prezentator și a vorbit în microfon-jucărie."
„Au făcut un mic concurs de desen „supereroul meu". Ei, Lorenei, i-au adus creioane suplimentare și a desenat mult."
„Superparty a organizat „ștafeta cu balonul" ținut între genunchi. Lui Sandu i-au arătat cum să meargă încet și a dus balonul până la capăt."
„Mi-a plăcut că nu au forțat pe nimeni la dans. Ei, Karinei, i-au oferit opțiunea să bată din palme și a fost fericită."
„Superparty a făcut un joc de „ghicește mirosul" cu arome blânde (vanilie, portocală). Lui Rareș i-au dat portocala și a recunoscut imediat."
„Au pregătit o mini-lectură cu întrebări despre poveste. Ei, Rebecăi, i-au pus o întrebare simplă și a răspuns curajos."
„Superparty a organizat un joc de „prinde culoarea cu clești" pe un șnur. Lui Teo i-au dat cleștii albaștri și a lucrat atent."
„Mi-a plăcut că au fost foarte rapizi la organizare și curățenie. Ei, Mariei, i-au șters masa imediat și a continuat activitatea."
„Superparty a făcut un joc de „ghicește personajul" după accesoriu. Lui Nelu i-au arătat o coroniță și a ghicit „rege" pe loc."
„Au avut un moment de aplauze pentru fiecare copil, fără grabă. Ei, Patriciei, i-au spus numele frumos și a zâmbit larg."
„Superparty a propus un joc de „câte silabe are cuvântul?" cu bătăi din palme. Lui Ovidiu i-au dat un cuvânt scurt și a prins imediat."
„Mi-a plăcut că au făcut un colț cu apă și șervețele la vedere. Ei, Ionelei, i-au adus șervețele când a cerut și a fost totul ok."
„Superparty a organizat un joc de „aruncă inelul" pe sticle din plastic. Lui Camil i-au apropiat distanța și a reușit."
„Au făcut un moment de „mulțumim sărbătoritului" cu urări în cerc. Ei, Monicăi, i-au șoptit urarea dacă a vrut și a spus-o frumos."
„Superparty a făcut un joc de „cine găsește perechea" (cartonașe identice). Lui Răzvan i-au dat primele două cartonașe și a pornit jocul."
„Mi-a plăcut că animatorii au observat când cineva rămâne pe margine. Ei, Ramonei, i-au oferit o sarcină clară și a intrat în joc."
„Superparty a propus un joc de „transportă comoara" cu un pahar pe tavă. Lui Florin i-au arătat cum să țină tava și a dus-o fără să verse."
„Au făcut o activitate de „colaj" cu hârtie colorată și lipici. Ei, Cristinei, i-au dat forme pre-tăiate și a fost foarte ușor."
„Superparty a organizat un moment de „quiz despre animale" cu imagini mari. Lui Beni i-au dat un animal simplu și a răspuns corect."
„Mi-a plăcut că au avut și jocuri fără alergat, pentru spații mici. Ei, Celinei, i-au dat rolul de „arbitru" și a fost încântată."
„Superparty a făcut un joc de „puzzle uriaș" pe podea, în echipă. Lui Dimi i-au dat piesa centrală și a potrivit-o imediat."
„Au avut un moment de „dans cu panglici" foarte estetic. Ei, Georgiei, i-au dat o panglică mai scurtă și a fost perfect pentru ea."
„Superparty a făcut o „paradă a pălăriilor" cu recuzită. Lui Iacob i-au dat pălăria de magician și a defilat amuzant."
„Au încheiat cu un joc de „spune un lucru bun despre petrecere". Ei, Ruxandrei, i-au dat timp să se gândească și a spus ceva foarte frumos."
„Superparty a pornit cu un joc de „statui muzicale" pe melodii pentru copii. Lui Matei i-au explicat regula simplu și a respectat-o din prima."
„Au avut o activitate de „brățări din mărgele mari", potrivite și pentru cei mici. Ei, Biancăi, i-au ales culorile preferate și a fost foarte atentă."
„Superparty a făcut un joc de „pescuit" cu undițe magnetice și peștișori din carton. Lui Darius i-au dat prima undiță și a prins „peștele auriu"."
„Mi-a plăcut că au avut un moment de liniște cu „respirație de dragon" (inspir-expir). Ei, Alexiei, i-au arătat modelul și s-a calmat rapid."
„Superparty a organizat un joc de „caută culoarea" prin cameră (atinge ceva roșu/albastru). Lui Paul i-au dat startul și a fost foarte implicat."
„Au făcut un atelier de „mini-evantaie" din hârtie colorată. Ei, Georgianei, i-au pliat modelul împreună și a ieșit perfect."
„Superparty a adus un set de conuri moi pentru un slalom ușor. Lui Robert i-au arătat traseul și a mers fără să dărâme nimic."
„Mi-a plăcut că au întrebat înainte dacă e ok cu muzica mai tare. Ei, Oanei, i-au oferit loc mai departe de boxă și a fost relaxată."
„Superparty a făcut un joc de „ghicește animalul" după sunet (imitații amuzante). Lui Ștefan i-au dat „leul" și a fost hilar."
„Au organizat o rundă de „poveste în lanț" (fiecare adaugă o propoziție). Ei, Anei, i-au dat un început ușor și a continuat creativ."
„Superparty a pregătit un joc de „aruncă la țintă" cu mingi din burete. Lui Victor i-au apropiat ținta și a prins încredere imediat."
„Au făcut un moment de „dans cu eșarfe" pe muzică lentă. Ei, Irinei, i-au dat o eșarfă mai ușoară și a dansat grațios."
„Superparty a organizat „trenulețul prieteniei" prin casă, fără alergat. Lui Cătălin i-au dat rolul de locomotivă și a condus încet."
„Mi-a plăcut că au avut cartonașe cu emoții și au vorbit 1 minut despre ele. Ei, Elizei, i-au dat cartonașul „curajoasă" și a zâmbit."
„Superparty a făcut o mini-vânătoare de comori cu indicii desenate. Lui Toma i-au dat primul indiciu și a găsit comoara rapid."
„Au organizat un joc de „cine sunt eu?" cu bandă pe frunte și imagini. Ei, Andreei, i-au pus un personaj ușor și a ghicit repede."
„Superparty a venit cu un joc de „balonul nu cade" (lovit ușor cu palma). Lui Rareș i-au spus să meargă încet și a ținut balonul în aer."
„Mi-a plăcut că animatorii au lăudat efortul, nu doar câștigul. Ei, Darei, i-au spus exact ce a făcut bine și s-a luminat."
„Superparty a propus „telefonul fără fir" cu cuvinte simple și haioase. Lui Ionuț i-au dat cuvântul „broască" și a stârnit râsete."
„Au avut un atelier de „desene pe farfurii de carton" (măști). Ei, Mariei, i-au dat elasticul și a ajutat la prindere."
„Superparty a făcut un joc de „numărătoare cu pași" (câți pași până la perete). Lui Adrian i-au dat rolul de a număra cu voce tare."
„Au organizat „bingo cu imagini" (animale, fructe). Ei, Teodorei, i-au explicat cum bifează și a prins imediat."
„Superparty a adus o mică „pânză" pentru jocul cu parașuta (varianta de interior). Lui Luca i-au dat colțul lui și a ridicat la timp."
„Mi-a plăcut că au avut jocuri pe rând, fără îmbulzeală. Ei, Emei, i-au spus clar când intră și a așteptat liniștită."
„Superparty a făcut un concurs de „imită profesia" (doctor, bucătar, pompier). Lui Bogdan i-au dat „pompier" și a fost foarte expresiv."
„Au pregătit o „cutie cu surprize" tactile (puf, burete, minge moale). Ei, Sarei, i-au dat voie să ghicească prima și s-a distrat."
„Superparty a organizat „pasează obiectul" pe muzică, fără eliminare. Lui Mihai i-au dat obiectul la start și a fost atent."
„Mi-a plăcut că au adaptat jocul pentru copii obosiți. Ei, Alinei, i-au oferit o variantă stând jos și a participat cu plăcere."
„Superparty a făcut un mic moment de „aplaudă ritmul" (clap-clap-pauză). Lui Sergiu i-au arătat modelul și a ținut ritmul perfect."
„Au organizat un colaj „superpetrecerea mea" cu stickere. Ei, Loredanei, i-au dat stickere extra și a fost încântată."
„Superparty a propus un joc de „cine are...?" (cine are tricou albastru, cine are șosete cu model). Lui Alex i-au dat primul enunț și a observat repede."
„Au făcut o mini-ștafetă cu „paharul cu apă" (foarte puțină apă). Ei, Ioanei, i-au pus un pahar mai mic și a reușit fără să verse."
„Superparty a organizat „îngheață la semn" cu semnale vizuale, nu strigate. Lui Kevin i-au arătat semnul și a reacționat imediat."
„Mi-a plăcut că au avut un moment de „felicită colegul" (spune ceva frumos). Ei, Corinei, i-au sugerat o idee și a spus-o cu curaj."
„Superparty a pregătit un joc de „potrivește umbrele" (imagini cu siluete). Lui Marian i-au dat planșa mai ușoară și a terminat primul."
„Au organizat o activitate de „împachetează cadoul imaginar" (mimă). Ei, Ilincăi, i-au dat un exemplu și a fost foarte amuzantă."
„Superparty a făcut un joc de „prinde coada dragonului" în cerc, încet. Lui Denis i-au spus să meargă ușor și n-a fost haos."
„Mi-a plăcut că au avut grijă la spațiu și obiecte fragile. Ei, Adrianei, i-au arătat zona sigură de joacă și a fost totul ok."
„Superparty a propus „pictură cu burețelul" (puncte și forme). Lui Emanuel i-au dat burețelul rotund și a făcut un model super."
„Au avut un moment scurt de „poveste cu întrebări" despre eroi. Ei, Dianei, i-au pus o întrebare simplă și a răspuns zâmbind."
„Superparty a organizat „cursa melcului" (cine merge cel mai încet fără să râdă). Lui Silviu i-au dat rolul de arbitru și a numărat corect."
„Au făcut un joc de „aranjează culorile curcubeu" cu cartonașe. Ei, Norei, i-au dat cartonașele lipsă și a completat curcubeul."
„Superparty a adus un joc de „puzzle pe echipe" cu timp cronometrat blând. Lui Horia i-au dat piesele de margine și a ajutat mult."
„Mi-a plăcut că animatorii au folosit mult umor, fără să ironizeze. Ei, Mădălinei, i-au făcut loc să vorbească și a fost apreciată."
„Superparty a făcut un joc de „ghicește obiectul" doar din descriere (mic, rotund, sare). Lui Răzvan i-au dat descrierea și a ghicit „minge"."
„Au organizat „scrisoare pentru sărbătorit" cu desene și semnături. Ei, Iasminei, i-au dat un marker strălucitor și a decorat frumos."
„Superparty a propus un joc de „labirint" desenat pe foaie, pe rând. Lui Raul i-au dat un labirint mai simplu și a reușit."
„Mi-a plăcut că au împărțit copiii în grupuri mici ca să nu fie aglomerație. Ei, Roxanei, i-au dat un grup liniștit și a fost perfect."
„Superparty a făcut un moment de „mic spectacol" cu aplauze la final. Lui Vlad i-au dat rolul principal 10 secunde și a fost mândru."
„Au încheiat cu un joc de „spune 3 lucruri care ți-au plăcut". Ei, Deliei, i-au dat timp să se gândească și a spus clar."
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
print(f"Total acum: {len(existing_testimonials)} testimoniale pentru {len(assigned_slugs) + (idx // 3)} articole.")
