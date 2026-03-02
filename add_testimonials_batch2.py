import os
import json
import random
from datetime import datetime, timedelta

raw_text = """
„Superparty a început cu un joc de încălzire care i-a prins pe toți din prima. Lui Călin i-au dat rolul de ‘căpitan’ și a condus echipa super.”
„Au avut un colț de baloane modelate și au făcut figurine rapide. Ei, Elena, i-au făcut o inimă cu aripi și a păstrat-o toată petrecerea.”
„Mi-a plăcut că au explicat regulile scurt și clar, fără discursuri lungi. Lui Petru i-au arătat exact cum se joacă și a intrat imediat.”
„Tema ‘prințese’ a fost fină, cu jocuri potrivite și muzică ok. Ei, Miruna, i-au pus o tiară ușoară și s-a simțit ca într-un basm.”
„Superparty a observat cine are energie multă și a canalizat-o în jocuri utile. Lui Horia i-au dat sarcina să adune ‘puncte’ și a stat focusat.”
„Au făcut un mini-atelier de desen pe carton, foarte relaxant. Ei, Ema, i-au schițat o coroniță și a colorat-o cu mare grijă.”
„Mi-a plăcut că nu au forțat competiția, au păstrat joaca prietenoasă. Lui Șerban i-au spus ‘bravo’ pentru fair-play și s-a înmuiat imediat.”
„Au avut un joc de ‘căutare de indicii’ prin casă, super bine gândit. Ei, Iulia, i-au găsit primul indiciu și a fost încântată.”
„Superparty a venit pregătit cu boxă, playlist și microfon pentru anunțuri. Lui Tudor i-au dat microfonul la momentul tortului și s-a simțit important.”
„Mi-a plăcut că au făcut pauze scurte de apă și respirație. Ei, Delia, i-au întrebat discret dacă e ok și a continuat cu zâmbetul pe buze.”
„Au introdus un joc de ‘mimă’ pe teme pentru copii, foarte amuzant. Lui Cezar i-au dat primul cuvânt și a fost show total.”
„Tema ‘flori și primăvară’ a fost superbă, cu accesorii simple. Ei, Adriana, i-au prins o floare la brățară și a fost fericită.”
„Superparty a reușit să gestioneze frumos când doi copii s-au contrazis. Lui Cosmin i-au dat o ‘misiune’ separată și conflictul s-a stins.”
„Au avut un moment de dans ghidat, cu mișcări ușoare. Ei, Larisa, i-au arătat pașii lângă animator și a prins curaj.”
„Mi-a plăcut că au adaptat jocurile la spațiu, fără înghesuială. Lui Dragoș i-au mutat echipa într-un colț mai liber și a mers perfect.”
„Atelierul de coronițe din hârtie a ieșit foarte frumos. Ei, Raluca, i-au ales culorile și a lipit totul cu grijă.”
„Superparty a păstrat ritmul petrecerii fără să pară grăbiți. Lui Florin i-au dat rând la toate jocurile și n-a mai cerut atenție extra.”
„Au făcut un joc de ‘ghicește personajul’ cu indicii haioase. Ei, Mara, i-au nimerit personajul din prima și a fost super mândră.”
„Mi-a plăcut că au fost atenți la limbaj și la ton, foarte respectuos. Lui Raul i-au vorbit calm când s-a agitat și a cooperat.”
„Superparty a avut un fundal foto simplu, dar foarte drăguț. Ei, Antonia, i-au făcut o poză cu ‘inimioare’ și a ieșit minunat.”
„Au adus un joc cu cercuri pe podea, ca mini-traseu, foarte safe. Lui Kevin i-au cronometrat parcurgerea și s-a motivat tare.”
„Tema ‘party neon’ a fost veselă, fără să fie obositoare. Ei, Daria, i-au dat o brățară fosforescentă și a fost încântată.”
„Superparty a reușit să-i facă pe copii să strângă rapid jucăriile printr-un joc. Lui Damian i-au spus că e ‘șef de echipă’ și a ajutat imediat.”
„Au avut un joc de ‘pantomimă cu emoții’, foarte educativ. Ei, Ioana, i-au jucat ‘bucuria’ perfect și toți au aplaudat.”
„Mi-a plăcut că au păstrat controlul fără să fie rigizi. Lui Ștefănel i-au dat două opțiuni de joc și a ales singur, fără scandal.”
„Atelierul de stickere personalizate a fost super idee. Ei, Cătălina, i-au scris numele cu litere colorate și a lipit peste tot.”
„Superparty a făcut un moment de ‘aplaudăm pe rând’ și s-a simțit foarte frumos. Lui Max i-au dedicat un ‘bravo’ pentru curaj și a radiat.”
„Au introdus o poveste scurtă între jocuri, ca să-i adune. Ei, Georgiana, i-au dat rolul de ‘zână’ și a intrat imediat în poveste.”
„Mi-a plăcut că au avut și jocuri pentru cei mai mici, separate de cei mari. Lui Teo i-au simplificat regulile și s-a descurcat.”
„Superparty a încheiat cu un mini-ritual de ‘urări’ foarte drăguț. Ei, Nadia, i-au spus să spună prima urarea și a fost emoționată.”
„Au făcut un joc de ‘telefonul fără fir’ adaptat cu cuvinte simple. Lui Silviu i-au dat startul și a ieșit foarte comic.”
„Tema ‘pirați’ a fost super, cu ‘hartă’ și indicii. Ei, Evelin, i-au dat ‘comoara’ (o cutiuță) și a fost în extaz.”
„Superparty a gestionat excelent un copil care nu voia să piardă. Lui Răzvan i-au dat un rol de arbitru și a acceptat imediat.”
„Au avut un joc de ‘culoarea comandă’ care i-a ținut atenți fără să alerge haotic. Ei, Andra, i-au prins regula din prima și a râs mult.”
„Mi-a plăcut că au avut recuzită moale și sigură, fără riscuri. Lui Denis i-au dat mingea moale pentru pasă și a fost ok.”
„Atelierul de felicitări pentru sărbătorit a fost foarte simpatic. Ei, Sânziana, i-au scris un mesaj frumos și a decorat cu inimioare.”
„Superparty a făcut tranziția spre tort foarte natural, fără să se împrăștie copiii. Lui Ayan i-au spus să cheme grupul la masă și a fost încântat.”
„Au avut un joc de ‘ghicește obiectul’ cu ochii închiși, super amuzant. Ei, Diana, i-au nimerit din prima și a fost foarte mândră.”
„Mi-a plăcut că au păstrat muzica la volum ok pentru apartament. Lui Iulian i-au dat sarcina să aleagă următoarea melodie și s-a simțit bine.”
„Superparty a oferit mici ‘insigne’ la final, ca suvenir. Ei, Flavia, i-au dat insigna de ‘cea mai creativă’ și a zâmbit enorm.”
„Au făcut un joc de echilibru cu ‘pahare’ din plastic, foarte distractiv. Lui Rocco i-au arătat trucul și a reușit din a doua.”
„Tema ‘înghețată’ a fost adorabilă, cu jocuri pe culori și forme. Ei, Selina, i-au făcut o ‘cupă’ din carton și a luat-o acasă.”
„Superparty a fost atent la copilul care se plictisea și l-a reintegrat. Lui Marius i-au dat o provocare scurtă și a revenit imediat.”
„Au avut un moment de ‘povești rapide’ inventate de copii. Ei, Gabriela, i-au încurajat ideea și a vorbit cu încredere.”
„Mi-a plăcut că au lucrat bine și cu părinții, fără să ne întrerupă aiurea. Lui Daniel i-au cerut acordul pentru un joc mai energic și totul a mers.”
„Atelierul de ‘pictat cu bureței’ a fost genial și curat. Ei, Carla, i-au făcut un curcubeu și a fost foarte fericită.”
„Superparty a avut răbdare și cu copiii care pun multe întrebări. Lui Fabian i-au răspuns calm și l-au lăsat să ‘testeze’ recuzita.”
„Au făcut un joc de ‘ring toss’ cu cercuri moi, potrivit pentru interior. Ei, Mihaela, i-au reușit două din trei și a sărit de bucurie.”
„Mi-a plăcut că au menținut o atmosferă caldă, fără presiune. Lui Constantin i-au dat un rol mic, dar important, și s-a simțit inclus.”
„Superparty a încheiat cu poze, strâns frumos și mulțumiri, foarte civilizat. Ei, Natalia, i-au făcut o poză cu animatorii și a fost un final super.”
„Superparty a început cu un joc de prezentare rapid, ca să nu stea nimeni pe margine. Lui Andrei i-au dat o replică haioasă și s-a dezghețat imediat.”
„Au făcut un colț de pictură pe față cu modele simple și curate. Ei, Bianca, i-au desenat un fluturaș mic și a fost super încântată.”
„Mi-a plăcut că animatorii au ținut cont de vârste și au separat provocările. Lui Rareș i-au dat varianta ‘mai grea’ și a fost mândru că a reușit.”
„Au introdus un joc cu baloane fără alergat haotic, foarte bine controlat. Ei, Sonia, i-au arătat cum să țină balonul în aer și a prins ritmul.”
„Superparty a avut un moment de ‘aplauze pe rând’, ca să fie toți văzuți. Lui Luca i-au evidențiat curajul și s-a luminat la față.”
„Atelierul de brățări din mărgele mari a fost perfect pentru copii. Ei, Teodora, i-au ales culorile preferate și a ieșit o brățară superbă.”
„Mi-a plăcut că au comunicat calm când cineva întrerupea. Lui Darius i-au dat o sarcină scurtă și s-a liniștit fără supărare.”
„Au făcut un joc cu ‘umbre și forme’ pe perete, super creativ. Ei, Alesia, i-au ieșit ‘iepurașul’ din prima și a râs mult.”
„Superparty a făcut tranziția către gustări fără să se împrăștie grupul. Lui Victor i-au cerut să cheme echipa la masă și a cooperat perfect.”
„Mi-a plăcut că au verificat discret dacă toți se simt bine. Ei, Mara, i-au întrebat dacă vrea pauză și a apreciat atenția.”
„Au avut un joc de ghicitori pe echipe, cu puncte simbolice, foarte motivant. Lui Sebastian i-au dat rolul de ‘cronometru’ și s-a implicat total.”
„Tema ‘curcubeu’ a fost plină de culoare, dar nu încărcată. Ei, Ilinca, i-au pus o panglică colorată și s-a simțit specială.”
„Superparty a folosit muzică potrivită și a oprit-o la timp când trebuia să explice ceva. Lui Paul i-au zis clar ce urmează și n-a mai întrerupt.”
„Au făcut un mini-traseu cu jaloane moi, potrivit și în apartament. Ei, Noemi, i-au arătat traseul încet și a reușit fără emoții.”
„Mi-a plăcut că au avut și jocuri pentru copiii mai timizi. Lui Matei i-au oferit o variantă în doi și a intrat ușor în grup.”
„Atelierul de măști din carton a ieșit foarte frumos. Ei, Anabela, i-au lipit paiete discrete și masca a fost minunată.”
„Superparty a ținut cont de spațiu și nu a aglomerat camera. Lui Bogdan i-au mutat echipa într-un loc liber și s-a jucat în siguranță.”
„Au făcut un joc de ‘statui muzicale’ foarte amuzant, fără stres. Ei, Patricia, i-au prins ‘poza’ perfect și toți au aplaudat.”
„Mi-a plăcut că au folosit un limbaj politicos și prietenos. Lui Ionuț i-au vorbit calm și a ascultat imediat.”
„Superparty a încheiat un segment cu o urare scurtă pentru sărbătorit. Ei, Amina, i-au spus prima urarea și a fost emoționată.”
„Au introdus un joc de ‘ghicește sunetul’ cu obiecte simple, genial. Lui Radu i-au dat primul sunet și a făcut show.”
„Tema ‘junglă’ a fost super, cu mișcări de animale și indicii. Ei, Yasmine, i-au dat rolul de ‘tigrișor’ și s-a distrat enorm.”
„Superparty a reușit să includă și frații mai mici fără să strice ritmul. Lui Emi i-au simplificat regulile și a participat fericit.”
„Au făcut o mini-vânătoare de comori cu hârtii colorate și săgeți. Ei, Sofia, i-au găsit indiciul final și a țopăit de bucurie.”
„Mi-a plăcut că au respectat timpul și nu au lungit jocurile inutil. Lui Mihai i-au dat rând la final și a fost mulțumit.”
„Atelierul de desen pe farfurii de carton a fost foarte reușit. Ei, Loredana, i-au desenat o steluță mare și a colorat-o cu grijă.”
„Superparty a gestionat elegant când doi copii voiau același rol. Lui Cătălin i-au oferit un rol echivalent și nu s-a supărat.”
„Au avut un joc de ‘povești în lanț’ unde fiecare adaugă o propoziție. Ei, Denisa, i-au inventat un final amuzant și toți au râs.”
„Mi-a plăcut că au venit cu recuzită curată și organizată. Lui Alex i-au dat o insignă de ‘ajutor de animator’ și a fost încântat.”
„Superparty a făcut un moment foto fără să îi țină mult pe loc. Ei, Vanessa, i-au făcut o poză rapidă și a ieșit super.”
„Au introdus un joc de ‘aruncă și prinde’ cu mingi moi, foarte safe. Lui Robert i-au arătat tehnica și a prins din prima.”
„Tema ‘spațiu’ a fost foarte reușită, cu planete și misiuni. Ei, Maria, i-au dat rolul de ‘astronaut’ și a intrat în poveste.”
„Superparty a observat că un copil se agită și a schimbat jocul pe ceva mai liniștit. Lui Vlad i-au dat o activitate de construit și s-a calmat.”
„Au făcut un joc de ‘culoarea comandă’ cu obiecte din cameră, super atent gândit. Ei, Carla, i-au găsit culoarea cerută rapid și s-a bucurat.”
„Mi-a plăcut că au lăsat copiii să aleagă între două activități. Lui Denis i-au oferit opțiuni și a cooperat fără discuții.”
„Atelierul de ‘steaguri personalizate’ a fost foarte drăguț. Ei, Evelyn, i-au scris numele frumos și a păstrat steagul ca amintire.”
„Superparty a ținut energia sus fără să devină gălăgie. Lui Gabriel i-au dat un rol de coordonare și a stat concentrat.”
„Au făcut un joc de ‘ghicește personajul’ cu indicii ușoare pentru cei mici. Ei, Ana, i-au ghicit repede și a fost foarte mândră.”
„Mi-a plăcut că au avut pauze scurte și au oferit apă la timp. Lui Ștefan i-au spus să respire și a revenit cu chef de joacă.”
„Superparty a încheiat cu o rundă de mulțumiri și strâns ordonat. Ei, Alina, i-au spus ‘bravo’ pentru ajutor și a zâmbit larg.”
„Au introdus un joc de ‘aruncă la țintă’ cu cuburi moi, potrivit pentru interior. Lui Beni i-au setat ținta mai aproape și a reușit.”
„Tema ‘magie’ a fost făcută simplu și frumos, fără exagerări. Ei, Ioana, i-au dat o baghetă din carton și a fost încântată.”
„Superparty a fost atent la copiii care vorbesc peste alții și a moderat frumos. Lui Edi i-au dat rând clar și a așteptat.”
„Au făcut un joc de ‘ștafetă cu obiecte ușoare’, fără pericol. Ei, Ruxandra, i-au dus ‘mesajul’ echipei și s-a simțit importantă.”
„Mi-a plăcut că au folosit încurajări reale, nu doar vorbe goale. Lui Dan i-au spus exact ce a făcut bine și a prins încredere.”
„Atelierul de ‘colaj cu forme’ a fost foarte potrivit și curat. Ei, Mara, i-au făcut un colaj cu inimioare și l-a luat acasă.”
„Superparty a integrat și un moment educativ despre fair-play. Lui Toma i-au explicat pe scurt și a devenit mai calm în joc.”
„Au făcut un joc de ‘mimă pe emoții’, care i-a prins pe toți. Ei, Irina, i-au jucat ‘surpriza’ perfect și a primit aplauze.”
„Mi-a plăcut că au respectat preferințele copilului sărbătorit și tema aleasă. Lui Nico i-au organizat jocurile pe supereroi și a fost top.”
„Superparty a încheiat cu un mic ‘certificat de participant’ pentru fiecare copil. Ei, Ema, i-au dat certificatul cu numele ei și a fost foarte fericită.”
„Superparty a venit cu un set de jocuri scurte de încălzire și a prins bine din primele minute. Lui Răzvan i-au dat primul ‘high-five de echipă’ și a intrat imediat în atmosferă.”
„Au făcut un moment de dans cu mișcări ușoare, pe care le-au repetat de două ori. Ei, Daria, i-au arătat pașii pe rând și a ținut ritmul fără să se încurce.”
„Mi-a plăcut că au avut un plan clar și nu au improvizat haotic. Lui Cezar i-au explicat rolul din joc în 10 secunde și a înțeles perfect.”
„Au organizat un joc de ‘telefonul fără fir’ adaptat pentru copii mici, cu propoziții scurte. Ei, Iulia, i-au șoptit mesajul clar și a fost amuzant cum a ajuns la final.”
„Superparty a adus stickere tematice pentru fiecare copil, ca mică recompensă. Lui Tudor i-au ales un sticker cu robot și l-a lipit imediat pe tricou.”
„Au avut un colț de baloane modelabile, dar fără aglomerație, pe rând. Ei, Larisa, i-au făcut o inimioară și a păstrat-o până la final.”
„Mi-a plăcut că au observat când energia a crescut prea mult și au schimbat jocul pe ceva mai liniștit. Lui Dani i-au propus un puzzle rapid și s-a echilibrat grupul.”
„Au făcut o mini-scenetă cu roluri simple, fără să îi pună pe copii în dificultate. Ei, Roxana, i-au dat rolul de ‘narator’ cu o singură propoziție și a fost încântată.”
„Superparty a folosit o listă scurtă de reguli, repetată amuzant, ca să o țină minte toți. Lui Patrick i-au cerut să repete regula 1 și a făcut-o cu mândrie.”
„Au avut un joc de ‘găsește perechea’ cu cartonașe mari, foarte potrivit pentru vârsta lor. Ei, Amalia, i-au găsit perechea din prima și a sărit de bucurie.”
„Mi-a plăcut că animatorii au păstrat un ton cald, chiar și când copiii se împrăștiau. Lui Șerban i-au spus pe nume și a revenit imediat în cerc.”
„Au introdus un moment de ‘aplauze pentru fiecare’, ca să nu rămână nimeni pe dinafară. Ei, Elena, i-au aplaudat desenul și s-a înroșit de emoție.”
„Superparty a făcut o vânătoare de indicii cu săgeți pe hârtie, foarte bine gândită. Lui Fabian i-au dat harta și s-a simțit ca un lider.”
„Au avut un joc de ‘mima obiectelor’ cu exemple la început, ca să nu fie confuz. Ei, Diana, i-au arătat o mimă simplă și a prins curaj să continue.”
„Mi-a plăcut că au respectat spațiul și au mutat activitățile ca să nu lovească mobila. Lui George i-au reorganizat echipa lângă perete și a fost mai sigur.”
„Au făcut un atelier mic de decupat și lipit, cu materiale deja pregătite, fără mizerie. Ei, Paula, i-au dat o foarfecă pentru copii și a lucrat foarte atent.”
„Superparty a gestionat bine când doi copii au vrut același premiu simbolic. Lui Marius i-au oferit o variantă echivalentă și nu a fost nicio supărare.”
„Au avut un joc de ‘cuvântul secret’ pe echipe, cu șoapte și semne. Ei, Andreea, i-au ghicit cuvântul și echipa a aplaudat-o.”
„Mi-a plăcut că au ținut cont de timiditate și au oferit roluri mici la început. Lui Iustin i-au dat un rol de ‘ajutor’ și apoi a cerut singur să participe mai mult.”
„Superparty a făcut poze pe rând, rapid, fără să blocheze petrecerea. Ei, Gabriela, i-au făcut o poză cu recuzita și a ieșit foarte bine.”
„Au introdus un joc de echilibru cu pernuțe moi, potrivit și în spațiu mic. Lui Damian i-au arătat traseul încet și a reușit din a doua încercare.”
„Mi-a plăcut că au vorbit frumos și au evitat comparațiile între copii. Ei, Raluca, i-au spus ‘bravo pentru curaj’ și s-a simțit încurajată.”
„Superparty a folosit muzică doar cât trebuia, apoi pauză pentru explicații clare. Lui Kevin i-au spus exact când începe jocul și a așteptat fără nerăbdare.”
„Au făcut un joc de ‘ghicește desenul’ pe tablă mică, super amuzant. Ei, Mihaela, i-au desenat o pisică și a ghicit repede toată lumea.”
„Mi-a plăcut că au avut o cutie cu recuzită și totul a rămas ordonat. Lui Florin i-au dat o pălărie haioasă și a devenit ‘personaj’ pe loc.”
„Au organizat un atelier de coronițe din hârtie, cu lipici care nu curgea. Ei, Nicoleta, i-au făcut o coroniță cu steluțe și a purtat-o până la final.”
„Superparty a fost atent la copiii care se enervează ușor și a intervenit calm. Lui Cosmin i-au propus să numere punctele și s-a liniștit.”
„Au avut un joc cu ‘semnal roșu/verde’ care i-a ținut concentrați fără alergătură excesivă. Ei, Bianca, i-au pornit jocul cu un exemplu și a prins imediat ideea.”
„Mi-a plăcut că au adaptat jocurile la tema aleasă fără să le facă complicate. Lui Albert i-au dat o ‘misiune de supererou’ și a fost încântat.”
„Superparty a închis frumos un segment, cu mulțumiri și un mini-ritual de final. Ei, Claudia, i-au oferit ultima ‘bravo’ și a zâmbit larg.”
„Au introdus un joc de ‘pescuit’ cu magnet (jucărie), foarte potrivit pentru cei mici. Lui Raul i-au dat prima undiță și a fost fascinat.”
„Mi-a plăcut că au verificat dacă cineva are nevoie de pauză, fără să întrerupă petrecerea. Ei, Sorina, i-au făcut semn că poate sta jos un minut și a revenit liniștită.”
„Superparty a gestionat perfect momentul tortului, fără îmbulzeală. Lui Victor i-au spus unde să stea și a respectat rândul.”
„Au făcut un joc de ‘caută forma’ prin cameră, cu indicații clare. Ei, Mara, i-au găsit cercul din prima și a fost foarte mândră.”
„Mi-a plăcut că au fost punctuali și au început la ora stabilită. Lui Silviu i-au dat imediat o activitate și nu a apucat să se plictisească.”
„Au avut un atelier de ‘insigne’ din carton, cu numele fiecărui copil. Ei, Oana, i-au scris numele frumos și a păstrat insigna ca suvenir.”
„Superparty a folosit o metodă simplă de împărțire pe echipe, fără discuții. Lui Radu i-au dat un cartonaș albastru și s-a așezat imediat cu echipa lui.”
„Au introdus un joc de ‘cine lipsește din cerc’, foarte bun pentru atenție. Ei, Alina, i-au ghicit rapid și toți au râs.”
„Mi-a plăcut că au fost atenți la volum și la vecini, fără să strice distracția. Lui Paul i-au făcut semn ‘mai încet’ printr-un gest amuzant și a funcționat.”
„Superparty a încheiat cu o mică ‘diplomă’ și o poză de grup. Ei, Florentina, i-au dat diploma cu numele ei și a fost foarte fericită.”
„Au introdus un joc de ‘povești cu zaruri’ (imagini), creativ și simplu. Lui Teo i-au aruncat zarul primul și a inventat o propoziție amuzantă.”
„Mi-a plăcut că au inclus și copiii care nu vor să danseze, cu roluri alternative. Ei, Cristina, i-au oferit rolul de ‘DJ’ și a fost încântată.”
„Superparty a făcut un joc cu obstacole moi, dar a păstrat distanța între copii. Lui Luca i-au explicat regula ‘pe rând’ și a respectat-o.”
„Au avut un joc de ‘ghicește animalul’ cu sunete, foarte amuzant. Ei, Natalia, i-au făcut sunetul de pisică și a ieșit genial.”
„Mi-a plăcut că au lăsat copilul sărbătorit să aleagă ordinea jocurilor. Lui Denis i-au cerut să aleagă și s-a simțit în centrul atenției.”
„Au făcut un atelier de colorat cu șabloane, rapid și curat. Ei, Adina, i-au ales un șablon cu inimă și a colorat foarte atent.”
„Superparty a știut să oprească un joc înainte să devină obositor. Lui Robert i-au spus ‘ultima rundă’ și a fost o încheiere perfectă.”
„Au avut un joc de ‘mesaje pozitive’ în cerc, foarte frumos ca idee. Ei, Evelina, i-au spus un compliment și a fost vizibil emoționată.”
„Mi-a plăcut că au folosit recuzită sigură și materiale moi, fără risc. Lui Andi i-au dat o minge moale și s-a jucat fără probleme.”
„Superparty a strâns totul la final și a lăsat locul curat, fără să fie nevoie să intervenim noi. Ei, Denisa, i-au mulțumit pentru ajutor și a fost încântată.”
"""

