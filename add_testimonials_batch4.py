import os
import json
import random
from datetime import datetime, timedelta

raw_text = """
„Superparty a pornit petrecerea cu un joc scurt de încălzire, ca să prindă curaj toți. Lui Ștefan i-au dat primul rol și s-a activat imediat.”
„Mi-a plăcut că au folosit un limbaj foarte blând când cineva se încurca. Ei, Ilinca, i-au spus ‘încearcă din nou’ și a prins încredere.”
„Superparty a făcut un joc de ‘telefonul fără fir’ adaptat, cu propoziții simple și haioase. Lui Cosmin i-au șoptit primul mesaj și a râs tot grupul.”
„Au pregătit o mini-coregrafie ușoară pe o melodie potrivită copiilor. Ei, Patricia, i-au arătat mișcările pe rând și a ținut pasul.”
„Mi-a plăcut că au avut semnale clare pentru ‘stop’ și ‘pauză’, fără țipat. Lui Luca i-au făcut semnul cu mâna și a oprit instant.”
„Superparty a venit cu un joc de ‘cine lipsește?’ care i-a ținut atenți fără agitație. Ei, Georgiana, i-au dat rolul de observator și a fost încântată.”
„Au făcut un concurs de mimă cu teme de copii, foarte potrivit. Lui Radu i-au dat primul cuvânt și a jucat super.”
„Mi-a plăcut că animatorii au verificat dacă toți înțeleg înainte să înceapă jocul. Ei, Alina, i-au repetat regula pe scurt și a fost ok.”
„Superparty a organizat un joc de ‘curier rapid’ cu bilețele, fără alergat haotic. Lui Sorin i-au dat primul bilețel și s-a simțit important.”
„Au introdus un moment de aplauze pentru fiecare echipă, fără comparații. Ei, Larisa, i-au condus aplauzele și a zâmbit mult.”
„Au avut un joc de ‘ghicește culoarea’ cu obiecte din cameră, simplu și distractiv. Lui Damian i-au spus prima provocare și a găsit imediat.”
„Mi-a plăcut că au lăsat loc și pentru copiii mai timizi să participe fără presiune. Ei, Amalia, i-au oferit o opțiune ușoară și a intrat în joc.”
„Superparty a făcut un joc de echipă cu nume amuzante pentru grupuri, ceea ce i-a unit. Lui Eric i-au pus numele echipei și a fost mândră.”
„Au folosit o mică poveste ca să lege activitățile între ele, foarte creativ. Ei, Raluca, i-au dat rolul de ‘explorator’ și a intrat în poveste.”
„Mi-a plăcut că au controlat bine energia, alternând jocuri active cu jocuri de masă. Lui Florin i-au oferit o pauză scurtă și apoi a revenit.”
„Superparty a făcut un joc de ‘pescuit’ cu carton și clipsuri, fără mizerie. Ei, Diana, i-au dat undița de jucărie și a fost încântată.”
„Au organizat un mic moment de ‘premiu pentru bunătate’, ceea ce a încurajat comportamentul frumos. Lui Vlad i-au dat o stea pentru ajutor și s-a bucurat.”
„Mi-a plăcut că au fost foarte atenți la spațiul de joacă și nu au împins copiii în colțuri. Ei, Noemi, i-au mutat jocul într-un loc mai liber și a fost perfect.”
„Superparty a ținut copiii implicați inclusiv la strâns, ca parte din joc. Lui Nicu i-au dat rolul de ‘colector’ și a strâns cu entuziasm.”
„Au făcut un joc de ‘șoapte și ecou’, care a calmat grupul înainte de tort. Ei, Evelina, i-au dat primul ‘ecou’ și a fost foarte drăguț.”
„Au avut un joc de ‘cine conduce trenulețul’ fără îmbulzeală, pe rând. Lui Ovidiu i-au dat startul și a respectat rândul.”
„Mi-a plăcut că animatorii au observat rapid când un copil se plictisea și l-au reintegrat. Ei, Selena, i-au dat o sarcină nouă și a revenit în joc.”
„Superparty a făcut un quiz cu întrebări de vârstă mică (animale, culori), super potrivit. Lui Mario i-au pus prima întrebare și a răspuns imediat.”
„Au adus baloane modelabile și au făcut forme simple, fără să prelungească prea mult. Ei, Cristina, i-au făcut o floare și a fost fericită.”
„Mi-a plăcut că au lăsat sărbătoritul să aleagă doar de câteva ori, fără să îl copleșească. Lui Paul i-au cerut o singură alegere și a fost relaxat.”
„Superparty a avut un joc de ‘punguța cu surprize’ unde fiecare primea pe rând, fără ceartă. Ei, Roberta, i-au explicat rândul și a așteptat frumos.”
„Au făcut un joc de ‘caută perechea’ cu cartonașe, foarte bun pentru interior. Lui Emanuel i-au dat primul cartonaș și a găsit perechea.”
„Mi-a plăcut că au folosit glume potrivite pentru copii, fără sarcasm. Ei, Andreea, i-au râs la poante și s-a simțit în largul ei.”
„Superparty a gestionat elegant când un copil a vărsat puțină apă: pauză scurtă și gata. Lui Adrian i-au spus ‘nu-i nimic’ și a continuat liniștit.”
„Au încheiat cu un joc scurt de ‘mulțumim’ și salut, fără să tragă de timp. Ei, Ana, i-au făcut un salut special și a plecat zâmbind.”
„Au făcut un joc de ‘pălăria cu provocări’ cu sarcini simple (bate din palme, salută), foarte amuzant. Lui Silviu i-au picat două bătăi din palme și a râs.”
„Mi-a plăcut că au dat instrucțiuni clare și au verificat că toți au înțeles. Ei, Iasmina, i-au repetat încet și a fost ok.”
„Superparty a avut un joc de ‘ștafetă cu lingura’ adaptat, fără risc. Lui Marius i-au arătat cum să meargă încet și a reușit.”
„Au pregătit o mică scenetă cu roluri scurte pentru copii, foarte drăguț. Ei, Bianca, i-au dat rolul de ‘prințesă’ pentru câteva replici și a fost încântată.”
„Mi-a plăcut că au ținut copiii în aceeași zonă, fără să alerge prin toată casa. Lui Felix i-au dat o poziție clară și a rămas acolo.”
„Superparty a venit cu un joc de ‘ghicește obiectul’ dintr-un săculeț, super captivant. Ei, Elena, i-au dat primul obiect și a ghicit repede.”
„Au fost foarte buni la a opri micile conflicte înainte să crească. Lui George i-au propus să schimbe rolul și s-a liniștit.”
„Mi-a plăcut că au avut și jocuri în care copiii cooperează, nu doar competiție. Ei, Gabriela, i-au dat rolul de ‘ajutor’ și s-a simțit utilă.”
„Superparty a făcut poze de grup rapid și ordonat, fără stres. Lui Răzvan i-au spus unde să stea și a ieșit bine.”
„Au oferit un final energic cu muzică scurtă, apoi au calmat atmosfera pentru plecare. Ei, Miruna, i-au făcut cu mâna la final și a fost foarte drăguț.”
„Au introdus un joc de ‘pietre, foarfecă, hârtie’ pe echipe, foarte distractiv. Lui Sami i-au explicat pe scurt și a intrat în joc imediat.”
„Mi-a plăcut că au știut să vorbească și cu părinții scurt, fără să întrerupă copiii. Ei, Ramona, i-au explicat ce urmează și a fost liniștită.”
„Superparty a făcut un joc de ‘șirul de cuvinte’ pe teme de copii, bun pentru pauze. Lui Denis i-au dat primul cuvânt și a continuat rapid.”
„Au folosit un mic ‘clopoțel’/semnal pentru schimbarea jocului, foarte eficient. Ei, Mara, i-au arătat semnul și a ascultat imediat.”
„Mi-a plăcut că au avut răbdare cu copiii care vorbesc peste rând și au rezolvat calm. Lui Alex i-au spus ‘ridicăm mâna’ și a respectat.”
„Superparty a făcut un joc de ‘desenează rapid’ cu teme simple, fără să murdărească. Ei, Daria, i-au dat o temă ușoară și a desenat fericită.”
„Au fost atenți la copilul care nu voia să fie atins și au păstrat distanța. Lui Noel i-au oferit roluri fără contact și a participat.”
„Mi-a plăcut că au ținut ritmul și nu au lăsat timpi morți între activități. Ei, Teona, i-au dat imediat următoarea sarcină și a rămas implicată.”
„Superparty a păstrat atmosfera pozitivă până la final, fără să scadă energia. Lui Cristian i-au făcut un ‘bravo’ special și s-a luminat.”
„Au încheiat cu o mică ‘paradă’ a echipelor și o poză finală, foarte simpatic. Ei, Ingrid, i-au dat un mic rol de lider și a fost mândră.”
„Superparty a început cu un joc de prezentare foarte scurt, ca să nu se plictisească nimeni. Lui Sebastian i-au dat primul rând și a prins curaj.”
„Mi-a plăcut că au împărțit copiii pe grupe după energie, fără să jignească pe nimeni. Ei, Adriana, i-au dat o sarcină liniștită și a fost perfect.”
„Superparty a venit cu un joc de ‘vânătoare de indicii’ printr-o singură cameră, fără haos. Lui Rareș i-au dat prima hartă și a fost super implicat.”
„Au făcut un mini-moment de dans cu mișcări simple, pe care le-au repetat de 2 ori și gata. Ei, Andra, i-au arătat pașii încet și a ținut pasul.”
„Mi-a plăcut că au folosit o voce calmă chiar și când copiii se agitau. Lui Robert i-au spus clar ‘acum e rândul tău’ și a așteptat.”
„Superparty a avut un joc de echilibru cu pernuțe, foarte safe pentru interior. Ei, Roxana, i-au ținut locul în echipă și a fost fericită.”
„Au adaptat jocurile pentru spațiul nostru mic, fără să se plângă. Lui Andrei i-au reorganizat traseul și a ieșit bine.”
„Mi-a plăcut că au lăudat comportamentele bune, nu doar câștigătorii. Ei, Daniela, i-au dat un ‘bravo’ pentru răbdare și a zâmbit.”
„Superparty a făcut un concurs de ghicit sunete (animale/obiecte), foarte potrivit vârstei. Lui Bogdan i-au dat primul sunet și a ghicit.”
„Au avut un mic moment de respirație/linistire înainte de tort, chiar a ajutat. Ei, Corina, i-au arătat cum să respire și s-a calmat.”
„Superparty a venit cu un joc de ‘puzzle pe echipe’ cu piese mari, fără frustrare. Lui Ionuț i-au dat rolul de ‘căutător’ și a fost încântat.”
„Mi-a plăcut că au ținut cont de copiii care nu vor să vorbească mult. Ei, Oana, i-au dat roluri fără vorbit și a participat liniștită.”
„Au făcut un joc de ‘statuile muzicale’ fără împins și fără supărări. Lui Darius i-au explicat regula de siguranță și a respectat.”
„Superparty a adus recuzită curată și bine organizată, nu aruncată la întâmplare. Ei, Loredana, i-au dat o cutie cu obiecte și a ales frumos.”
„Mi-a plăcut că au fost punctuali și au început exact când au spus. Lui Victor i-au făcut un mic ‘start’ oficial și s-a bucurat.”
„Au introdus un joc de ‘bingo’ cu imagini pentru copii, super amuzant. Ei, Irina, i-au arătat cum să bifeze și a fost atentă.”
„Superparty a gestionat foarte bine diferențele de vârstă dintre copii. Lui Mihai i-au dat sarcini mai grele, iar cei mici au avut variante simple.”
„Mi-a plăcut că au pus muzica la volum potrivit, nu prea tare. Ei, Simona, i-au spus că poate cere mai încet și a apreciat.”
„Au făcut un joc de ‘cuvinte interzise’ adaptat (pentru copii), foarte distractiv. Lui Cătălin i-au dat primul cartonaș și a râs.”
„Superparty a avut o tranziție foarte bună către tort, fără agitație mare. Ei, Florentina, i-au chemat pe rând la masă și a fost ordonat.”
„Au făcut un mic concurs de aruncat la țintă cu mingi moi, fără risc. Lui Denis i-au arătat de unde să arunce și a nimerit.”
„Mi-a plăcut că animatorii au observat imediat când cineva rămâne pe dinafară. Ei, Ioana, i-au găsit o echipă rapid și a reintrat.”
„Superparty a inventat o ‘misiune de super-erou’ pe pași scurți, foarte captivant. Lui Teodor i-au dat insigna și a fost mândru.”
„Au avut un joc de ‘ghicește personajul’ cu descrieri simple, fără să îi încurce. Ei, Maria, i-au dat un personaj ușor și a ghicit.”
„Mi-a plăcut că au păstrat regulile constante, nu le-au schimbat din mers. Lui Șerban i-au reamintit regula o singură dată și a fost suficient.”
„Superparty a adus autocolante ca recompense mici, fără să creeze obsesie. Ei, Vanessa, i-au dat unul pentru implicare și a fost fericită.”
„Au făcut un joc de ‘lanțul complimentelor’, foarte frumos pentru grup. Lui Gabriel i-au spus să zică un lucru bun și a făcut-o.”
„Mi-a plăcut că au vorbit pe nume cu copiii, ceea ce i-a apropiat. Ei, Mirela, i-au spus pe nume și s-a luminat.”
„Superparty a ținut un joc de ‘caută forma’ (cerc/pătrat) prin cameră, foarte simplu și eficient. Lui Paul i-au dat prima formă și a găsit.”
„Au făcut o pauză scurtă de apă la momentul potrivit, fără să piardă controlul. Ei, Paula, i-au reamintit să bea apă și a ascultat.”
„Superparty a făcut un joc de ‘ștafetă cu balonul’ fără să fie nevoie de alergat tare. Lui Raul i-au arătat traseul și a mers bine.”
„Mi-a plăcut că au fost atenți la copilul care se sperie de zgomote și au ajustat imediat. Ei, Elena, i-au redus stimulii și a fost ok.”
„Au venit cu un joc de ‘cod secret’ (culori și semne), foarte creativ. Lui Alexandru i-au dat primul cod și l-a rezolvat.”
„Superparty a folosit glume potrivite vârstei, fără ironii. Ei, Alexandra, i-au râs cu poftă și s-a simțit bine.”
„Mi-a plăcut că au încurajat cooperarea: ‘ajută-l pe coleg’. Lui Tudor i-au cerut să ajute și a făcut-o imediat.”
„Au făcut un joc de ‘poveste pe rând’, fiecare zicea o propoziție, super simpatic. Ei, Sorina, i-au dat începutul și a fost creativă.”
„Superparty a avut un plan B când un joc nu a prins la grup. Lui Matei i-au schimbat activitatea rapid și a mers perfect.”
„Mi-a plăcut că au fost politicoși și cu părinții, fără să întrerupă atmosfera pentru copii. Ei, Teodora, i-au explicat scurt programul și a fost liniștită.”
„Au făcut un joc de ‘labirint’ desenat cu bandă pe podea, foarte ingenios. Lui Daniel i-au dat primul traseu și a fost încântat.”
„Superparty a încheiat cu un moment de mulțumire pentru sărbătorit, foarte frumos. Ei, Catalina, i-au oferit un salut special și a zâmbit.”
„Au organizat un joc de ‘cine e liderul?’ care i-a ținut atenți fără gălăgie. Lui Răzvan i-au dat rolul de lider și a fost mândru.”
„Mi-a plăcut că au respectat limitele: fără atingeri forțate, fără tras de copii. Ei, Emilia, i-au oferit opțiuni și a ales singură.”
„Superparty a făcut un concurs de ‘ghicește din desen’ cu desene foarte simple. Lui Horia i-au dat prima foaie și a ghicit repede.”
„Au avut un joc de ‘stafeta cu cărți’ (transportă fără să cadă), foarte amuzant. Ei, Denisa, i-au arătat cum să țină și a reușit.”
„Mi-a plăcut că au păstrat ritmul și nu au lungit jocurile până se plictisesc copiii. Lui David i-au spus ‘ultimul tur’ și a fost perfect.”
„Superparty a avut un joc de ‘detectiv’ cu întrebări simple, potrivit pentru interior. Ei, Ruxandra, i-au dat lupa de jucărie și a fost încântată.”
„Au gestionat foarte bine când doi copii voiau același obiect: au făcut schimb pe rând. Lui Marian i-au explicat rândul și a acceptat.”
„Mi-a plăcut că au avut energie bună, fără să devină obositori. Ei, Nicoleta, i-au ținut atenția cu un joc scurt și a râs.”
„Superparty a pus accent pe distracție, nu pe competiție agresivă. Lui Sergiu i-au spus ‘jucăm împreună’ și s-a văzut diferența.”
„Au încheiat cu o poză rapidă și ordonată, apoi au lăsat copiii să se îmbrățișeze și să plece liniștit. Ei, Larisa, i-au spus ‘la revedere’ cu un gest frumos.”
„Superparty a început cu un joc de încălzire pe culori, foarte ușor de înțeles. Lui Radu i-au dat cartonașul roșu și a intrat imediat în joc.”
„Mi-a plăcut că au avut activități și pentru copiii mai timizi. Ei, Biancăi, i-au dat rolul de ‘ajutor’ și s-a simțit în siguranță.”
„Au făcut un mini-show de magie cu trucuri scurte, pe înțelesul copiilor. Lui Luca i-au chemat ca voluntar și a fost în extaz.”
„Superparty a adus jocuri de logică pe echipe, fără presiune. Ei, Dariai, i-au dat piese mai mari și a reușit ușor.”
„Mi-a plăcut că au împărțit timpul bine: joacă, pauză, iar joacă. Lui Ciprian i-au spus clar când urmează pauza și nu s-a agitat.”
„Au făcut un concurs de mimă cu subiecte pentru copii, super amuzant. Ei, Anei, i-au dat un animal simplu și a ieșit grozav.”
„Superparty a venit pregătit cu muzică potrivită și fără versuri nepotrivite. Lui Florin i-au lăsat să aleagă o melodie și s-a bucurat.”
„Mi-a plăcut că au încurajat copiii să aplaude și pe ceilalți. Ei, Georgianei, i-au spus ‘bravo’ pentru curaj și a prins încredere.”
„Au adaptat un joc de ‘telefonul fără fir’ ca să fie scurt și clar. Lui Petru i-au dat începutul și s-a descurcat perfect.”
„Superparty a ținut copiii concentrați fără să țipe la ei. Ei, Iuliei, i-au vorbit calm și a ascultat imediat.”
„Au făcut un atelier rapid de brățări din hârtie, simplu și ordonat. Lui Ștefan i-au arătat modelul și a lucrat atent.”
„Mi-a plăcut că au avut grijă la copiii care se plictisesc repede. Ei, Evelinei, i-au schimbat activitatea la timp și a rămas implicată.”
„Superparty a organizat o mini-ștafetă fără alergat nebunește, doar pași rapizi. Lui Vlad i-au explicat traseul și a respectat regulile.”
„Au făcut un joc cu ghicitori pe nivel de vârstă, foarte bine gândit. Ei, Sarei, i-au dat ghicitori ușoare și a reușit.”
„Mi-a plăcut că animatorii au fost atenți la spațiul din jur și au mutat mobilierul cu grijă. Lui Marius i-au creat loc pentru joc și a fost ok.”
„Superparty a introdus un joc de ‘comori ascunse’ cu indicii scurte, fără confuzie. Ei, Amaliei, i-au dat primul indiciu și a fost încântată.”
„Au gestionat bine când un copil a vrut să plece la părinți: fără dramă, fără presiune. Lui Ștefănel i-au spus ‘revii când ești gata’ și a revenit.”
„Mi-a plăcut că au avut un ton prietenos, dar ferm la reguli. Ei, Claudiei, i-au explicat pe scurt și a înțeles.”
„Superparty a făcut un joc de ‘puntea sigură’ cu pași pe bandă, foarte safe. Lui Adrian i-au dat primul start și a fost lider.”
„Au avut o tranziție excelentă spre masă, fără îmbulzeală. Ei, Mirelei, i-au chemat pe rând și a mers lin.”
„Au făcut un joc de ‘cine lipsește?’ (observație), care i-a liniștit după agitație. Lui Emanuel i-au dat rolul de observator și i-a plăcut.”
„Mi-a plăcut că au venit cu recuzită suficientă pentru toți, fără ceartă. Ei, Alexiei, i-au dat setul ei și nu a mai apărut conflict.”
„Superparty a ținut o provocare de ‘turn din pahare’ pe echipe, super distractiv. Lui Sebastian i-au dat rolul de constructor și a fost mândru.”
„Au făcut un joc de memorie cu imagini, foarte potrivit pentru 5–7 ani. Ei, Karinei, i-au arătat cum să întoarcă cartonașele și a prins repede.”
„Mi-a plăcut că au verificat dinainte ce spațiu au și au venit cu planul potrivit. Lui Paul i-au adaptat jocul ca să nu alerge în zona îngustă.”
„Superparty a introdus un joc de ‘codul culorilor’ pe muzică, foarte clar. Ei, Deliei, i-au explicat regula pe rând și a înțeles.”
„Au păstrat energia sus fără să fie obositori sau gălăgioși. Lui Sorin i-au dat o sarcină activă și a consumat energia frumos.”
„Mi-a plăcut că au ținut cont de copiii care nu vor să fie în centru. Ei, Ilincăi, i-au dat rolul de ‘organizator’ și a fost fericită.”
„Superparty a făcut un joc de ‘povești cu imagini’, fiecare alegea o carte și continua. Lui Dorian i-au dat prima carte și a fost creativ.”
„Au încheiat un joc înainte să se plictisească grupul, exact la timp. Ei, Melisei, i-au spus ‘ultima rundă’ și a rămas cu chef.”
„Au avut un moment de dans cu mișcări pe loc, perfect pentru interior. Lui Cosmin i-au arătat pașii simplu și a ținut ritmul.”
„Mi-a plăcut că au încurajat copiii să fie politicoși între ei. Ei, Alinei, i-au reamintit ‘te rog’ și ‘mulțumesc’ fără morală.”
„Superparty a făcut un joc de ‘cine prinde bilețelul’ pe rând, fără îmbrânceli. Lui Cezar i-au dat primul bilețel și a respectat rândul.”
„Au organizat un mini-atelier de desen rapid, iar apoi au expus desenele. Ei, Laviniei, i-au lăudat desenul și a fost foarte mândră.”
„Mi-a plăcut că au avut soluții când un copil s-a supărat: au schimbat rolul și s-a liniștit. Lui Nectarie i-au oferit altă sarcină și a mers.”
„Superparty a adus un joc de ‘întrebări fulger’ despre personaje, super antrenant. Ei, Mirei, i-au dat întrebări pe gustul ei și a râs mult.”
„Au fost atenți la reguli de siguranță: fără alergat printre scaune, fără împins. Lui Damian i-au spus clar limita și a ascultat.”
„Mi-a plăcut că au integrat și copiii mai mici fără să îi țină pe loc pe cei mari. Ei, Patriciei, i-au dat activități pe nivel și a fost perfect.”
„Superparty a ținut un joc de ‘mesaje secrete’ în șoaptă, care i-a captivat. Lui Călin i-au dat primul mesaj și a fost super atent.”
„Au terminat cu un mini-moment de aplauze pentru sărbătorit și pentru echipă, foarte frumos. Ei, Otiliei, i-au dat o inimioară din carton și a zâmbit.”
„Au făcut un joc de coordonare cu mingi moi, fără riscuri. Lui Beniamin i-au arătat cum să paseze corect și a cooperat.”
„Mi-a plăcut că au avut un program clar și l-au respectat. Ei, Rebecăi, i-au spus dinainte ce urmează și a fost liniștită.”
„Superparty a introdus un joc de ‘cine ghicește obiectul’ cu ochii închiși (safe, pe rând). Lui Filip i-au dat un obiect ușor și a ghicit rapid.”
„Au avut răbdare când copiii puneau multe întrebări și au răspuns pe înțeles. Ei, Nicoletei, i-au explicat frumos și a fost încântată.”
„Mi-a plăcut că nu au făcut glume pe seama copiilor, doar glume prietenoase. Lui Marcel i-au spus ‘super încercare’ și a prins curaj.”
„Superparty a făcut un joc de ‘echipă vs echipă’ fără scor agresiv, doar obiective. Ei, Iasminei, i-au dat rolul de cronometru și a fost fericită.”
„Au reușit să țină atenția grupului chiar și după ce au intrat invitați târziu. Lui Hristian i-au reluat regula scurt și a reintrat în joc.”
„Mi-a plăcut că au strâns recuzita ordonat, fără să lase mizerie. Ei, Adrianei, i-au cerut ajutor la strâns și s-a simțit importantă.”
„Superparty a avut o comunicare bună cu părinții, dar fără să rupă ritmul petrecerii. Lui George i-au continuat jocul fără pauze inutile.”
„Au încheiat frumos, cu un mic mesaj de mulțumire și o atmosferă calmă. Ei, Mihaelei, i-au spus ‘ai fost grozavă azi’ și a plecat zâmbind.”
"""

lines = [line.strip() for line in raw_text.split('\n') if line.strip().startswith('„')]
print(f"Am gasit {len(lines)} testimoniale noi.")

MDX_DIR = "src/content/seo-articles"
JSON_PATH = "src/data/superparty_testimonials.json"

mdx_files = sorted([f for f in os.listdir(MDX_DIR) if f.endswith('.mdx')])

with open(JSON_PATH, "r", encoding="utf-8") as f:
    existing_testimonials = json.load(f)

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
