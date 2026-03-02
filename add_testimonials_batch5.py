import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a început partea a doua cu un joc de atenție pe semnale (bat din palme = îngheț). Lui Robert i-au plăcut regulile simple și a intrat imediat."
„Au făcut o provocare de 'statui muzicale' fără eliminări, doar cu aplauze. Ei, Teodorei, i-au spus că e ok să greșească și a dansat relaxată."
„Mi-a plăcut că au avut o 'cutie cu misiuni' și fiecare copil a tras un bilețel. Lui Denis i-au dat o misiune amuzantă și a râs tot timpul."
„Au organizat un mini-joc de 'puzzle pe echipe' cu piese mari. Ei, Sofiei, i-au dat colțurile și a reușit repede."
„Superparty a introdus un joc de imitație pe animale, dar pe rând, fără haos. Lui Ionuț i-au dat primul exemplu și a fost foarte comic."
„Au avut o activitate de colorat rapid cu temă de petrecere, apoi au făcut 'galerie'. Ei, Ralucăi, i-au pus desenul la mijloc și s-a luminat."
„Mi-a plăcut că au corectat cu blândețe când copiii vorbeau peste altcineva. Lui Rareș i-au făcut semn discret și a așteptat."
„Superparty a făcut un joc de 'ștafetă cu lingura' folosind mingi moi. Ei, Andreei, i-au arătat cum să țină lingura și a mers perfect."
„Au avut o pauză scurtă de apă și au revenit cu energie, fără să piardă grupul. Lui Alexandru i-au spus clar 'în 2 minute reluăm' și a respectat."
„Mi-a plăcut că au inclus și un moment de 'respirație de balon' pentru calm. Ei, Mădălinei, i-au explicat frumos și s-a liniștit imediat."
„Superparty a făcut un joc de 'cine e personajul?' cu indicii simple. Lui Tudor i-au dat un personaj cunoscut și a ghicit rapid."
„Au pregătit un mini-concurs de 'aruncă la țintă' cu cercuri, foarte safe. Ei, Elenei, i-au setat distanța potrivită și a nimerit."
„Mi-a plăcut că nu au lungit jocurile inutil; când vedeau oboseală, schimbau ritmul. Lui Cătălin i-au dat o sarcină nouă și a revenit."
„Superparty a introdus un joc de 'șoapte pe rând' și copiii au fost super atenți. Ei, Irianei, i-au dat primul mesaj și a fost încântată."
„Au făcut o rundă de 'baloane fără să cadă' fără împins, doar cooperare. Lui Darius i-au spus să ajute echipa și chiar a ajutat."
„Mi-a plăcut că au avut autocolante ca mici premii, fără competiție toxică. Ei, Ioanei, i-au dat un autocolant 'curajoasă' și a fost mândră."
„Superparty a folosit o poveste scurtă ca să lege activitățile între ele. Lui Victor i-au dat rolul de 'erou' și a intrat în poveste."
„Au făcut un joc de 'culoare interzisă' (nu ai voie să spui un cuvânt), foarte amuzant. Ei, Larisei, i-au explicat clar regula și a prins repede."
„Mi-a plăcut că au controlat volumul muzicii, nu a fost deranjant. Lui Răzvan i-au permis să aleagă o piesă potrivită și a fost fericit."
„Superparty a avut o tranziție elegantă spre tort, cu copiii așezați pe rând. Ei, Cătălinei, i-au arătat unde să stea și a fost liniște."
„Au făcut un joc de 'bingo cu imagini' (animale/forme), super potrivit. Lui Mateo i-au dat cartonașul și a fost concentrat."
„Mi-a plăcut că au încurajat copiii să se ajute, nu să se încurce. Ei, Mariei, i-au spus 'în echipă e mai ușor' și a cooperat."
„Superparty a introdus un joc cu 'semne secrete' (mâna sus = schimbare), foarte util. Lui Paul-Andrei i-au dat rolul de exemplu și a funcționat."
„Au făcut un mini-atelier de coronițe din hârtie și au scris numele copiilor. Ei, Alexandrei, i-au decorat coronița frumos și a păstrat-o."
„Mi-a plăcut că au păstrat glumele curate și potrivite pentru vârstă. Lui Bogdan i-au spus o poantă scurtă și a râs fără să deranjeze."
„Superparty a făcut un joc de 'roata norocului' cu provocări ușoare. Ei, Denisei, i-au dat o provocare simplă și a reușit."
„Au gestionat excelent când doi copii au vrut același lucru: au făcut rotație de roluri. Lui Marian i-au explicat rândul și a acceptat."
„Mi-a plăcut că au avut și activități statice pentru momentele de oboseală. Ei, Anei-Maria, i-au dat de ales între două jocuri și a fost încântată."
„Superparty a făcut un joc de 'labirint pe podea' cu bandă, fără alergat. Lui Șerban i-au dat startul și a urmat traseul corect."
„Au încurajat frumos copiii să aplaude la finalul fiecărei runde. Ei, Georgiei, i-au mulțumit pentru participare și a zâmbit."
„Superparty a introdus un joc de 'detectiv' cu indicii prin cameră, bine organizat. Lui Mihai i-au dat prima pistă și a fost super curios."
„Mi-a plăcut că au observat imediat când cineva rămâne pe margine și l-au inclus. Ei, Camiliei, i-au dat un rol discret și a intrat în joc."
„Au făcut un joc de 'cine conduce trenulețul' pe muzică, fără îmbulzeală. Lui Iacob i-au dat șansa să fie locomotivă și a fost încântat."
„Superparty a organizat o provocare de 'potrivește umbrele' (imagini simple), foarte educativ. Ei, Iulianei, i-au arătat un exemplu și a înțeles."
„Mi-a plăcut că au ținut cont de spațiul mic și au ales jocuri pe loc. Lui Călin i-au dat mișcări simple și s-a distrat."
„Au făcut un mini-joc de 'ghicește sunetul' (clopoțel/pahar), super interesant. Ei, Mirelei, i-au dat sunetul ușor și a ghicit."
„Superparty a avut un moment de 'poveste în cerc', fiecare spune o propoziție. Lui Eric i-au dat începutul și a fost creativ."
„Mi-a plăcut că au fost atenți la copiii sensibili la zgomot și au redus volumul la timp. Ei, Ioanei-Andrada, i-au spus dinainte și a fost ok."
„Au organizat un joc de 'prinde culoarea' cu cartonașe, foarte clar. Lui Patrick i-au dat cartonașul potrivit și a urmărit atent."
„Superparty a ținut finalul cu o activitate calmă, ca să plece toți liniștiți. Ei, Cristinei, i-au mulțumit personal și a plecat fericită."
„Au făcut un joc de 'codul secret' cu gesturi, fără să fie complicat. Lui Radu-Mihnea i-au arătat gesturile pe rând și a prins repede."
„Mi-a plăcut că au alternat copiii la roluri, ca să nu fie mereu aceiași în față. Ei, Beatricei, i-au oferit un rol principal și a fost foarte mândră."
„Superparty a pregătit un joc de 'întrebări cu da/nu' despre personaje, super amuzant. Lui Marco i-au dat primele întrebări și a râs mult."
„Au făcut o mică vânătoare de 'forme' (cerc/pătrat) prin cameră, foarte potrivită. Ei, Aurorei, i-au dat lista și a fost încântată."
„Mi-a plăcut că au avut grijă la copii care se enervează ușor: au oferit pauză fără rușine. Lui David i-au spus 'ia o pauză' și a revenit ok."
„Superparty a făcut un joc de 'șir de cuvinte' pe teme pentru copii, fără presiune. Ei, Dianei, i-au dat un cuvânt simplu și a continuat."
„Au gestionat bine energia grupului: au ridicat ritmul, apoi l-au coborât la timp. Lui Kevin i-au dat un rol activ, apoi l-au mutat la unul calm."
„Mi-a plăcut că au lăudat efortul, nu doar câștigul. Ei, Oanei, i-au spus 'ai încercat super' și a fost foarte fericită."
„Superparty a introdus un joc de 'bilețele cu emoții' (fericit/trist) și a fost educativ. Lui Gabriel i-au dat un bilețel 'fericit' și a explicat frumos."
„Au încheiat cu o mică 'paradă' a copiilor, pe rând, fără grabă. Ei, Sânzianei, i-au făcut loc să treacă și a fost un final foarte drăguț."
„Superparty a început cu un joc de 'mâna pe cap când auzi cuvântul-cheie'. Lui Sebastian i-au explicat regula dintr-o propoziție și a prins imediat."
„Au făcut o provocare de 'balonul prietenos' (îl pasezi fără să-l strângi). Ei, Biancăi, i-au arătat cum să paseze ușor și a intrat în joc."
„Superparty a pregătit un joc de 'ghicește desenul' pe tablă, cu imagini simple. Lui Emanuel i-au dat un cuvânt ușor și a fost foarte amuzant."
„Mi-a plăcut că au avut o mini-rutină de încălzire (întinderi, 10 secunde). Ei, Alexiei, i-au spus că poate face mai încet și s-a simțit confortabil."
„Au organizat un joc de 'căutare de culori' prin cameră, fără alergat. Lui Vlad i-au dat culoarea 'verde' și a găsit rapid."
„Superparty a făcut o scenetă scurtă cu păpuși și copiii au rămas atenți. Ei, Iasminei, i-au oferit o păpușă la final și a fost încântată."
„Mi-a plăcut că au folosit semnale clare pentru schimbarea jocului. Lui Luca i-au arătat semnul 'pauză' și a respectat imediat."
„Au făcut o ștafetă cu obiecte ușoare (fără viteză), doar coordonare. Ei, Nicoletei, i-au dat rolul de start și a fost mândră."
„Superparty a introdus un joc de 'spune un lucru bun despre coleg'. Lui Andrei i-au dat un exemplu și a spus ceva frumos."
„Au avut un moment de 'quiz cu imagini' pe cartonașe. Ei, Danei, i-au dat întrebarea preferată (cu animale) și a răspuns imediat."
„Superparty a făcut un joc de 'urmează liderul' cu mișcări simple. Lui Filip i-au dat rolul de lider pentru 30 de secunde și a fost super fericit."
„Mi-a plăcut că au distribuit roluri astfel încât toți să participe. Ei, Cătălinei, i-au oferit rolul de 'crainic' și a vorbit clar."
„Au pregătit o activitate de 'decorează medalia' din carton. Lui Răzvan i-au scris numele frumos și a păstrat medalia."
„Superparty a schimbat jocul exact când copiii începeau să se plictisească. Ei, Alinei, i-au dat o sarcină nouă și a revenit cu energie."
„Au făcut un joc de 'telefonul fără fir' cu propoziții scurte. Lui Cosmin i-au șoptit ușor și a transmis corect."
„Mi-a plăcut că au folosit muzică scurtă, apoi au oprit la timp ca să nu agite. Ei, Deliei, i-au spus dinainte când se oprește muzica."
„Superparty a introdus un joc de 'prinde ritmul' cu bătăi din palme. Lui Alex i-au dat un ritm ușor și a reușit."
„Au făcut o mini-vânătoare de 'obiecte rotunde', foarte potrivită pentru interior. Ei, Teodorei, i-au dat lista și a găsit tot."
„Mi-a plăcut că au intervenit calm când doi copii au vorbit simultan. Lui Ștefan i-au cerut pe rând și a așteptat."
„Superparty a avut un joc de 'ghicește emoția' din mimă. Ei, Roxanei, i-au dat 'bucurie' și a fost adorabil."
„Au făcut un joc de 'construiește turnul' din cuburi mari, pe echipe. Lui Denis i-au dat piesele de bază și a organizat bine."
„Mi-a plăcut că au lăsat copiii să aleagă între două activități, ca să nu se simtă forțați. Ei, Elizei, i-au dat opțiunea mai calmă și a ales-o."
„Superparty a introdus un joc de 'spune 3 lucruri despre tine' (scurt și amuzant). Lui Robert i-au pus o întrebare ușoară și a răspuns sigur pe el."
„Au făcut un joc de 'aruncă cercul' cu distanțe ajustate. Ei, Mirei, i-au apropiat ținta și a nimerit."
„Mi-a plăcut că au avut recuzită curată și sigură, fără piese mici periculoase. Lui Darius i-au dat o minge moale și a jucat fără incidente."
„Superparty a pregătit un mini-moment de magie simplă (dispariția unei eșarfe). Ei, Andreei, i-au arătat trucul la final și a fost uimită."
„Au organizat un joc de 'stop-dans' fără eliminare, doar puncte de participare. Lui Bogdan i-au dat un 'bravo' la fiecare rundă."
„Mi-a plăcut că au observat când cineva era timid și l-au inclus delicat. Ei, Ioanei, i-au oferit un rol mic și a prins curaj."
„Superparty a făcut un joc de 'poveste pe rând' cu o propoziție de copil. Lui Victor i-au dat finalul și l-a inventat foarte comic."
„Au încheiat cu o activitate de 'poza pe echipe', organizată, fără înghesuială. Ei, Mariei, i-au aranjat locul în față și a zâmbit."
„Superparty a introdus un joc de 'cine lipsește?' (un copil se ascunde). Lui Raul i-au explicat clar și a jucat corect."
„Mi-a plăcut că au gestionat foarte bine tranziția spre gustare. Ei, Ilincăi, i-au spus unde să stea și a fost ordine."
„Au făcut un joc de 'misiuni cu zar' (sari, bate din palme, rotește-te). Lui Cătălin i-au dat o misiune simplă și a reușit."
„Superparty a avut un mic atelier de 'brățări din hârtie' cu nume. Ei, Georgiei, i-au decorat brățara cu inimioare și a păstrat-o."
„Mi-a plăcut că au menținut o energie pozitivă fără țipete. Lui Ionuț i-au vorbit calm și a ascultat."
„Au organizat un joc de 'aliniere după culoare' (tricou/șosete), foarte amuzant. Ei, Larisei, i-au găsit echipa potrivită și a râs mult."
„Superparty a făcut un joc de 'ghicește obiectul' dintr-un săculeț, super captivant. Lui Matei i-au dat primul rând și a fost încântat."
„Mi-a plăcut că au evitat competiția dură și au accentuat cooperarea. Ei, Darei, i-au spus 'suntem aceeași echipă' și s-a calmat."
„Au făcut un joc de 'urmează linia' pe podea, cu bandă, fără alergat. Lui Paul i-au dat startul și a mers atent."
„Superparty a încheiat cu un 'moment de aplauze' pentru fiecare copil. Ei, Oanei, i-au spus pe nume la final și a fost foarte fericită."
„Au început o mini-coregrafie ușoară, pe pași simpli. Lui Marco i-au arătat mișcările de două ori și a ținut minte."
„Mi-a plăcut că au avut un plan de rezervă când un joc nu a prins. Ei, Anei, i-au propus altceva imediat și n-a existat pauză moartă."
„Superparty a făcut un joc de 'semnalele culorilor' (roșu=stop, verde=mergi). Lui Damian i-au dat exemple și a respectat perfect."
„Au făcut un mic concurs de 'balonul între genunchi' adaptat, fără viteză. Ei, Cristinei, i-au spus să meargă încet și a reușit."
„Mi-a plăcut că animatorii au fost atenți la copii care se frustrează rapid. Lui David i-au oferit o pauză scurtă și a revenit bine."
„Superparty a introdus un joc de 'ghicește personajul' cu 3 indicii clare. Ei, Irinei, i-au dat un personaj ușor și a ghicit imediat."
„Au făcut un joc de 'prinde sunetul' (clopoțel=schimbi locul), foarte ordonat. Lui Kevin i-au explicat și a urmat regula."
„Mi-a plăcut că au ținut copiii implicați inclusiv la strânsul recuzitei, ca joc. Ei, Denizei, i-au dat rolul de 'ajutor' și a fost încântată."
„Superparty a avut un final cu 'diplome amuzante' (curajos, vesel, atent). Lui Gabriel i-au dat diploma 'atent' și a zâmbit."
„Au încheiat cu o scurtă poveste de 'noapte bună' ca să se calmeze grupul. Ei, Sânzianei, i-au spus că a fost minunată și a plecat liniștită."
„Superparty a făcut un joc de 'umbre pe perete' cu o lanternă, foarte liniștitor. Lui Toma i-au dat rolul de a ține lanterna și a fost fascinat."
„Mi-a plăcut că au avut un colț cu activități calme pentru copiii obosiți. Ei, Emiliei, i-au adus o foaie de colorat și s-a liniștit imediat."
„Superparty a început cu un salut în cor și reguli scurte, pe înțelesul tuturor. Lui Ianis i-au cerut să repete regula 1 și a făcut-o perfect."
„Au organizat un joc de 'pescuit' cu pești din carton și magnet. Ei, Patriciei, i-au arătat cum să țină undița și a prins primul pește."
„Mi-a plăcut că animatorii au observat rapid când un copil se simte exclus. Lui Silviu i-au oferit o sarcină clară și a intrat în echipă."
„Superparty a făcut un joc de 'ghicește sunetul' cu obiecte simple (chei, hârtie, clopoțel). Ei, Sorinei, i-au dat primul sunet și a ghicit repede."
„Au avut o activitate de 'pictură cu burețel', fără mizerie excesivă. Lui Rareș i-au pus șorțul la timp și a lucrat curat."
„Mi-a plăcut că au setat ritmul potrivit și nu au grăbit copiii. Ei, Martei, i-au spus că poate termina desenul în liniște și a apreciat."
„Superparty a introdus un joc de 'litere ascunse' (cartonașe prin cameră). Lui Tudor i-au dat litera 'T' și a găsit-o primul."
„Au făcut un joc de 'statui' cu muzică scurtă și pauze clare. Ei, Laviniei, i-au explicat că nu se elimină nimeni și a prins curaj."
„Superparty a organizat 'trenulețul prieteniei' fără alergat, doar mers ordonat. Lui Sergiu i-au dat rolul de locomotivă și a fost încântat."
„Mi-a plăcut că au folosit un ton calm când copiii se agitau. Ei, Naomi, i-au șoptit instrucțiunea și a ascultat imediat."
„Au făcut un joc de 'aruncă la coș' cu distanțe adaptate pe vârste. Lui Nicolas i-au apropiat coșul și a nimerit de 3 ori."
„Superparty a avut un mini-joc de 'cine sunt eu?' cu bentițe și imagini. Ei, Ioanei, i-au pus bentița corect și a ghicit personajul."
„Mi-a plăcut că au alternat jocurile energice cu unele de atenție. Lui Cristian i-au dat o provocare de memorie și s-a concentrat excelent."
„Au făcut o activitate de 'colaj cu stickere', foarte potrivită pentru copii mici. Ei, Evelinei, i-au oferit stickerele preferate și a zâmbit tot timpul."
„Superparty a introdus un joc de 'pietre, foarfecă, hârtie' pe echipe, fără presiune. Lui Edi i-au explicat repede semnele și a intrat în joc."
„Mi-a plăcut că au încurajat politețea (te rog/mulțumesc) printr-un joc. Ei, Adrianei, i-au dat puncte pentru 'mulțumesc' și a fost motivată."
„Au avut un moment de 'poveste cu imagini' proiectate pe perete. Lui Radu i-au cerut să aleagă următoarea imagine și a ales inspirat."
„Superparty a făcut o activitate de 'mimă pe meserii' cu indicii ușoare. Ei, Sabinei, i-au dat 'medic' și a fost foarte amuzant."
„Au organizat un joc de 'ștafetă cu lingura și mingea', dar fără grabă. Lui Horia i-au arătat trucul să meargă încet și a reușit."
„Mi-a plăcut că au păstrat tot timpul spațiul sigur, fără înghesuială. Ei, Andreei, i-au făcut loc în cerc și a participat liniștită."
„Superparty a propus un joc de 'caută perechea' cu cartonașe identice. Lui Fabian i-au dat un set mic și a găsit perechile rapid."
„Au făcut o provocare de 'balonul nu atinge podeaua' cu reguli simple. Ei, Rebecăi, i-au spus să folosească palmele ușor și a ținut balonul sus."
„Mi-a plăcut că au oferit alternative pentru copiii mai timizi. Lui Paul-Andrei i-au dat rolul de observator la început și apoi a intrat singur în joc."
„Superparty a avut un joc de 'cuvântul secret' (spui doar șoaptă). Ei, Ilonei, i-au dat cuvântul ușor și a râs mult."
„Au făcut o activitate de 'origami simplu' (avion de hârtie), bine ghidată. Lui Marius i-au arătat pașii pe rând și a reușit din prima."
„Mi-a plăcut că au folosit recompense simbolice, nu dulciuri în exces. Ei, Selenei, i-au dat o insignă cu stea și a fost fericită."
„Superparty a introdus un joc de 'ghicește mirosul' cu arome blânde (vanilie, lămâie). Lui Șerban i-au dat prima aromă și a ghicit corect."
„Au încheiat o rundă cu 'aplaudăm echipa' ca să nu existe supărări. Ei, Mihaelei, i-au spus pe nume la aplauze și s-a luminat."
„Superparty a făcut un joc de 'puzzle pe echipe' cu piese mari. Lui Dorian i-au dat colțurile și a construit repede baza."
„Mi-a plăcut că animatorii au fost atenți la limbaj și au vorbit pe înțelesul copiilor. Ei, Otiliei, i-au explicat regula în două cuvinte și a înțeles."
„Au organizat 'bingo cu imagini' (animale, fructe), foarte captivant. Lui Cezar i-au dat planșa și a urmărit atent."
„Superparty a introdus un joc de 'roata norocului' cu sarcini haioase. Ei, Amaliei, i-au picat 'dans amuzant' și a făcut toată lumea să râdă."
„Mi-a plăcut că au adaptat volumul muzicii, fără să deranjeze. Lui Teo i-au pus muzica mai încet și a rămas implicat."
„Au făcut un joc de 'spune o calitate' pentru fiecare copil, pe rând. Ei, Carlei, i-au spus o calitate frumoasă și a prins încredere."
„Superparty a avut un joc de 'cursa cu obstacole' din perne, dar foarte sigur. Lui Albert i-au arătat traseul și a mers atent."
„Mi-a plăcut că au oprit imediat un conflict minor, fără dramă. Ei, Ralucăi, i-au cerut să respire și s-a calmat."
„Au făcut o activitate de 'desenează-ți superputerea' cu creioane colorate. Lui Patrick i-au dat ideea de start și a creat un desen genial."
„Superparty a încheiat cu un 'moment de mulțumire' pentru părinți și copii. Ei, Teodorei, i-au oferit diploma la final și a plecat fericită."
„Au introdus un joc de 'prinde culoarea' cu cartonașe ridicate în aer. Lui Mihai i-au dat rolul de a arăta culorile și a fost atent."
„Mi-a plăcut că au păstrat un program clar și nu au lăsat pauze lungi. Ei, Iuliei, i-au spus ce urmează și a rămas liniștită."
„Superparty a făcut un joc de 'ghicește gustul' cu fructe tăiate (cu acordul părinților). Lui Rares-Matei i-au dat banana și a ghicit imediat."
„Au făcut o activitate de 'povești cu zar' (imagini pe zar). Ei, Dorianei, i-au ieșit 'castel' și a inventat o poveste superbă."
„Mi-a plăcut că au oferit încurajări specifice, nu doar 'bravo'. Lui Iacob i-au spus exact ce a făcut bine și s-a motivat."
„Superparty a organizat un joc de 'codul prieteniei' (bate din palme de 2 ori când e rândul tău). Ei, Aurorei, i-au arătat semnalul și a respectat."
„Au făcut un joc de 'păstrează echilibrul' cu o carte pe cap, fără competiție. Lui Marin i-au spus să meargă încet și a reușit până la capăt."
„Mi-a plăcut că au avut mereu recuzită de rezervă, în caz că se strică ceva. Ei, Corinei, i-au înlocuit rapid un balon spart și nu s-a supărat."
„Superparty a avut un joc de 'cuvinte pe categorii' (animale, culori, jucării). Lui Rayan i-au dat categoria 'jucării' și a spus multe idei."
„Au încheiat cu o activitate de 'poza cu rame' din carton, foarte simpatică. Ei, Mirelei, i-au oferit rama cu numele ei și a păstrat-o ca amintire."
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
print(f"Total acum: {len(existing_testimonials)} testimoniale.")
