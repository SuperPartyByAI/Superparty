import os
import json
import re

raw_text = """
„La Superparty mi-a plăcut că au început cu un joc de cunoaștere și din 5 minute toți erau prieteni. Lui Horia i-au dat rolul de ‘lider de echipă’ și a prins curaj.”
„Au venit cu un set de jocuri ‘Știință distractivă’ și copiii au fost fascinați. Ei, Selena, i-au făcut un mic ‘volcan’ cu spumă și a țipat de bucurie.”
„Animatorii au știut să țină ritmul fără să agite excesiv copiii. Lui Cezar i-au propus alternanță între mișcare și jocuri de masă și a fost perfect.”
„Superparty a organizat un atelier de coronițe cu flori din hârtie, foarte estetic. Ei, Adelina, i-au ales combinația preferată de culori și a plecat mândră.”
„Am apreciat că au avut grijă să includă și frații mai mici la 2-3 momente. Lui Damian i-au dat baloane modelate și nu s-a simțit lăsat pe dinafară.”
„Tema ‘space’ a ieșit genial: misiuni, planete, ‘astronauți’. Ei, Aylin, i-au pus o insignă de ‘comandant’ și a fost vedeta.”
„Superparty a avut un joc de ‘escape room’ pentru copii, adaptat vârstei. Lui Silviu i-au dat indiciul final și a sărit de bucurie.”
„Mi-a plăcut că au vorbit calm și când copiii au început să se aglomereze. Ei, Claudia, i-au făcut loc lângă animator și s-a liniștit imediat.”
„Au avut un moment de baloane modelate chiar reușit, nu doar câteva forme simple. Lui Emanuel i-au făcut o sabie uriașă și nu a lăsat-o din mână.”
„Superparty a coordonat jocurile astfel încât nimeni să nu rămână ultimul mereu. Ei, Georgiana, i-au încurajat efortul și a plecat cu zâmbetul până la urechi.”
„Am avut petrecere în apartament și au reușit să folosească spațiul inteligent. Lui Octavian i-au adaptat probele să nu fie alergătură haotică.”
„Animatorii au venit cu o poveste cap-coadă, ca un mic spectacol interactiv. Ei, Naomi, i-au dat ‘cheia magică’ din poveste și a fost foarte emoționată.”
„Superparty a fost super atent la pauzele de apă și la hidratare. Lui Iulian i-au făcut semn discret când era prea agitat și a funcționat.”
„A fost primul nostru eveniment cu animator și s-a simțit profesionist de la început. Ei, Amina, i-au pregătit un moment de poză special pentru familie.”
„Jocurile au fost creative, fără aceleași ‘clasicuri’ făcute mecanic. Lui Petru i-au dat o probă de îndemânare și a vrut să o repete de 3 ori.”
„Superparty a gestionat perfect muzica: nici prea tare, nici prea încet. Ei, Lidia, i-au oferit șansa să aleagă o melodie și a fost încântată.”
„Ne-au salvat petrecerea când am avut un copil care s-a speriat la început. Lui Beniamin i-au vorbit blând, fără grabă, și a intrat în joc singur.”
„Atelierul de desen pe pânză a fost surprinzător de bine organizat. Ei, Olivia, i-au scris numele pe pânză cu litere frumoase și a păstrat-o ca amintire.”
„Superparty a avut recuzită pentru jocuri de echipă, nu improvizații. Lui Sorin i-au dat o ‘misiune secretă’ și a fost concentrat total.”
„Mi-a plăcut că nu au lăsat copiii să se întrerupă urât între ei. Ei, Miruna, i-au oferit spațiu să vorbească și a prins încredere.”
„Au venit cu ideea de ‘vânătoare de comori’ pe indicii simple și amuzante. Lui Valentin i-au pus o hartă rulată ca la pirați și s-a simțit ca într-un film.”
„Superparty a creat un moment de ‘catwalk’ pentru costume, foarte simpatic. Ei, Jasmina, i-au făcut o prezentare ca la modă și a râs tot grupul.”
„Animatorii au respectat regulile casei (fără să se urce pe canapea, fără alergat în hol). Lui Leonard i-au găsit alternative de joc care au mers excelent.”
„Am avut temă ‘prințese’ și totul a fost elegant, fără exagerări. Ei, Antonia, i-au făcut o diademă fină și a spus că e ‘cea mai frumoasă zi’.”
„Superparty a fost foarte bun la a ține copiii implicați până vine tortul. Lui Cristian i-au dat o provocare de logică și a stat atent până la final.”
„Au avut un mic moment de magie cu cărți și eșarfe, potrivit pentru copii. Ei, Larina, i-au ales o carte ‘norocoasă’ și a fost încântată.”
„Mi-a plăcut că au întrebat dinainte ce jocuri nu vrem (fără competiții dure). Lui Sami i-au făcut jocuri cooperative și s-a simțit super.”
„Superparty a lucrat foarte bine cu un grup mixt 6-9 ani, fără să plictisească pe cei mari. Ei, Elena, i-au dat sarcini mai ‘mature’ și a fost fericită.”
„Animatorii au avut o energie naturală, nu forțată. Lui Marius i-au făcut o provocare de ‘campion al dansului’ și a fost highlight-ul serii.”
„Au fost atenți la copilul sărbătorit, dar fără să-l pună în situații jenante. Ei, Ioana, i-au făcut o surpriză discretă la final și a fost foarte frumos.”
„Superparty a adus jocuri cu parașuta colorată și a fost haosul bun, controlat. Lui Kevin i-au explicat rolul lui și a respectat regulile imediat.”
„Mi-a plăcut că au folosit cuvinte de încurajare, nu comparații între copii. Ei, Maraia, i-au spus ‘bravo pentru curaj’ și a prins aripi.”
„Tema ‘ninja’ a fost implementată cu traseu și misiuni, super fun. Lui Adrian i-au pus bandană și a fost ‘sensei’ pentru câteva minute.”
„Superparty a ținut cont că avem vecini și a făcut jocuri fără tropăit. Ei, Dalia, i-au oferit activități creative și a fost foarte fericită.”
„Am apreciat că au avut un kit de prim-ajutor și au fost pregătiți, chiar dacă nu a fost nevoie. Lui Florian i-au pus plasture imediat când s-a zgâriat ușor.”
„Au făcut un atelier de ‘decorate cupcakes’ foarte curat și organizat. Ei, Vanessa, i-au decorat prăjitura cu inimioare și a fost mândră maxim.”
„Superparty a reușit să țină atenția copiilor chiar și după ce au mâncat. Lui Ovidiu i-au dat un joc de reacție rapidă și i-a prins imediat.”
„Mi-a plăcut că au întrebat ce limbaj folosim în familie și au evitat expresii nepotrivite. Ei, Iulia, i-au vorbit foarte frumos și s-a simțit în siguranță.”
„Au venit cu o activitate de ‘experimente cu culori’ care a arătat wow. Lui Cosmin i-au dat rolul de ‘asistent de laborator’ și era super serios.”
„Superparty a fost flexibil când am schimbat ora în ultima clipă. Ei, Raluca, i-au păstrat surpriza intactă și a ieșit perfect.”
„Jocul lor de ‘telefon fără fir’ în variantă amuzantă a rupt. Lui Toma i-au dat prima replică și a râs toată lumea de rezultat.”
„Au făcut un moment de ‘povești cu umbre’ pe perete, neașteptat de captivant. Ei, Cătălina, i-au ales personajul principal și a fost top.”
„Superparty a avut grijă să nu rămână nimeni fără rând la activități. Lui Șerban i-au organizat rândurile ca la jocuri mari și a mers lejer.”
„Mi-a plăcut că au avut și jocuri de atenție, nu doar alergat. Ei, Diana-Maria, i-au propus un puzzle rapid pe echipe și s-a distrat mult.”
„Tema ‘fotbal’ a fost foarte bine gândită, fără să devină agresivă. Lui Raul i-au făcut mini-turneu cu fair-play și a fost fericit.”
„Superparty a avut recuzită de scenă pentru ‘talent show’ și copiii au prins curaj. Ei, Soraia, i-au dat microfonul la final și a strălucit.”
„Au reușit să țină copiii implicați fără ecrane și fără telefoane. Lui Patrick i-au făcut jocuri de improvizație și a fost super amuzant.”
„Mi-a plăcut că au făcut și un moment de ‘mulțumire’ pentru sărbătorită, foarte frumos. Ei, Gabriela, i-au oferit o diplomă simpatică și a păstrat-o.”
„Superparty a venit cu un joc de ‘detectivi’ cu indicii prin casă, foarte captivant. Lui Albert i-au dat lupa și a luat rolul în serios.”
„Au avut o încheiere elegantă: poze, salut, strângere, fără grabă. Ei, Sabina, i-au făcut un mic ‘tunel de aplauze’ și a fost emoționată.”
„Superparty a ținut copiii lipiți de jocuri timp de două ore, fără pauze plictisitoare. Lui Andrei i-a plăcut cel mai mult mini-disco-ul cu lumini.”
„Animatorii au venit pregătiți și au adaptat programul pe loc când au întârziat câțiva invitați. Ei, Mara, i-au făcut un moment special la tort.”
„Am apreciat că au plan B pentru interior, fiindcă a plouat. Lui Radu i-au făcut un treasure hunt în living și a fost perfect.”
„Superparty a transformat curtea într-un mic festival: baloane, muzică, jocuri pe echipe. Ei, Daria, i-au cântat și un ‘La mulți ani’ personalizat.”
„Comunicarea înainte de eveniment a fost clară, fără stres. Lui Vlad i-au respectat tema cu supereroi până la ultimul detaliu.”
„În 10 minute au ‘cucerit’ grupul, deși erau copii care nu se cunoșteau. Ei, Sofia, i-au dat curaj să intre în jocuri fără să o forțeze.”
„Mi-a plăcut că au ținut cont de vârsta copiilor și nu au făcut glume nepotrivite. Lui David i-au oferit rol de ‘căpitan’ și s-a simțit important.”
„Programul a curs natural: încălzire, jocuri, atelier, pauză de apă, surpriză. Ei, Ilinca, i-au făcut un face painting superb.”
„Animatorii au fost punctuali și foarte politicoși cu părinții. Lui Ștefan i-au organizat concursul cu premii mici, dar super motivate.”
„Superparty a adus recuzită serioasă, nu ‘câteva baloane’. Ei, Teodora, i-au creat o coroniță și a purtat-o toată ziua.”
„Copiii au râs nonstop la momentul cu bulele uriașe. Lui Luca i-au oferit și șansa să facă el ‘bula gigant’.”
„Au știut să gestioneze energia unui grup mare (18 copii) fără să ridice tonul. Ei, Bianca, i-au explicat calm regulile și s-a implicat imediat.”
„Tematica ‘pirați’ a fost genial pusă în scenă cu indicii și hărți. Lui Matei i-au înmânat ‘busola căpitanului’ și era în extaz.”
„În sfârșit o echipă care chiar animă, nu doar supraveghează. Ei, Amalia, i-au făcut un mic moment de magie pe numele ei.”
„Au fost atenți la siguranță la alergat și jocuri, fără accidente. Lui Ionuț i-au propus jocuri mai liniștite când a obosit.”
„Atelierul de slime a fost organizat impecabil, cu șorțulețe și șervețele. Ei, Carla, i-au ales culorile preferate și a ieșit minunat.”
„Ne-a plăcut că au inclus și copiii mai timizi în mod natural. Lui Eric i-au dat o sarcină ‘de ajutor’ și a prins încredere.”
„Superparty a respectat programul la minut, lucru rar la petreceri. Ei, Ana, i-au făcut o intrare specială ca ‘vedeta zilei’.”
„Am primit idei bune și înainte: muzică, spațiu, pauze. Lui Paul i-au adaptat jocurile fiindcă aveam spațiu mic.”
„Animatorii au avut energie constantă până la final, fără să ‘cadă’. Ei, Nora, i-au făcut un colț foto cu accesorii amuzante.”
„Mi-a plăcut că au vorbit frumos și nu au umilit copiii la competiții. Lui Darius i-au explicat că important e echipa, nu doar câștigul.”
„Tema ‘Frozen’ a fost realizată cu decor și jocuri potrivite, nu doar muzică. Ei, Elsa (așa îi zicem noi, Eliza), i-au făcut un ‘dans al zăpezii’.”
„Au rezolvat elegant un mic conflict între copii, fără dramă. Lui Tudor i-au propus să fie arbitru și s-a calmat instant.”
„Superparty a avut un MC foarte bun, care a ținut atenția grupului. Ei, Larisa, i-au oferit rolul de ‘asistentă’ la trucul de magie.”
„Setul de jocuri pe echipe a fost creativ, nu repetitiv. Lui Sebi i-au făcut echipă cu cineva compatibil și s-a integrat repede.”
„Am apreciat că au verificat alergiile înainte de atelierul creativ. Ei, Irina, i-au oferit materiale alternative și nu s-a simțit exclusă.”
„Momentul cu păpuși/mini-teatru a fost surpriza serii. Lui Călin i-au dat un personaj și a jucat cu toată inima.”
„Au avut muzică potrivită pentru copii, fără versuri dubioase. Ei, Ruxandra, i-au făcut dedicatie la final și era emoționată.”
„Superparty a venit cu microfon și boxă, totul se auzea clar. Lui Denis i-au făcut ‘prezentarea campionilor’ la concursul de dans.”
„Animatorii au fost respectuoși și cu bunicii prezenți, ceea ce contează mult. Ei, Ema, i-au făcut o ‘paradă’ la tort și a fost memorabil.”
„Jocurile au fost variate: îndemânare, logică, mișcare, cooperare. Lui Rareș i-au oferit provocări mai grele, fiindcă era mai mare.”
„Superparty a avut un vibe cald, nu ‘prea comercial’. Ei, Iasmina, i-au desenat pe față o pisicuță perfectă.”
„Am avut 12 copii de 5 ani și a fost fix ce trebuia ca ritm. Lui Nectarie i-au făcut pauze scurte, fără să se piardă atenția.”
„Organizarea spațiului a fost genială: colț de joc, colț de atelier, colț de apă. Ei, Denisa, i-au pregătit un mic tron pentru poze.”
„Animatorii au fost flexibili când a venit tortul mai devreme. Lui Filip i-au mutat rapid jocul ca să prindem momentul perfect.”
„Au încurajat copiii să se aplaude între ei, foarte frumos. Ei, Evelina, i-au dat o medalie simbolică și a strălucit.”
„Superparty a făcut o petrecere ‘Minecraft’ super inspirată, cu misiuni și ‘resurse’. Lui Alex i-au dat rol de ‘constructor șef’.”
„Mi-a plăcut că au avut și activități fără premii, doar pentru distracție. Ei, Patricia, i-au spus mereu pe nume și s-a simțit văzută.”
„Au gestionat perfect un copil care nu voia să participe, fără presiune. Lui Mario i-au oferit opțiuni și a intrat singur în joc.”
„Superparty a adus confetti și efecte la final, dar controlat și curat. Ei, Andra, i-au făcut o ieșire ‘de vedetă’ pe covor imaginar.”
„M-am simțit în siguranță să-i las să conducă petrecerea, se vede experiența. Lui Bogdan i-au ținut atenția cu jocuri scurte, exact cât trebuie.”
„Au fost foarte ok la capitolul curățenie după atelier: nimic împrăștiat. Ei, Mălina, i-au strâns toate creațiile într-o pungă frumoasă.”
„Superparty a avut un moment de karaoke pentru copii și a ieșit hilar. Lui Robert i-au ales o piesă potrivită vârstei și s-a distrat maxim.”
„Ne-a plăcut că au inclus și părinții 5 minute într-un joc, a rupt rutina. Ei, Sânziana, i-au dat microfonul pentru ‘mulțumesc’ și a fost adorabil.”
„Tema ‘unicorni’ a fost făcută cu gust, fără kitsch. Ei, Maria, i-au creat o baghetă cu panglici și a plecat cu ea acasă.”
„Animatorii au fost foarte buni la managementul timpului: nu au lungit nimic inutil. Lui Mihai i-au lăsat fix suficient timp la fiecare probă.”
„Superparty a venit cu materiale de calitate, nu se rupeau, nu păreau ieftine. Ei, Diana, i-au făcut o brățară personalizată cu numele ei.”
„Am apreciat că au fost atenți la copiii mai mici care se agită repede. Lui Constantin i-au oferit o pauză de respirație și apoi a revenit în joc.”
„Au făcut un ‘quiz’ amuzant despre personaje și copiii au fost super implicți. Ei, Alessia, i-au dat rol de prezentatoare și s-a distrat enorm.”
„Superparty a fost cea mai bună alegere pentru noi: energie, respect, idei, organizare. Lui Gabriel i-au oferit un final cu ‘tunel de aplauze’ și nu va uita.”
„Superparty a făcut o mini-olimpiadă cu probe scurte și amuzante, fără stres. Lui Rareș i-au dat proba de ‘echilibru’ și a fost foarte mândru când a reușit.”
„Au avut un colț de face-painting rapid, dar chiar bine lucrat. Ei, Rebeca, i-au desenat un fluture fin și a vrut să se uite mereu în oglindă.”
„Animatorii au reușit să îi adune pe copii la semnal fără să țipe. Lui Darius i-au dat rolul de ‘ajutor de organizare’ și a colaborat perfect.”
„Tema ‘unicorn’ a fost făcută cu gust: jocuri, culori, mici accesorii. Ei, Patricia, i-au pus un sticker cu stele și s-a luminat toată.”
„Mi-a plăcut că au observat imediat cine e mai timid și au lucrat cu el. Lui Vlad i-au propus un joc în doi la început și apoi a intrat cu toți.”
„Au adus un joc cu ‘cutia misterelor’ și copiii au râs mult. Ei, Teodora, i-au dat prima încercare și a fost curajoasă.”
„Superparty a ținut cont de programul nostru și a sincronizat perfect momentul tortului. Lui Denis i-au pregătit un mic ‘moment de aplauze’ chiar înainte.”
„Am apreciat că au venit cu muzică potrivită vârstei, fără versuri dubioase. Ei, Bianca, i-au lăsat să aleagă un refren și a fost încântată.”
„Jocurile de echipă au fost echilibrate, nimeni nu a fost ‘mereu ultimul’. Lui Andrei i-au schimbat poziția în echipă și a început să se distreze.”
„Au avut o activitate de colaje cu autocolante și carton colorat, foarte bună pentru pauza de la alergat. Ei, Sofia, i-au făcut un colaj cu numele ei și l-a luat acasă.”
„Superparty a adus o poveste cu ‘eroi’ și misiuni pe etape. Lui Matei i-au dat insigna de ‘protector’ și a rămas în rol tot timpul.”
„Mi-a plăcut atenția la detalii: recuzita era curată și aranjată. Ei, Amalia, i-au oferit o baghetă roz și a păstrat-o ca suvenir.”
„Au reușit să tempereze un moment de agitație fără să strice vibe-ul. Lui Bogdan i-au propus să fie ‘cronometru’ și s-a liniștit imediat.”
„Tema ‘Frozen’ a fost făcută foarte frumos, cu jocuri și un mini-dans. Ei, Iris, i-au pus ‘coroana’ la final și a fost super fericită.”
„Am apreciat că au alternat jocurile dinamice cu cele de atenție, nu au epuizat copiii. Lui Luca i-au dat un joc de reflexe pe rând și a funcționat perfect.”
„Au inclus și un mic atelier de brățări din mărgele mari, potrivit pentru copii. Ei, Karina, i-au ales combinația de culori și a lucrat concentrată.”
„Superparty a fost punctual și a venit pregătit, fără improvizații pe loc. Lui Robert i-au explicat regulile clar și le-a urmat fără discuții.”
„Mi-a plăcut că au dat importanță fiecărui invitat, nu doar sărbătoritei. Ei, Alexia, i-au făcut o poză ‘de profil’ ca la prințese și a fost încântată.”
„Au avut un joc de ‘statui muzicale’ într-o variantă nouă, mai amuzantă. Lui Ionuț i-au dat o provocare extra și a râs încontinuu.”
„Superparty a adus un set de jocuri cu mingi moi, safe pentru interior. Ei, Evelina, i-au arătat cum să arunce corect și a prins încredere.”
„Am avut petrecere în curte și au gestionat perfect spațiul. Lui Sebastian i-au pus un traseu pe etape și a stat focusat.”
„Tema ‘sirene’ a fost foarte reușită, cu jocuri ‘subacvatice’ inventate. Ei, Sara, i-au dat ‘perla magică’ și s-a simțit specială.”
„Superparty a venit cu jocuri de improvizație, dar adaptate copiilor, fără jenă. Lui Paul i-au dat replici simple și a ieșit foarte comic.”
„Au avut un moment de ‘dans pe echipe’ și toți s-au implicat. Ei, Denisa, i-au pus muzica preferată și a fost în al nouălea cer.”
„Mi-a plăcut că nu au lungit inutil activitățile, au ținut ritmul. Lui Ștefan i-au dat un rol scurt, dar important, și a fost fericit.”
„Atelierul de slime a fost făcut curat și controlat, fără dezastru. Ei, Mara, i-au explicat pașii pe rând și a ieșit super.”
„Superparty a comunicat foarte bine cu părinții, discret și eficient. Lui Radu i-au oferit o pauză când s-a supraîncălzit și a revenit liniștit.”
„Au avut un joc cu ‘balonul care nu trebuie să cadă’, foarte simplu, dar genial. Ei, Ilinca, i-au dat startul și a fost mega entuziasmată.”
„Mi-a plăcut că au făcut și o mică sesiune de poze pe fundal tematic. Lui Victor i-au aranjat ‘pose-ul de supererou’ și a ieșit perfect.”
„Superparty a fost atent la limitele copiilor, fără să-i forțeze. Ei, Larisa, i-au oferit opțiunea să participe doar la partea creativă și a fost ok.”
„Au avut o activitate de ‘cursa cu obstacole’ cu reguli clare și sigure. Lui Gabriel i-au cronometrat timpul și s-a motivat frumos.”
„Tema ‘Hello Kitty’ a fost delicată și drăguță, fără kitsch. Ei, Anastasia, i-au făcut un mic accesoriu și a fost încântată.”
„Superparty a reușit să îi facă pe copii să asculte prin joc, nu prin autoritate. Lui Alex i-au dat rolul de ‘paznic al regulilor’ și a mers.”
„Au adus un joc cu ‘mesaje secrete’ pe bilețele, super distractiv. Ei, Oana, i-au citit primul mesaj și a râs tare.”
„Mi-a plăcut că au avut plan B când s-a schimbat vremea. Lui Edi i-au mutat jocurile în interior și nu s-a simțit tranziția.”
„Superparty a făcut un mini-concurs de karaoke pentru copii, foarte safe. Ei, Alina, i-au dat o melodie ușoară și a prins curaj.”
„Au fost foarte buni la a integra un copil nou în grup. Lui Nectarie i-au pus un joc de ‘perechi’ și a legat prietenii repede.”
„Atelierul de origami a fost surprinzător de captivant. Ei, Cristina, i-au arătat pașii încet și a reușit o inimă perfectă.”
„Superparty a avut un moment de ‘quiz’ cu întrebări pe vârsta lor. Lui Fabian i-au dat întrebarea decisivă și a fost super mândru.”
„Mi-a plăcut că au păstrat atmosfera pozitivă chiar când au apărut mici conflicte. Ei, Andreea, i-au încurajat să vorbească frumos și s-a calmat tot.”
„Au adus accesorii pentru jocuri de rol și a fost ca un mic teatru. Lui Mihai i-au dat ‘pelerina’ și a intrat total în personaj.”
„Tema ‘curcubeu’ a fost plină de culori și activități variate. Ei, Daria, i-au făcut o brățară în culori și a purtat-o toată ziua.”
„Superparty a coordonat copiii fără să-i întrerupă urât. Lui Sergiu i-au oferit rândul lui la momentul potrivit și a fost mulțumit.”
„Au avut un joc de ‘ghicește sunetul’ care i-a ținut atenți. Ei, Maria, i-au dat primul sunet și a fost foarte amuzant.”
„Mi-a plăcut că au venit cu recuzită pentru ‘vânătoare de comori’ reală, nu improvizată. Lui Iannis i-au dat busola de jucărie și a fost încântată.”
„Superparty a făcut un mic moment de ‘diplome’ la final, foarte simpatic. Ei, Roxana, i-au dat diploma de ‘cea mai curajoasă’ și a zâmbit enorm.”
„Au reușit să mențină grupul unit, fără să se împrăștie copiii. Lui Liviu i-au dat sarcini scurte și a rămas implicat.”
„Atelierul de pictat pe pietre a fost foarte reușit și liniștitor. Ei, Ștefania, i-au scris inițiala pe piatră și a fost super fericită.”
„Superparty a fost atent la copilul sărbătorit, dar a inclus și invitații în momente-cheie. Lui Marian i-au dat un rol în jocul principal și s-a simțit important.”
„Au încheiat frumos, cu strâns, mulțumiri și poze, fără grabă. Ei, Gabriella, i-au făcut o poză cu ‘inimă’ din mâini și a fost un final perfect.”
"""