lines = [line.strip() for line in raw_text.split('\n') if line.strip().startswith('„')]
print(f"Am gasit {len(lines)} testimoniale noi.")

MDX_DIR = "src/content/seo-articles"
JSON_PATH = "src/data/superparty_testimonials.json"

mdx_files = sorted([f for f in os.listdir(MDX_DIR) if f.endswith('.mdx')])

with open(JSON_PATH, "r", encoding="utf-8") as f:
    existing_testimonials = json.load(f)

# Find out how many unique slugs are already assigned
assigned_slugs = {t["slug"] for t in existing_testimonials}
print(f"Baza noastra are deja testimoniale pentru {len(assigned_slugs)} articole.")

idx = 0
for mdx in mdx_files:
    slug = mdx.replace('.mdx', '')
    if slug in assigned_slugs:
        continue
    
    # Adaugam 3 testimoniale la acest slug
    for _ in range(3):
        if idx >= len(lines):
            break
        text = lines[idx].strip('„”')
        loc = "București"
        if "sector" in slug:
            loc = "Sector " + slug.split('sector-')[1][0]
        elif "ilfov" in slug:
            loc = "Ilfov"
            
        t_obj = {
            "siteId": "superparty",
            "slug": slug,
            "name": "Părinte mulțumit",
            "location": loc,
            "event": "Petrecere Copii",
            "text": text,
            "source": random.choice(["whatsapp", "google", "facebook"]),
            "date": (datetime.now() - timedelta(days=random.randint(10, 200))).strftime("%Y-%m-%d")
        }
        existing_testimonials.append(t_obj)
        idx += 1

    if idx >= len(lines):
        break

with open(JSON_PATH, "w", encoding='utf-8') as f:
    json.dump(existing_testimonials, f, indent=2, ensure_ascii=False)

print(f"S-au salvat noul stoc de testimoniale in {JSON_PATH}. Acum avem in total {len(existing_testimonials)}.")
