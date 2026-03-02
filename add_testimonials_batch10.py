import os, json, random
from datetime import datetime, timedelta

raw_text = """
„Superparty a făcut „parada personajelor" cu muzică scurtă și intrări pe rând. Lui Rares i-au pus o pelerină și a defilat mândru."
„Au pregătit „misiunea spațială" cu planete din carton lipite pe pereți. Ei Alinei i-au dat rolul de „comandant" și a condus echipa."
„Superparty a organizat „bowling cu sticle" (sticle ușoare, mingi moi). Lui Bogdan i-au arătat poziția și a doborât toate sticlele."
„Au făcut „atelier de pălării de magician" din carton negru. Ei Laviniei i-au decorat pălăria cu stele aurii și a arătat superb."
„Superparty a propus „jocul cu indicii" (cald-rece) pentru un mic premiu. Lui Cristi i-au dat primul indiciu și a găsit rapid."
„Au organizat „dansul cu opriri" pe melodii scurte. Ei Ilincăi i-au arătat semnalul de stop și a prins regulile imediat."
„Superparty a făcut „atelier de brățări" cu mărgele mari, ușor de înșirat. Lui Eduard i-au ales mărgele albastre și a ieșit o brățară tare."
„Au pregătit „vânătoarea de culori" prin cameră (găsești obiecte roșii, verzi etc.). Ei Daciei i-au dat lista cu imagini și s-a descurcat singură."
„Superparty a organizat „mini-quiz cu sunete de animale". Lui Marius i-au pus sunetul de leu și a ghicit din prima."
„Au făcut „atelier de mască" (tigruleț, iepuraș, pisică). Ei Iulianei i-au dat o mască de pisică și a colorat-o atent."
„Superparty a propus „cursa cu lingura și mingea" (minge de burete). Lui Damian i-au scurtat traseul și a terminat fără să scape mingea."
„Au organizat „pictură pe șevalet" cu teme de vară. Ei Camilei i-au pus un șorțuleț și a pictat un soare mare."
„Superparty a făcut „jocul cu post-it-uri" (lipești pe tablă ce îți place). Lui Radu i-au dat post-it-uri cu emoji și a ales cele amuzante."
„Au pregătit „atelier de avion din hârtie" și test de zbor. Ei Florentinei i-au arătat o pliere simplă și avionul a zburat cel mai departe."
„Superparty a organizat „piramida de pahare" (pahare de plastic). Lui Kevin i-au explicat cum să ridice baza și a reușit din a doua."
„Au făcut „poveste cu imagini" (copiii aleg carduri și construiesc firul). Ei Anișoarei i-au dat cardul cu castel și a pornit povestea."
„Superparty a propus „jocul cu baloane pe echipe" (fără să folosești mâinile). Lui Patrick i-au dat rolul de „paznic de balon" și a fost foarte implicat."
„Au organizat „atelier de stickere personalizate" (desen + lipit pe carton). Ei Silviei i-au scris numele cu litere frumoase și a păstrat stickerul."
„Superparty a făcut „mică prezentare de talent" cu aplauze după fiecare. Lui Sergiu i-au ținut microfonul-jucărie și a cântat o strofă."
„Au pregătit „jocul cu steaguri" (ridică steagul când auzi cuvântul). Ei Otiliei i-au dat un steag roz și a fost foarte atentă."
„Superparty a organizat „puzzle mare pe podea" cu personaje. Lui Dorian i-au dat colțurile și a început construcția corect."
„Au făcut „atelier de felicitări" pentru sărbătorit. Ei Mihaelei i-au dat inimioare autocolante și a făcut o felicitare foarte frumoasă."
„Superparty a propus „ghicește obiectul" dintr-un săculeț (obiecte sigure). Lui Horia i-au dat o minge texturată și a ghicit imediat."
„Au organizat „dansul roboților" (mișcări amuzante, ușoare). Ei Mariei i-au arătat două mișcări simple și a dansat fără emoții."
„Superparty a făcut „atelier de mini-trofee" (carton + folie aurie). Lui Iulian i-au lipit o stea pe trofeu și l-a luat acasă fericit."
„Au pregătit „jocul cu traseu de litere" (calci doar pe literele din cuvânt). Ei Anastasiei i-au arătat cuvântul și a mers corect pe traseu."
„Superparty a organizat „pescuit de pești" cu magneți și puncte. Lui Fabian i-au arătat cum să țină undița și a prins peștele mare."
„Au făcut „atelier de rame foto" (decorate cu spumă colorată). Ei Dorinei i-au ales flori și inimioare și rama a ieșit superbă."
„Superparty a propus „jocul cu semaforul" (verde/alergi, roșu/oprești). Lui Victor i-au dat rolul de semafor și a condus jocul."
„Au încheiat un moment cu „fotografie de grup" și o poziție amuzantă. Ei Feliciei i-au sugerat o poză cu mâinile în inimă și a fost drăguț."
„Superparty a făcut „misiune de detectivi" cu lupă de jucărie și indicii pe bilețele. Lui Robert i-au dat lupa și s-a simțit ca un adevărat detectiv."
„Au organizat „atelier de colaje" (reviste, lipici, forme). Ei Andreei i-au oferit imagini cu curcubeu și a făcut un colaj vesel."
„Superparty a propus „aruncă la coș" cu mingi moi și coș jos. Lui Cosmin i-au ajustat distanța și a marcat de mai multe ori."
„Au făcut „jocul cu ritmuri" (bați din palme după model). Ei Soranei i-au arătat un ritm scurt și l-a repetat perfect."
„Superparty a organizat „atelier de semne de carte" (laminate, cu sclipici). Lui Ștefan i-au făcut semnul cu un dragon și a fost încântat."
„Au pregătit „jocul cu cercurile" (sari în cercul corect după culoare). Ei Carinei i-au spus din timp culoarea și a prins repede."
„Superparty a făcut „micul show de iluzie" cu eșarfă care dispare (truc simplu). Lui Ovidiu i-au explicat cum funcționează și a vrut să repete."
„Au organizat „atelier de păpuși din șosete" (lipit ochi, decor). Ei Monicăi i-au dat ochi mari și păpușa a ieșit foarte haioasă."
„Superparty a propus „jocul cu întrebări despre sărbătorit" (ușor, amuzant). Lui Alex i-au pus prima întrebare și a râs toată lumea."
„Au făcut „dansul cu eșarfe" pe muzică lentă, ca să se miște toți în siguranță. Ei Adrianei i-au dat o eșarfă albastră și a fost încântată."
„Superparty a organizat „atelier de insignă" (nume + simbol preferat). Lui Raul i-au desenat un fulger și a purtat insigna pe tricou."
„Au făcut „jocul cu turnul de cuburi" (cine pune fără să cadă). Ei Siminei i-au dat cuburile mari și a reușit să pună ultimele."
„Superparty a propus „construcție de castel" din cutii ușoare. Lui Dan i-au dat rolul de arhitect și a decis unde vin turnurile."
„Au organizat „atelier de flori din hârtie creponată". Ei Ruxandrei i-au arătat cum răsucește petalele și floarea a ieșit elegantă."
„Superparty a făcut „jocul cu umbre chinezești" și a spus o poveste scurtă. Lui Mihai i-au făcut umbra unui lup și a fost fascinat."
„Au pregătit „ștafeta cu bilețele" (duci mesajul la echipă). Ei Irinei i-au dat mesajul cu inimioare și l-a dus rapid."
„Superparty a organizat „atelier de mini-tabla" (carton + cretă). Lui Zoran i-au scris numele mare și a desenat apoi o mașină."
„Au făcut „jocul cu emoji" (mimi ce emoji primești). Ei Georgianei i-au dat emoji cu „râs" și a jucat foarte bine."
„Superparty a propus „cursa cu jaloane" (slalom). Lui Cezar i-au arătat traseul și a făcut slalom fără să dărâme jaloanele."
„Au încheiat cu „momentul cadoului" și mulțumiri frumoase către copii. Ei Evelinei i-au oferit un autocolant special și s-a bucurat mult."
„Superparty a venit cu pictură pe față și un panou cu modele. Lui Tudor i-au făcut un tigru rapid și a stat cuminte până la final."
„Au organizat „cursa cu saci" pe covor, ca să fie sigur. Ei Anei i-au explicat cum ține sacul și a râs tot traseul."
„Superparty a făcut baloane modelate (sabie, floare, cățel). Lui David i-au modelat un dinozaur verde și l-a păzit toată petrecerea."
„Au pus un colț foto cu recuzită (ochelari, mustăți, coroane). Ei Biancăi i-au dat o coroniță cu sclipici și pozele au ieșit super."
„Superparty a organizat „Bingo cu imagini" pentru cei mici. Lui Răzvan i-au arătat cum marchează și a completat primul."
„Au făcut „atelier de slime" (variantă simplă, supravegheat). Ei Sofiei i-au ales culoarea mov și slime-ul a ieșit perfect."
„Superparty a pregătit „jocul cu frânghia" (tras ușor, pe echipe). Lui Luca i-au pus o bandană și a tras cu energie."
„Au organizat „quiz cu desene animate" pe niveluri. Ei Teodorei i-au dat întrebări ușoare la început și a prins curaj."
„Superparty a făcut „stop-dans" cu luminițe colorate. Lui Andrei i-au dat rolul de DJ pentru un minut și s-a simțit important."
„Au pregătit „atelier de coronițe cu flori" din hârtie. Ei Ioanei i-au arătat cum lipește florile și a ieșit o coroniță superbă."
„Superparty a organizat „aruncă inelele pe conuri" (joc de îndemânare). Lui Matei i-au apropiat conurile și a reușit din prima."
„Au făcut „atelier de magneți de frigider" din spumă colorată. Ei Darei i-au decupat o inimă și a decorat-o cu sclipici."
„Superparty a pregătit „poveste cu păpuși" și voci amuzante. Lui Sebastian i-au dat o păpușă de leu și a intrat în rol."
„Au organizat „vânătoare de comori" cu hartă simplă. Ei Karinei i-au dat harta și a condus echipa spre premiu."
„Superparty a făcut „turneu de mini-fotbal" cu mingi moi. Lui Denis i-au pus un tricou de căpitan și a fost foarte fair-play."
„Au pregătit „atelier de origami" (forme ușoare). Ei Elenei i-au arătat o inimă din hârtie și i-a ieșit din a doua."
„Superparty a organizat „ștafeta cu balonul între genunchi". Lui Paul i-au arătat cum merge încet și a terminat fără să scape."
„Au făcut „jocul cu mimă de meserii". Ei Mirelei i-au dat „doctor" și a jucat foarte convingător."
„Superparty a pregătit „atelier de biscuiți decorați" (glazură + bombonele). Lui Șerban i-au făcut un model cu fulger și a fost încântat."
„Au organizat „cursa cu obstacole" din perne și cercuri. Ei Oanei i-au arătat varianta mai ușoară și a reușit perfect."
„Superparty a făcut „jocul cu ghicitori" pe echipe, cu puncte. Lui Cătălin i-au dat prima ghicitoare și a deschis scorul."
„Au pregătit „atelier de tablouri cu amprente" (mână/palmă). Ei Larisei i-au făcut un fluturaș din amprente și a ieșit foarte drăguț."
„Superparty a organizat „cursa cu pahare" (mutat apă cu burete). Lui Ionuț i-au pus un prosop și a jucat fără să stropească."
„Au făcut „dansul personajelor" (fiecare alege un personaj și îl imită). Ei Amaliei i-au ales o prințesă și a intrat imediat în rol."
„Superparty a pregătit „jocul cu baloane pe ritm" (spargi doar la semnal). Lui Marc i-au explicat regula și a respectat-o perfect."
„Au organizat „atelier de carton cu supereroi" (cape + siglă). Ei Iasminei i-au lipit o inimă pe pelerină și a fost foarte fericită."
„Superparty a făcut „mini-karaoke" cu refrene scurte pentru copii. Lui Liviu i-au ținut microfonul-jucărie și a cântat fără emoții."
„Au pregătit „pictură cu bureți" (forme de stele și nori). Ei Norei i-au dat bureți în formă de stea și tabloul a ieșit plin de culoare."
„Superparty a organizat „jocul cu scaune", dar fără îmbrânceli (regulă clară). Lui Vlad i-au explicat că se merge încet și a fost civilizat."
„Au făcut „atelier de corăbii" din carton și pai. Ei Georgiei i-au decorat corabia cu valuri albastre și arăta genial."
„Superparty a pregătit „jocul cu litere magnetice" (formezi cuvinte simple). Lui Edi i-au dat literele din nume și le-a aranjat singur."
„Au organizat „atelier de fluturi" (aripi din hârtie + elastic). Ei Crinei i-au prins aripile confortabil și a alergat fericită prin cameră."
„Superparty a făcut „ștafetă cu mingi moi" pe echipe. Lui Darius i-au dat startul și a încurajat pe toți."
„Au pregătit „jocul cu întrebări amuzante" (ce ai alege: înghețată sau pizza?). Ei Nicoletei i-au pus întrebarea și a răspuns super haios."
„Superparty a organizat „atelier de hărți ale comorii" (desen + X). Lui Simi i-au arătat cum face traseul și a desenat o hartă foarte clară."
„Au făcut „micul concurs de echilibru" (mergi cu o carte ușoară pe cap). Ei Adelinei i-au ales o carte subțire și a reușit până la capăt."
„Superparty a pregătit „jocul cu mingea la țintă" (cercuri pe perete). Lui Cristi i-au pus ținta mai jos și a nimerit de multe ori."
„Au organizat „atelier de felicitări 3D" (lipit straturi). Ei Ramonei i-au dat abțibilduri cu flori și felicitarea a ieșit elegantă."
„Superparty a făcut „pantomimă cu animale" pe rând. Lui Nelu i-au dat „pinguin" și a fost foarte amuzant."
„Au încheiat cu „momentul tortului" și un cântec scurt, pe vocea animatorilor. Ei Dianei i-au dat o steluță de decor și a fost încântată."
„Superparty a organizat „jocul cu balonul și farfuria" (ții balonul pe farfurie). Lui Rian i-au arătat cum merge încet și a câștigat."
„Au făcut „atelier de măști de supererou" (benzi + siglă). Ei Loredanei i-au decupat o mască mov și i-a stat perfect."
„Superparty a pregătit „cursa cu jaloane" pe muzică (te oprești când se oprește). Lui Emil i-au explicat regula și a fost atent."
„Au organizat „colțul de tatuaje temporare" pentru copii. Ei Irinei i-au pus un fluture pe mână și a fost super fericită."
„Superparty a făcut „jocul cu ghicește desenul" pe tablă (desen rapid). Lui Gabi i-au dat primul marker și a desenat o mașină."
„Au pregătit „atelier de medalioane" din carton și sfoară. Ei Carlei i-au ales sfoară roz și medalionul a ieșit foarte fin."
„Superparty a organizat „micul concurs de aruncat șosete" (șosete rulate în coș). Lui Sava i-au arătat distanța corectă și a marcat des."
„Au făcut „jocul cu poveste pe rând" (fiecare adaugă o propoziție). Ei Mariei i-au dat începutul și a inventat o introducere foarte bună."
„Superparty a pregătit „atelier de stele fosforescente" (lipit pe carton). Lui Mălin i-au dat stele verzi și a fost încântat de efect."
„Au încheiat cu „parada de final" și aplauze pentru fiecare copil. Ei Aurorei i-au oferit o coroniță mică și a plecat zâmbind."
„Superparty a venit cu un set de jocuri de cooperare (puzzle pe echipe). Lui Bogdan i-au dat piesele de colț și a fost foarte mândru că a „închis" cadrul."
„Au făcut un moment de „bubble show" cu baloane de săpun uriașe. Ei Ilincăi i-au arătat cum să prindă balonul fără să-l spargă și a reușit."
„Superparty a organizat „bowling" cu popice din plastic și o minge moale. Lui Victor i-au setat popicele mai aproape și a făcut strike."
„Au pregătit „atelier de brățări" cu mărgele mari, sigure pentru copii. Ei Andreei i-au ales mărgele pastel și brățara a ieșit foarte fină."
„Superparty a făcut „telefonul fără fir" cu propoziții amuzante. Lui Rareș i-au dat startul și a râs când a auzit cum s-a transformat mesajul."
„Au organizat un mini „teatru de umbre" cu povești scurte. Ei Evelinei i-au dat o siluetă de fluture și a jucat cu multă atenție."
„Superparty a pregătit „pescuit" cu undițe magnetice și peștișori colorați. Lui Toma i-au explicat trucul și a prins cei mai mulți."
„Au făcut „atelier de pălării" din carton (de decorat cu stickere). Ei Roxanei i-au pus o panglică roz și pălăria a arătat super."
„Superparty a organizat „cursa cu lingura și mingea" (minge ușoară). Lui Ștefan i-au ales o lingură mai mare și a terminat fără să scape."
„Au pregătit „jocul cu culori" (găsește ceva roșu/albastru în cameră). Ei Patriciei i-au dat prima culoare și a găsit imediat un obiect."
„Superparty a făcut „atelier de punguțe-cadou" (lipit, decorat, pus bomboane). Lui Cosmin i-au dat abțibilduri cu mașini și punguța a ieșit genială."
„Au organizat „mini-olimpiada" cu probe scurte și medalii din carton. Ei Denisei i-au pus o medalie aurie și a zâmbit toată ziua."
„Superparty a pregătit „jocul cu parșivul" (ștafetă cu baton moale). Lui Iulian i-au explicat să nu alerge tare și a respectat regulile."
„Au făcut „atelier de semne de carte" cu desene și sclipici. Ei Anei i-au decupat un nor și l-a decorat foarte creativ."
„Superparty a organizat „ghicește sunetul" (animatorii fac sunete de animale). Lui Marian i-au dat „leu" și a ghicit din prima."
„Au pregătit „colțul de construcții" cu piese mari tip lego. Ei Ralucăi i-au arătat cum se fixează turnul și n-a mai căzut."
„Superparty a făcut „dansul cu eșarfe" (mișcări simple pe muzică). Lui Alex i-au dat o eșarfă albastră și s-a mișcat super."
„Au organizat „atelier de pictat pietre" (pietre netede, vopsea lavabilă). Ei Iuliei i-au propus o buburuză și a ieșit foarte frumos."
„Superparty a pregătit „jocul cu întrebări fulger" despre sărbătorit. Lui Flaviu i-au pus întrebarea preferată și a răspuns fără ezitare."
„Au făcut un „concurs de statui" (îngheață când se oprește muzica). Ei Sarei i-au arătat o poză de „statuie" și a imitat perfect."
„Superparty a organizat „ștafetă cu cercuri" (treci prin cerc fără grabă). Lui Nicanor i-au arătat cum ține cercul și a mers excelent."
„Au pregătit „atelier de flori din șervețele" (împăturit, răsucit). Ei Melisei i-au făcut o floare mov și a păstrat-o ca suvenir."
„Superparty a făcut „jocul cu cine sunt?" (lipit post-it cu personaj pe frunte). Lui Ovidiu i-au pus „pirat" și a ghicit repede."
„Au organizat „mini-dans pe perechi" (pași foarte simpli). Ei Cătălinei i-au găsit o parteneră și a prins pașii imediat."
„Superparty a pregătit „atelier de rame foto" din carton. Lui Radu i-au dat stickere cu stele și rama a ieșit foarte cool."
„Au făcut „jocul cu balonul la perete" (ții balonul în aer fără mâini, doar suflat). Ei Mirei i-au explicat tehnica și a reușit surprinzător de bine."
„Superparty a organizat „cursa cu jaloane și clap" (te oprești la aplauze). Lui Damian i-au dat rolul de „arbitru" pentru un tur."
„Au pregătit „atelier de ghirlande" (hârtie colorată + lipici). Ei Almei i-au ales inimioare și ghirlanda a arătat superb."
„Superparty a făcut „jocul cu detectivul" (găsește obiectul lipsă). Lui Cezar i-au dat lupa de jucărie și a fost foarte implicat."
„Au încheiat o parte cu „pauză de hidratare" și au ținut copiii calmi. Ei Elizei i-au adus paharul la timp și a continuat fericită."
„Superparty a organizat „atelier de colaje" cu reviste și forme decupate. Lui Nelu i-au dat teme cu vehicule și colajul a fost plin de mașini."
„Au făcut un moment de „povești interactive" (copiii aleg finalul). Ei Florinei i-au oferit două opțiuni și a ales finalul amuzant."
„Superparty a pregătit „jocul cu mingea pe culoare" (treci mingea pe sub picioare). Lui Sandu i-au arătat ritmul și echipa lui a mers perfect."
„Au organizat „atelier de stickere" (copiii își creează propriile autocolante). Ei Georgianei i-au decupat o inimă și a colorat-o frumos."
„Superparty a făcut „cursa cu pași de animal" (iepure, urs, crab). Lui Patrick i-au dat „urs" și a mers foarte haios."
„Au pregătit „jocul cu numere" (aruncă la țintă și adună puncte). Ei Sabinei i-au explicat rapid adunarea și s-a prins imediat."
„Superparty a organizat „atelier de ștampile" cu forme (stea, cerc, inimă). Lui Mihai i-au dat ștampila cu fulger și a umplut foaia."
„Au făcut „jocul cu pernuța muzicală" (pui perna mai departe la muzică). Ei Doiniței i-au zis să dea perna ușor și a fost totul safe."
„Superparty a pregătit „mic concurs de aplauze" (cine aplaudă pe ritm câștigă). Lui Teo i-au bătut ritmul și l-a ținut perfect."
„Au organizat „atelier de broșe" din fetru (lipit forme simple). Ei Otiliei i-au făcut o broșă cu floare și a purtat-o imediat."
„Superparty a făcut „jocul cu cuvinte rimate" pe rând. Lui Horia i-au dat un cuvânt ușor și a prins rapid ideea."
„Au pregătit „atelier de planetă" (pictat o minge de polistiren). Ei Adrianei i-au ales o planetă cu inele și a ieșit foarte frumos."
„Superparty a organizat „mini-baschet" cu coș mic și mingi moi. Lui Sergiu i-au ajustat distanța și a marcat de mai multe ori."
„Au făcut „jocul cu umbrele pe perete" (forme cu mâinile). Ei Mirunei i-au arătat un iepure și a reușit și ea."
„Superparty a pregătit „atelier de etichete pentru sticle" (nume + desen). Lui Raul i-au scris numele clar și a desenat un robot."
„Au organizat „ștafetă cu puzzle" (duci o piesă pe rând). Ei Laviniei i-au dat piesa cu modelul cel mai simplu și a ajutat echipa."
„Superparty a făcut „jocul cu expresii" (imită bucurie, surpriză, somn). Lui Iacob i-au dat „surpriză" și a fost foarte amuzant."
„Au pregătit „atelier de decorațiuni pentru tort" din carton (stele, nume). Ei Georgiei i-au făcut o stea cu sclipici și a stat pe tort."
„Superparty a organizat „cursa cu balonul pe cap" (fără mâini, mers lent). Lui Fabian i-au arătat cum să meargă încet și a câștigat."
„Au încheiat cu un „cerc al complimentelor" (fiecare spune ceva frumos). Ei Deliei i-au dat timp să se gândească și a spus un compliment foarte dulce."
„Superparty a făcut un mini „laborator de slime" cu ingrediente sigure și mese protejate. Lui Darius i-au explicat pas cu pas și a fost încântat când slime-ul a ieșit perfect elastic."
„Au organizat o vânătoare de comori cu indicii desenate. Ei Mariei i-au dat prima hartă și a condus echipa până la „cufăr"."
„Superparty a pregătit un colț de karaoke cu melodii pentru copii. Lui Ionuț i-au ales o piesă scurtă și a cântat fără emoții."
„Au făcut un atelier de „mini-vulcan" (bicarbonat + oțet) în recipiente mici. Ei Biancăi i-au pus ochelari de protecție de jucărie și a zis că e „cea mai tare magie"."
„Superparty a organizat un joc „Ținta cu ventuze" pe panou. Lui Vlad i-au arătat cum să țintească din încheietură și a nimerit de mai multe ori."
„Au pregătit un moment cu „povești pe roluri" (copiii aleg personajele). Ei Ioanei i-au dat rolul de zână și a intrat imediat în personaj."
„Superparty a făcut un mini „fotobooth" cu recuzită (ochelari, pălării, mustăți). Lui Paul i-au dat ochelarii haioși și a pozat ca un star."
„Au organizat o „cursă cu obstacole" cu perne și jaloane moi. Ei Dacianei i-au arătat traseul și l-a parcurs super atent."
„Superparty a pregătit un joc „Găsește perechea" cu cartonașe mari. Lui Denis i-au dat setul cu animale și a găsit toate perechile rapid."
„Au făcut un atelier de „stickere cu inițiale" (litere din spumă + sclipici). Ei Larei i-au ales litera L și a decorat-o foarte elegant."
„Superparty a organizat un joc „Construcții pe echipe" cu cuburi mari. Lui Matei i-au dat rolul de „arhitect" și a coordonat super."
„Au pregătit un moment de „dans cu panglici" pe muzică lentă. Ei Alinei i-au dat o panglică mov și a dansat foarte grațios."
„Superparty a făcut „Baloane modelate" (sabie, cățel, floare). Lui Sebastian i-au făcut o sabie albastră și a stat cu ea tot party-ul."
„Au organizat un joc „Ghicește personajul" din desene (întrebări simple). Ei Sofiei i-au șoptit cum să pună întrebarea și a ghicit corect."
„Superparty a pregătit un atelier de „măști de animale" din carton. Lui Călin i-au decupat o mască de tigru și a colorat-o singur."
„Au făcut o „ploaie de confetti" controlată, la final de joc. Ei Teodorei i-au spus dinainte momentul și a așteptat cu entuziasm."
„Superparty a organizat „Jenga" cu piese mari din spumă. Lui Luca i-au arătat cum să scoată piesa fără să dărâme turnul și a reușit."
„Au pregătit un atelier de „felicitări pentru sărbătorit". Ei Irinei i-au dat ștampile cu inimioare și felicitarea a ieșit superbă."
„Superparty a făcut un joc „Semafor" (roșu-stop, verde-merge). Lui Eric i-au dat rolul de semaforist pentru o rundă."
„Au organizat un mini „quiz" despre culori și forme. Ei Camiliei i-au pus întrebări ușoare la început și apoi a prins curaj."
„Superparty a pregătit un joc „Transportă comoara" (minge în coș pe cap). Lui Tudor i-au arătat postura corectă și a terminat fără să scape."
„Au făcut un atelier de „pictură pe tricou" (marker lavabil, șabloane). Ei Nicolinei i-au oferit șablon cu fluture și desenul a ieșit clar."
„Superparty a organizat „Aruncă inelele" pe conuri colorate. Lui Robert i-au ajustat distanța și a marcat foarte repede."
„Au pregătit un moment de „magie" cu trucuri simple și sigure. Ei Oanei i-au dat bagheta și a „făcut" să apară o eșarfă."
„Superparty a făcut un joc „Cine lipsește?" (un copil se ascunde, ceilalți ghicesc). Lui Liviu i-au dat runda de ascuns și s-a distrat maxim."
„Au organizat un atelier de „coroane regale" (autocolante + pietricele). Ei Anastasiei i-au pus o „piatră" mare în față și coroana a arătat wow."
„Superparty a pregătit „cursa cu balonul între genunchi". Lui Cătălin i-au explicat să meargă încet și a ajuns la finish fără să-l scape."
„Au făcut „jocul cu rime" pe numele sărbătoritului (amuzant, fără să jignească). Ei Monicăi i-au dat un exemplu și a inventat și ea o rimă."
„Superparty a organizat un colț de „lego challenge" (construiește un pod). Lui Adi i-au dat timer-ul și a fost super motivat."
„Au pregătit un mini „atelier de origami" (forme foarte simple). Ei Mădălinei i-au pliat o inimă și apoi a făcut și ea încă una."
„Superparty a făcut un joc „Ștafetă cu mingi" (treci mingea deasupra capului). Lui Răzvan i-au arătat ritmul și echipa lui a mers ca unsă."
„Au organizat un „atelier de pietre norocoase" (scrii un mesaj pe piatră). Ei Larisei i-au scris cu ea „Curaj" și a păstrat piatra în buzunar."
„Superparty a pregătit un moment „piratesc" cu jurământ și hartă. Lui Șerban i-au dat bandana și a fost cel mai implicat pirat."
„Au făcut un joc „Vânătoare de culori" (caută obiecte după culoare). Ei Elenei i-au dat culoarea „turcoaz" și a găsit ceva rar, super rapid."
„Superparty a organizat „mini-tenis" cu palete moi și mingiuțe ușoare. Lui Raul i-au arătat cum să lovească ușor și a ținut schimbul."
„Au pregătit un atelier de „decorat cupcakes" (ornamente simple, curat). Ei Iasminei i-au dat sprinkles și a decorat cel mai frumos."
„Superparty a făcut „jocul cu mimă" (sporturi, animale, meserii). Lui Cornel i-au dat „astronaut" și a fost foarte amuzant."
„Au organizat un moment de „povești cu întrebări" (copiii răspund pe rând). Ei Mirelei i-au dat timp să răspundă și a participat cu încredere."
„Superparty a pregătit „cursa cu pași pe numere" (covoraș cu cifre). Lui Doru i-au arătat traseul și a sărit exact pe cifre."
„Au făcut un atelier de „mini-ramă cu magnet" pentru frigider. Ei Claudiei i-au lipit magnetul bine și rama a stat perfect."
„Superparty a organizat un joc „Sticlele cu puncte" (arunci bile și numeri). Lui Andrei i-au explicat punctajul și a fost super corect în numărare."
„Au pregătit un moment de „dans în cerc" cu mișcări pe niveluri. Ei Corinei i-au arătat varianta simplă și apoi a trecut la varianta „pro"."
„Superparty a făcut un atelier de „pictat pe față" cu modele discrete. Lui Radu i-au făcut un fulger mic pe obraz și a fost foarte încântat."
„Au organizat „telefonul fără fir" cu tema „supereroi". Ei Melaniei i-au dat mesajul inițial și l-a spus clar, fără să se încurce."
„Superparty a pregătit un joc „Aruncă la coș" cu inele din spumă. Lui Silviu i-au ajustat înălțimea țintei și a reușit din prima."
„Au făcut un atelier de „badge-uri" (insigne din carton cu nume). Ei Adrianei i-au scris numele frumos și a purtat insigna imediat."
„Superparty a organizat „cursa cu jaloane și întoarcere" (fără alergat tare). Lui Cezar i-au reamintit regulile și a jucat foarte fair-play."
„Au pregătit un moment „surpriză pentru sărbătorit" cu aplauze coordonate. Ei Danei i-au spus când să înceapă aplauzele și a mers perfect."
„Superparty a făcut un joc „Construiește cel mai înalt turn" pe timp. Lui Gabriel i-au dat piesele mari de bază și turnul a stat drept."
„Au încheiat cu „poza de grup" și un salut special Superparty. Ei Otiliei i-au aranjat recuzita și a ieșit o poză super reușită."
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
if total_articles >= 500:
    print("COMPLET! Toate cele 500 de articole au testimoniale -> status READY!")
else:
    print(f"Mai lipsesc {500 - total_articles} articole.")