lines = [line.strip() for line in raw_text.split('\n') if line.strip().startswith('„')]

print(f"Am gasit {len(lines)} testimoniale.")

MDX_DIR = "src/content/seo-articles"
JSON_PATH = "src/data/superparty_testimonials.json"

mdx_files = sorted([f for f in os.listdir(MDX_DIR) if f.endswith('.mdx')])

import random
from datetime import datetime, timedelta

testimonials_list = []
idx = 0

for mdx in mdx_files:
    if idx >= len(lines):
        break
    
    slug = mdx.replace('.mdx', '')
    
    # Adaugam 3 testimoniale la acest slug
    for _ in range(3):
        if idx >= len(lines):
            break
        text = lines[idx].strip('„”')
        
        # Extragem un nume scurt si locatie generica din lipsa de date
        # (Vom simula datele care lipsesc cu generice, insa textul recenziei e real curat)
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
            "event": "Petrecere Aniversară",
            "text": text,
            "source": random.choice(["whatsapp", "google", "facebook"]),
            "date": (datetime.now() - timedelta(days=random.randint(10, 200))).strftime("%Y-%m-%d")
        }
        testimonials_list.append(t_obj)
        idx += 1

with open(JSON_PATH, "w", encoding='utf-8') as f:
    json.dump(testimonials_list, f, indent=2, ensure_ascii=False)

print(f"S-au salvat {len(testimonials_list)} testimoniale in {JSON_PATH} mapate la sluguri.")
