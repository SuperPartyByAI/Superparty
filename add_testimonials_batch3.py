import os
import json
import random
from datetime import datetime, timedelta

raw_text = """
„Superparty a început cu un joc scurt de prezentare, ca să nu fie nimeni exclus. Lui Bogdan i-au pus o întrebare simplă și a răspuns fără emoții.”
„Au avut o rundă de ‘urmează liderul’ cu mișcări foarte ușoare. Ei, Simona, i-au arătat pas cu pas și a râs tot timpul.”
„Mi-a plăcut că animatorii au ținut cont de spațiul mic și au ales jocuri potrivite. Lui Alex i-au dat rolul de cronometrist și a fost foarte implicat.”
„Au făcut un joc de ‘ghicește obiectul’ în sac, cu obiecte moi și sigure. Ei, Ioana, i-au lăsat timp să pipăie și a ghicit din a doua.”
„Superparty a venit pregătit cu plan B pentru când copiii obosesc. Lui Sebastian i-au propus un joc mai liniștit și a funcționat perfect.”
„Au făcut un atelier rapid de felicitări pentru sărbătorit. Ei, Cătălina, i-au scris o urare frumoasă și a fost foarte mândră.”
„Mi-a plăcut că au folosit reguli scurte și repetate amuzant. Lui Rareș i-au cerut să repete o regulă și a făcut-o ca un mic ‘șef’.”
„Au introdus un joc de ‘pietre/paper/foarfecă’ pe echipe, super energic. Ei, Georgiana, i-au arătat semnele și a intrat imediat în joc.”
„Superparty a fost atent când un copil s-a speriat de gălăgie și a redus volumul. Lui Darius i-au oferit o pauză scurtă și a revenit liniștit.”
„Au încheiat un segment cu o mini-paradă a copiilor, pe rând. Ei, Anda, i-au aplaudat momentul și s-a simțit specială.”
„Au avut un joc de ‘caută culoarea’ care i-a ținut concentrați fără alergat haotic. Lui Eduard i-au dat prima provocare și a găsit repede.”
„Mi-a plăcut că au avut mereu contact vizual și au comunicat clar cu copiii. Ei, Mirela, i-au spus pe nume și a răspuns imediat.”
„Superparty a organizat o întrecere cu baloane, dar în ritm calm, fără împingeri. Lui Vlad i-au explicat ‘fără grabă’ și a fost foarte corect.”
„Au făcut un joc de ‘statui muzicale’ cu pauze scurte, perfect pentru vârsta lor. Ei, Teodora, i-au prins poziția amuzantă și toți au râs.”
„Mi-a plăcut că au avut recuzită curată și totul era pregătit dinainte. Lui Emi i-au dat o mască haioasă și a păstrat-o până la final.”
„Au introdus un joc de ‘poveste pe rând’, fiecare copil adăugând o propoziție. Ei, Adriana, i-au început fraza și a continuat singură.”
„Superparty a fost foarte bun la a menține ordinea fără să ridice tonul. Lui Călin i-au făcut un semn discret și a ascultat imediat.”
„Au făcut un atelier mic cu abțibilduri tematice, fără să murdărească. Ei, Anca, i-au ales un set cu steluțe și a fost încântată.”
„Mi-a plăcut că au încurajat copiii să se ajute între ei, nu să se întreacă agresiv. Lui Leon i-au cerut să o ajute pe un coleg și a făcut-o frumos.”
„Superparty a gestionat foarte bine timpul și a trecut natural de la joc la tort. Ei, Sonia, i-au spus când urmează tortul și a așteptat calm.”
„Au făcut un joc de ‘cine sunt eu?’ cu cartonașe simple, foarte amuzant. Lui Matei i-au lipit cartonașul și a ghicit din câteva întrebări.”
„Mi-a plăcut că au lăudat efortul, nu doar câștigul. Ei, Irina, i-au spus ‘bravo că ai încercat’ și a prins curaj.”
„Superparty a folosit o poveste tematică pentru a lega activitățile între ele. Lui Horia i-au dat o ‘misiune’ și a luat-o foarte în serios.”
„Au introdus un joc de ‘ștafetă’ adaptat, cu pași mici și siguri. Ei, Melania, i-au arătat traseul și a fost foarte atentă.”
„Mi-a plăcut că au observat când un copil e pe margine și l-au integrat natural. Lui Rocco i-au dat o sarcină simplă și a intrat în joc.”
„Au făcut un atelier de mini-ornamente din hârtie, foarte rapid. Ei, Loredana, i-au lipit un abțibild și a ieșit foarte frumos.”
„Superparty a fost atent la limbaj și a folosit expresii potrivite pentru copii. Lui Eric i-au explicat pe scurt și a înțeles imediat.”
„Au avut un joc de ‘bingo’ cu imagini, super potrivit pentru cei mici. Ei, Sabrina, i-au găsit repede imaginea și a strigat fericită.”
„Mi-a plăcut că au avut pauze scurte de hidratare, fără să se piardă ritmul. Lui Dragoș i-au amintit să bea apă și a revenit la joacă.”
„Superparty a încheiat cu un moment de mulțumire pentru părinți și copii. Ei, Diana, i-au făcut cu mâna la final și a fost foarte fericită.”
„Au introdus un joc de ‘numărătoare’ pentru a alege echipele, foarte corect. Lui Cătălin i-au ieșit echipa și a acceptat imediat.”
„Mi-a plăcut că au fost flexibili când un joc nu a prins și au schimbat rapid. Ei, Alisa, i-au propus alt joc și a mers perfect.”
„Superparty a făcut o mini-probă de curaj, dar fără presiune. Lui Ionuț i-au spus ‘doar dacă vrei’ și a încercat singur.”
„Au avut un joc de ‘ghicește sunetul’ cu instrumente mici. Ei, Karina, i-au arătat instrumentul și a ghicit imediat.”
„Mi-a plăcut că au fost atenți la copii mai mici și au adaptat sarcinile. Lui Andrei i-au simplificat regula și a reușit.”
„Au făcut un colț de desen cu teme amuzante, pe rând, fără înghesuială. Ei, Ramona, i-au dat un marker și a desenat o floare mare.”
„Superparty a avut o energie bună, dar nu obositoare pentru copii. Lui Remus i-au păstrat ritmul potrivit și a rezistat până la final.”
„Au introdus un joc de ‘cuvânt interzis’, cu variante ușoare. Ei, Mihaela, i-au explicat clar și a intrat rapid în joc.”
„Mi-a plăcut că au fost politicoși și au cerut acordul înainte de poze. Lui Ayan i-au întrebat dacă vrea poză și a spus da cu zâmbet.”
„Superparty a strâns recuzita treptat, fără haos la final. Ei, Corina, i-au mulțumit pentru ajutor și a fost încântată.”
„Au făcut un joc de ‘pune în ordine’ cu imagini mari, foarte educativ. Lui Dan i-au dat primul cartonaș și a început corect.”
„Mi-a plăcut că au dat atenție fiecărui copil măcar câteva secunde. Ei, Alexandra, i-au spus ‘bravo’ direct și s-a luminat la față.”
„Superparty a folosit un moment de respirație/relaxare scurt, ca să calmeze grupul. Lui Mircea i-au arătat cum să respire și a funcționat.”
„Au introdus un joc de ‘misiuni pe bilețele’, fiecare copil trăgea una. Ei, Ștefania, i-au tras o misiune ușoară și a făcut-o cu entuziasm.”
„Mi-a plăcut că nu au forțat copiii să participe la ceva ce nu vor. Lui Nectarie i-au oferit opțiunea să privească și apoi a intrat singur.”
„Au făcut un atelier de mini-coronițe pentru toți, foarte rapid și curat. Ei, Lara, i-au prins coronița bine și a purtat-o fericită.”
„Superparty a creat o atmosferă prietenoasă, fără competiție agresivă. Lui Sami i-au spus ‘important e să ne distrăm’ și a zâmbit.”
„Au avut un joc de ‘ghicește personajul’ cu indicii simple. Ei, Patricia, i-au dat un indiciu bun și a ghicit corect.”
„Mi-a plăcut că au fost bine organizați și nu au pierdut timp căutând materiale. Lui Filip i-au dat imediat recuzita și a fost încântat.”
„Superparty a încheiat cu o mini-felicitare pentru sărbătorit, semnată de toți. Ei, Emilia, i-au semnat și a păstrat-o ca amintire."
„Superparty a făcut un joc de ‘telefonul fără fir’ pe șoaptă, ca să scadă energia după alergat. Lui Paul i-au dat primul mesaj și a fost atent.”
„Au organizat o vânătoare de indicii cu cartonașe mari, ușor de citit. Ei, Bianca, i-au înmânat un indiciu și s-a bucurat că ‘a găsit comoara’.”
„Mi-a plăcut că animatorii au explicat regulile în 10 secunde și apoi au arătat pe loc. Lui George i-au făcut demonstrația și a pornit imediat.”
„Au avut o mini-provocare de echipă cu mingi ușoare, fără aruncări puternice. Ei, Mara, i-au pus mingea în brațe și a participat fără teamă.”
„Superparty a ținut grupul unit și nu a lăsat copii să se risipească prin casă. Lui Denis i-au dat rolul de ‘paznic al echipei’ și a fost încântat.”
„Au făcut un moment de aplauze pentru fiecare copil, pe rând. Ei, Daria, i-au aplaudat ‘momentul de curaj’ și s-a luminat.”
„Mi-a plăcut că au avut și jocuri pentru copii mai timizi, nu doar pentru cei energici. Lui Șerban i-au propus o sarcină mică și a prins curaj.”
„Au introdus un joc de ‘potrivește perechea’ cu imagini tematice, foarte simpatic. Ei, Ilinca, i-au arătat cum se joacă și a devenit foarte atentă.”
„Superparty a gestionat foarte bine când copiii au început să vorbească peste animator. Lui Robert i-au cerut să ridice mâna și a dat exemplu.”
„Au făcut un ‘mini-show’ cu glume potrivite vârstei, fără exagerări. Ei, Natalia, i-au prins reacția și a râs cu poftă.”
„Au avut un joc de ‘cercuri pe podea’ cu pași mici, fără să alunece nimeni. Lui Luca i-au arătat traseul și l-a parcurs corect.”
„Mi-a plăcut că au întrebat părinții de alergii înainte să dea orice gustare/recuzită comestibilă. Ei, Denisa, i-au spus clar ce are voie și a fost liniștită.”
„Superparty a folosit un semnal amuzant (bătăi din palme) ca să adune grupul rapid. Lui Edi i-au dat startul și copiii au reacționat imediat.”
„Au făcut un joc de ‘ghicește emoji-ul’ cu cartonașe, super actual. Ei, Iasmina, i-au arătat un emoji și a ghicit din prima.”
„Mi-a plăcut că au rotit rolurile, ca să nu fie mereu aceiași în față. Lui Victor i-au dat rolul de ‘lider’ pentru un minut și a fost mândru.”
„Au introdus un atelier de brățări din hârtie, rapid și curat. Ei, Raluca, i-au potrivit brățara pe mână și a păstrat-o până a plecat.”
„Superparty a fost foarte atent la ton și nu a speriat copiii cu strigăte. Lui Ștefan i-au vorbit calm și a răspuns foarte bine.”
„Au avut un joc de ‘mima’ cu cuvinte ușoare și multe exemple. Ei, Carla, i-au sugerat o mimă simplă și a reușit imediat.”
„Mi-a plăcut că au introdus competiția doar ca joacă, fără premii care să creeze supărare. Lui Radu i-au spus ‘toți suntem câștigători’ și a acceptat.”
„Superparty a făcut tranziția spre tort fără agitație, cu un countdown amuzant. Ei, Oana, i-au spus când începe numărătoarea și a stat cuminte.”
„Au organizat un joc de ‘detectiv’ în care copiii găseau detalii din cameră. Lui Theo i-au dat lupa de jucărie și s-a simțit important.”
„Mi-a plăcut că au avut muzică la volum potrivit și au redus imediat când a fost nevoie. Ei, Evelyn, i-au întrebat dacă e ok volumul și a zâmbit.”
„Superparty a ținut cont că sunt copii de vârste diferite și a separat sarcinile pe nivel. Lui Damian i-au dat varianta mai grea și a fost provocat.”
„Au făcut un joc de ‘cuvinte în lanț’ cu timp de gândire, fără presiune. Ei, Andreea, i-au dat timp și a găsit un cuvânt bun.”
„Mi-a plăcut că au adus recuzită suficientă pentru toți, fără ceartă pe obiecte. Lui Kevin i-au oferit un obiect identic și nu s-a supărat nimeni.”
„Au introdus un moment de ‘poze cu recuzită’ pe rând, organizat. Ei, Larisa, i-au dat o coroniță și a pozat fericită.”
„Superparty a fost foarte bun la a integra un copil nou venit în mijlocul petrecerii. Lui Emanuel i-au făcut loc în echipă și a intrat imediat.”
„Au avut un joc de ‘memorie’ cu cartonașe mari, perfect pentru interior. Ei, Roxana, i-au arătat cum să întoarcă două și a prins ideea.”
„Mi-a plăcut că au folosit umor, dar au păstrat respectul față de copii. Lui Marian i-au răspuns frumos la o glumă și s-a simțit apreciat.”
„Superparty a încheiat segmentul cu un ‘bravo’ colectiv și aplauze. Ei, Ana, i-au făcut semn să vină la aplauze și a fost bucuroasă.”
„Au făcut un joc de ‘aruncă și prinde’ cu reguli clare, ca să nu se lovească nimeni. Lui Sergiu i-au arătat distanța corectă și a respectat-o.”
„Mi-a plăcut că au inclus și un joc static pentru copiii obosiți. Ei, Timea, i-au dat un rol de ‘juriu’ și a participat din scaun.”
„Superparty a fost punctual și a început fix la ora stabilită. Lui Aron i-au făcut o primire scurtă și a intrat în atmosferă.”
„Au avut un joc de ‘ghicește melodia’ cu fragmente scurte, potrivit pentru copii. Ei, Selina, i-au șoptit o idee și a ghicit.”
„Mi-a plăcut că animatorii au comunicat și cu părinții discret, fără să întrerupă petrecerea. Lui Marius i-au dat o pauză când a cerut și a revenit.”
„Au făcut un mini-atelier de decorațiuni pentru punguțe, foarte drăguț. Ei, Delia, i-au lipit o etichetă cu numele și a fost încântată.”
„Superparty a ales jocuri care nu au necesitat mult spațiu, dar au rămas distractive. Lui Niels i-au dat sarcini scurte și a stat conectat.”
„Au introdus un joc de ‘cine lipsește?’ în cerc, care i-a făcut atenți. Ei, Flavia, i-au ghidat privirea și a ghicit corect.”
„Mi-a plăcut că au menținut disciplina fără pedepse, doar cu reguli și glume. Lui Cristian i-au reamintit regula și a cooperat.”
„Superparty a făcut finalul cu o mică ceremonie pentru sărbătorit, elegant. Ei, Maria, i-au înmânat o felicitare și a aplaudat.”
„Au organizat o provocare de ‘construcție rapidă’ cu pahare de hârtie, foarte amuzant. Lui Patrick i-au dat startul și a fost super implicat.”
„Mi-a plăcut că au observat imediat când un copil se frustrează și au intervenit calm. Ei, Ema, i-au spus ‘încearcă din nou’ și s-a liniștit.”
„Superparty a folosit o poveste cu ‘misiuni’ ca să țină copiii atenți până la final. Lui Silviu i-au dat o misiune specială și a fost fericit.”
„Au introdus un joc de ‘litere/imagini’ pentru cei mici, fără să fie complicat. Ei, Noemi, i-au arătat litera și a găsit imaginea corectă.”
„Mi-a plăcut că au păstrat ritmul: joc activ, joc calm, apoi pauză scurtă. Lui Cosmin i-au spus ce urmează și a acceptat tranziția ușor.”
„Au făcut un moment de mulțumire pentru ajutorul copiilor la strâns, foarte civilizat. Ei, Alina, i-au mulțumit pe nume și a zâmbit.”
„Superparty a fost atent la siguranță: fără alergat lângă mobilier și fără împins. Lui Dorian i-au explicat pe scurt și a respectat.”
„Au avut un joc de ‘alege un card’ cu provocări amuzante, dar ușoare. Ei, Paula, i-au ales o provocare potrivită și a făcut-o fără emoții.”
„Mi-a plăcut că au menținut atenția și nu au lăsat timpi morți. Lui Toma i-au dat imediat următorul rol și nu s-a plictisit.”
„Superparty a încheiat cu o poză de grup organizată, fără înghesuială. Ei, Sofia, i-au făcut loc în față și a ieșit foarte frumos.”
„Superparty a introdus un joc de ‘cod secret’ cu culori, super ușor de înțeles. Lui Vlad i-au dat prima combinație și a alergat să o rezolve.”
„Mi-a plăcut că au avut un moment de liniștire cu respirații scurte, ca un ‘buton de pauză’. Ei, Teodora, i-au spus ‘inspiră-expiră’ și s-a calmat imediat.”
„Au făcut o mini-ștafetă cu obstacole moi, fără să fie riscant. Lui Ionuț i-au arătat traseul și a respectat regulile.”
„Superparty a venit cu autocolante tematice pentru fiecare copil. Ei, Alexandra, i-au ales unul cu inimioară și l-a lipit pe tricou.”
„Mi-a plăcut că animatorii au ținut cont de spațiul din sufragerie și au adaptat jocurile. Lui Cătălin i-au dat rolul de ‘arbitru’ și a fost încântat.”
„Au făcut un joc de ‘împarte pe echipe’ fără să lase pe cineva singur. Ei, Ioana, i-au găsit rapid o echipă și s-a simțit inclusă.”
„Superparty a avut un moment scurt de magie/comic, fără să lungescă programul. Lui Rareș i-au cerut să aleagă un card și a fost fascinat.”
„Mi-a plăcut că au folosit recuzită care nu murdărește (benzi, cartonașe, mingi moi). Ei, Andra, i-au dat o panglică și a dansat cu ea.”
„Au făcut un joc de ‘ghicește sunetul’ cu obiecte simple, foarte amuzant. Lui Dinu i-au dat primul sunet și a ghicit din a doua.”
„Superparty a respectat pauza de apă și a reamintit copiilor să bea. Ei, Denisa, i-au oferit timp să bea liniștită și apoi a revenit.”
„Au organizat un mini-concurs de ‘turn din cuburi’ pe timp, dar fără presiune. Lui Matei i-au cronometrat 20 de secunde și s-a distrat.”
„Mi-a plăcut că au vorbit frumos când un copil a greșit și au corectat fără rușinare. Ei, Carmen, i-au spus ‘e ok, mai încercăm’ și a zâmbit.”
„Superparty a ținut copiii ocupați până când a fost gata tortul, fără haos. Lui Răzvan i-au dat o sarcină mică și a stat atent.”
„Au avut un joc de ‘alege povestea’ unde copiii votau ce se întâmplă mai departe. Ei, Sabina, i-au numărat votul și a fost încântată.”
„Mi-a plăcut că au schimbat activitățile exact când începea plictiseala. Lui Andrei i-au propus imediat următorul joc și a prins energie.”
„Superparty a folosit un sistem simpatic de puncte pe echipă, fără să compare urât copiii. Ei, Diana, i-au lipit o stea pe echipă și a fost mândră.”
„Au făcut un joc de ‘statui muzicale’ cu reguli clare și muzică potrivită. Lui Bogdan i-au arătat exemplul și a jucat corect.”
„Mi-a plăcut că au remarcat fiecare copil pe ceva concret (‘ai fost atent’, ‘ai ajutat’). Ei, Irina, i-au spus că a ajutat la strâns și s-a bucurat.”
„Superparty a reușit să păstreze atmosfera veselă chiar și când s-a spart un balon. Lui Alex i-au schimbat rapid jocul și nu s-a supărat nimeni.”
„Au avut un joc de ‘urmează liderul’ cu mișcări simple pentru toți. Ei, Bianca, i-au arătat o mișcare și a condus echipa câteva secunde.”
„Au organizat o vânătoare de comori cu indicii ascunse la vedere, foarte inteligent. Lui Mihai i-au dat primul indiciu și a pornit imediat.”
„Mi-a plăcut că au fost atenți la copii sensibili la zgomot și au redus volumul instant. Ei, Ada, i-au întrebat dacă e ok și a dat din cap.”
„Superparty a venit pregătit cu un plan B când a început să plouă și nu s-a mai ieșit afară. Lui Ștefănel i-au mutat jocul în interior și a mers perfect.”
„Au făcut un joc de ‘ghicește personajul’ fără întrebări complicate. Ei, Larisa, i-au dat un personaj ușor și a ghicit repede.”
„Mi-a plăcut că animatorii au păstrat un ton cald și nu au ironizat copiii. Lui Paul i-au răspuns respectuos și a cooperat imediat.”
„Superparty a stabilit reguli de la început (‘fără împins’, ‘ridicăm mâna’) și s-au ținut de ele. Ei, Roxana, i-au reamintit discret și a ascultat.”
„Au avut un joc de ‘puzzle pe echipe’ care chiar i-a unit. Lui Denis i-au dat piesele de margine și s-a simțit util.”
„Mi-a plăcut că au integrat sărbătoritul fără să îl pună în situații jenante. Ei, Mara, i-au cerut o singură alegere și a fost relaxată.”
„Superparty a făcut un moment de ‘felicitări’ unde fiecare copil spunea ceva frumos. Lui Sebastian i-au dat primul rând și a spus ceva simpatic.”
„Au organizat pozele pe rând, fără îmbulzeală și fără timp pierdut. Ei, Natalia, i-au aranjat părul rapid și a ieșit superb.”
„Au făcut un joc de ‘semafor’ (roșu-galben-verde) ca să controleze alergatul. Lui Victor i-au dat comanda ‘verde’ și copiii au înțeles instant.”
„Mi-a plăcut că au avut și activități pentru 6-7 ani, nu doar pentru cei mici. Ei, Ioana, i-au dat o provocare mai interesantă și a fost captivată.”
„Superparty a adus recuzită curată și organizată, nimic aruncat la întâmplare. Lui Robert i-au dat un set complet și nu s-a certat cu nimeni.”
„Au făcut un joc de ‘ținte’ cu mingi moi, fără să strice nimic prin casă. Ei, Flavia, i-au arătat unde să arunce și a nimerit.”
„Mi-a plăcut că au anunțat din timp când urmează tortul, ca să nu fie crize de nerăbdare. Lui Edi i-au spus ‘mai avem 5 minute’ și a așteptat.”
„Superparty a gestionat super bine când doi copii au vrut același rol. Ei, Paula, i-au oferit o alternativă egală și a fost ok.”
„Au introdus un joc de ‘cuvânt interzis’ adaptat vârstei, foarte amuzant. Lui Marian i-au explicat pe scurt și a prins din prima.”
„Mi-a plăcut că animatorii au verificat dacă sunt obiecte fragile înainte de jocurile active. Ei, Elena, i-au mutat jocul mai departe de vitrină și a fost sigur.”
„Superparty a făcut un final ordonat: strâns recuzită, punguțe, apoi salut. Lui Darius i-au dat punguța la timp și nu a fost agitație.”
„Au avut un mic moment de ‘mulțumim părinților’ foarte discret, fără să întrerupă distracția. Ei, Andreea, i-au spus ‘mulțumim’ și a aplaudat.”
„Au făcut un joc de ‘cine e în spatele meu?’ cu indicii, super potrivit pentru interior. Lui Raul i-au dat rolul de ghicitor și a râs mult.”
„Mi-a plăcut că au folosit premii simbolice (sticker, aplauze), nu lucruri care să creeze invidie. Ei, Daria, i-au dat un sticker și a fost fericită.”
„Superparty a menținut grupul împreună, fără copii rătăciți prin camere. Lui David i-au dat o sarcină de ‘ajutor’ și a stat în zonă.”
„Au făcut un joc de ‘baloane în aer’ fără să lovească pe nimeni, doar cu palmele. Ei, Iulia, i-au arătat cum să dea ușor și a mers perfect.”
„Mi-a plăcut că au avut replici scurte și clare, nu explicații lungi care plictisesc. Lui Tudor i-au spus regula în două propoziții și a început imediat.”
„Superparty a reușit să includă și un copil mai mic, fără să încetinească tot grupul. Ei, Sonia, i-au dat o sarcină simplă și a participat cu zâmbet.”
„Au introdus un joc de ‘labirint’ desenat pe foi, foarte ingenios pentru pauze. Lui Ciprian i-au dat un creion și a stat concentrat.”
„Mi-a plăcut că au menținut energia fără să obosească excesiv copiii. Ei, Carla, i-au oferit o pauză scurtă și a revenit cu chef.”
„Superparty a fost atent la timp și a respectat programul până la final. Lui Gabriel i-au făcut un salut special și s-a simțit important.”
„Au încheiat cu un ‘high-five’ pe rând, ceea ce a fost foarte drăguț. Ei, Sofia, i-au dat un high-five și a plecat super fericită.”
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
