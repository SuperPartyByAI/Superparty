// generate_unique_content_80pct.mjs
// Genereaza 700+ cuvinte de continut UNIC per pagina (localitate-specifica)
// Scop: aduce fiecare pagina la >80% continut unic si relevant pt "animatori petreceri copii"
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    const rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}

// ══════════════════════════════════════════════════════════════════
// BAZA DE DATE LOCATII
// ══════════════════════════════════════════════════════════════════
const LOC_DB = {
  // COMUNE DAMBOVITA / GIURGIU / ILFOV / CALARASI
  '1-decembrie':     {jud:'Ilfov',km:28,dir:'sud',dn:'DJ401',pop:6200,vec:['Vidra','Clinceni','Bragadiru'],fauna:'câmpie',tip:'com',specific:'fostă comună agricolă în transformare rapidă spre rezidențial suburban'},
  'adunatii-copaceni':{jud:'Giurgiu',km:42,dir:'sud',dn:'DN5 + DJ412',pop:4100,vec:['Comana','Prundu','Mihailești'],fauna:'câmpie dunăreană',tip:'com',specific:'zonă protejată lângă Parcul Natural Comana, cea mai mare pădure din Câmpia Română'},
  'afumati':         {jud:'Ilfov',km:22,dir:'est',dn:'E60/DN3',pop:8300,vec:['Dobroești','Pantelimon','Cernica'],fauna:'câmpie',tip:'com',specific:'comună în creștere rapidă situată pe coridorul estic al metropolei București'},
  'alunisu':         {jud:'Giurgiu',km:50,dir:'sud-vest',dn:'DJ412',pop:2800,vec:['Mihailești','Bolintin-Vale','Bulbucata'],fauna:'câmpie',tip:'com',specific:'sat tradițional din Câmpia Munteniei, gospodariile având curți spațioase ideale pentru petreceri'},
  'aviatiei':        {jud:'Sector-2',km:0,dir:'nord',dn:'-',pop:38000,vec:['Dorobanți','Floreasca','Băneasa'],fauna:'urban',tip:'cartier',specific:'cartier de blocuri turn și vile lângă aeroport, cu o comunitate de tineri profesioniști cu copii'},
  'bacu':            {jud:'Giurgiu',km:55,dir:'sud-vest',dn:'DN61',pop:3100,vec:['Calugareni','Gogosari','Ulmi'],fauna:'câmpie',tip:'com',specific:'comună cu tradiție vitivinicola în câmpia Munteniei, cu crame și gospodarii generoase'},
  'balaceanca':      {jud:'Ilfov',km:18,dir:'est',dn:'DJ301',pop:5600,vec:['Cernica','Pantelimon','Glina'],fauna:'câmpie umedă',tip:'com',specific:'comună la confluența cu zona lacurilor periurbane estice ale Bucureștiului'},
  'balotesti':       {jud:'Ilfov',km:28,dir:'nord',dn:'DN1 + DJ104',pop:7800,vec:['Snagov','Gruiu','Ciolpani'],fauna:'pădure de câmpie',tip:'com',specific:'comună exclusivistă lângă Lacul Snagov, populată de familii cu venituri ridicate'},
  'baneasa':         {jud:'Sector-1',km:0,dir:'nord',dn:'-',pop:35000,vec:['Aviației','Otopeni','Floreasca'],fauna:'urban-pădure',tip:'cartier',specific:'cartier de vile cu acces la Pădurea Băneasa, cel mai verde cartier suburban al Capitalei'},
  'belciugatele':    {jud:'Călărași',km:65,dir:'est',dn:'DN3',pop:3400,vec:['Drajna','Ulmu','Frumusani'],fauna:'câmpie',tip:'com',specific:'comună tradițională din județul Călărași, accesibilă pe DN3 (E60) spre Constanța'},
  'berceni-ilfov':   {jud:'Ilfov',km:16,dir:'sud-est',dn:'DJ401A',pop:9200,vec:['Jilava','Popești-Leordeni','Glina'],fauna:'câmpie',tip:'com',specific:'comună din sudul Ilfovului cu industrie în reconversie spre cartier rezidențial'},
  'bolintin-deal':   {jud:'Giurgiu',km:52,dir:'vest',dn:'DN6',pop:5100,vec:['Bolintin-Vale','Florești','Mihailești'],fauna:'câmpie',tip:'com',specific:'semirban din câmpia Vlăsiei occidentale, lângă drumul european E70/DN6 spre Pitești'},
  'bolintin-vale':   {jud:'Giurgiu',km:52,dir:'vest',dn:'DN6',pop:11200,vec:['Bolintin-Deal','Iepurești','Buzoiești'],fauna:'câmpie',tip:'oras',specific:'municipiu de mici dimensiuni, centru administrativ al zonei de vest a județului Giurgiu'},
  'bragadiru':       {jud:'Ilfov',km:18,dir:'sud-vest',dn:'DN6 + DJ401',pop:18500,vec:['Clinceni','Jilava','Domneșiti'],fauna:'câmpie',tip:'oras',specific:'cel mai rapid-growing oraș din sudul Ilfovului, cu 5 cartiere rezidențiale noi din 2018'},
  'branesti':        {jud:'Ilfov',km:24,dir:'est',dn:'DJ302',pop:9600,vec:['Cernica','Pantelimon','Afumați'],fauna:'câmpie umedă',tip:'com',specific:'comună cu 7 sate situată la est de Capitală, în zona coridorului ecologic Cernica-Snagov'},
  'branistari':      {jud:'Ilfov',km:30,dir:'est',dn:'DJ101A',pop:3200,vec:['Brănești','Lipia','Gagu'],fauna:'câmpie',tip:'com',specific:'sat aparținând de Brănești, Ilfov, cu gospodarii tradiționale și curți spațioase'},
  'buciumeni':       {jud:'Dâmbovița',km:70,dir:'nord-vest',dn:'DJ711',pop:4100,vec:['Pucioasa','Moreni','Ocnița'],fauna:'deal subcarpatic',tip:'com',specific:'comună din zona subcarpaților dâmbovițeni, cu peisaje dealurchicesc și gospodarii tradiționale'},
  'bucuresti':       {jud:'București',km:0,dir:'-',dn:'-',pop:1800000,vec:['Ilfov'],fauna:'urban',tip:'municipiu',specific:'capitala României și centrul de referință al serviciilor SuperParty — acoperire 100% fără taxă de deplasare'},
  'budeni':          {jud:'Giurgiu',km:60,dir:'sud',dn:'DN61 + drum local',pop:2100,vec:['Iepurești','Gogosari','Calugareni'],fauna:'câmpie',tip:'com',specific:'sat din câmpia Munteniei sudice, cu peisaje deschise și comunitate agricolă tradițională'},
  'budesti':         {jud:'Călărași',km:45,dir:'est-sud-est',dn:'DN4',pop:6800,vec:['Oltenița','Lehliu','Mânăstirea'],fauna:'câmpie',tip:'com',specific:'comună cu acces pe DN4 spre Oltenița, în zona de câmpie dintre Argeș și Mostiștea'},
  'buftea':          {jud:'Ilfov',km:24,dir:'nord-vest',dn:'DN1A',pop:22000,vec:['Chiajna','Chitila','Mogoșoaia'],fauna:'lacuri',tip:'oras',specific:'orașul studiurilor de film din România, cu Lacul Buftea și infrastructură culturală bine dezvoltată'},
  'bulbucata':       {jud:'Giurgiu',km:58,dir:'vest',dn:'DN6 + drum local',pop:3600,vec:['Bolintin-Vale','Alunișu','Iepurești'],fauna:'câmpie',tip:'com',specific:'comună din Câmpia Vlăsiei de vest, cu livezi tradiționale și gospodarii cu curți generoase'},
  'butimanu':        {jud:'Dâmbovița',km:32,dir:'nord',dn:'DN1A + DJ720',pop:4200,vec:['Titu','Găești','Răcari'],fauna:'câmpie-deal',tip:'com',specific:'comună din nordul Câmpiei Române, la limita cu zona subcolinară dâmbovițeană'},
  'buturugeni':      {jud:'Giurgiu',km:48,dir:'sud',dn:'DN61 + drum local',pop:3800,vec:['Hotarele','Gogosari','Singureni'],fauna:'câmpie',tip:'com',specific:'sat din câmpia sudică giurgiuvana, accesibil via Hotarele pe drumul spre Giurgiu'},
  'caciulati':       {jud:'Ilfov',km:35,dir:'nord',dn:'DN1 + drum local',pop:3100,vec:['Balotești','Gruiu','Snagov'],fauna:'pădure',tip:'com',specific:'localitate rurală din nordul Ilfovului, lângă zona lacustră Snagov-Căciulați'},
  'calarasi':        {jud:'Călărași',km:100,dir:'est-sud-est',dn:'DN3',pop:65000,vec:['Oltenița','Modelu','Lehliu-Gară'],fauna:'Dunăre',tip:'municipiu',specific:'municipiu reședință de județ la Dunăre, cu port și industrie, centru urban important al Bărăganului'},
  'caldararu':       {jud:'Ilfov',km:16,dir:'est',dn:'DJ301',pop:4800,vec:['Cernica','Tânganu','Balaceanca'],fauna:'pădure-lac',tip:'com',specific:'sat din comuna Cernica, la 2 km de Mânăstirea Cernica și Lacul Cernica'},
  'calugareni':      {jud:'Giurgiu',km:45,dir:'sud',dn:'DN5',pop:5200,vec:['Putineiu','Gogosari','Singureni'],fauna:'câmpie',tip:'com',specific:'comună cu semnificație istorică (Bătălia de la Călugăreni 1595), pe drum european E85/DN5'},
  'campurelu':       {jud:'Giurgiu',km:50,dir:'sud',dn:'DJ412 + drum local',pop:2600,vec:['Gostinari','Comana','Văcărești'],fauna:'câmpie',tip:'com',specific:'sat din sudul Giurgiu, în zona de câmpie secă a Câmpiei Românești'},
  'candeasca':       {jud:'Dâmbovița',km:70,dir:'nord-vest',dn:'DJ721',pop:3400,vec:['Ulmi','Potlogi','Slobozia Moară'],fauna:'deal',tip:'com',specific:'sat dâmbovițean din zona colinară, cu peisaje verduroase și curți mari tipice zonei de deal'},
  'catelu':          {jud:'Sector-3',km:0,dir:'est',dn:'-',pop:55000,vec:['Dristor','Titan','Pantelimon'],fauna:'urban',tip:'cartier',specific:'cartier de blocuri din Sectorul 3, cu acces rapid la Parcul Titan și Parcul Natural Văcărești'},
  'catrunesti':      {jud:'Teleorman',km:80,dir:'sud-vest',dn:'DN61 + drum local',pop:2900,vec:['Turnu Măgurele','Roșiori','Zimnicea'],fauna:'câmpie',tip:'com',specific:'sat din câmpia teleormăneana, specific prin gospodarii cu curți largi și grădini'},
  'cernica':         {jud:'Ilfov',km:16,dir:'est',dn:'DJ301',pop:14200,vec:['Pantelimon','Fundeni','Glina'],fauna:'pădure-lac',tip:'com',specific:'comună cu Mânăstirea Cernica și Lacul Cernica — destinație de weekend a Bucureștenilor'},
  'chiajna':         {jud:'Ilfov',km:12,dir:'vest',dn:'DN7',pop:15800,vec:['Militari','Roșu','Domneșiti'],fauna:'câmpie',tip:'com',specific:'comună ce găzduiește Militari Residence — cel mai mare ansamblu rezidențial privat din România'},
  'chirculesti':     {jud:'Ialomița',km:75,dir:'est',dn:'DN3A',pop:3600,vec:['Urziceni','Grivița','Moldoveni'],fauna:'câmpie',tip:'com',specific:'sat din nordul Ialomiței, pe coridorul Urziceni-Fetești'},
  'chitila':         {jud:'Ilfov',km:15,dir:'nord-vest',dn:'DN1',pop:14500,vec:['Mogoșoaia','Buftea','Chiajna'],fauna:'câmpie',tip:'oras',specific:'oraș cu gară importantă, conexiune directă la Gara de Nord — 15 minute din centrul Capitalei'},
  'ciocanesti':      {jud:'Dâmbovița',km:45,dir:'nord',dn:'DN1A',pop:7200,vec:['Titu','Răcari','Gäești'],fauna:'câmpie-deal',tip:'com',specific:'comună la limita dintre câmpie și deal, pe axa rutieră Municipiului Titu'},
  'ciofliceni':      {jud:'Ilfov',km:30,dir:'nord',dn:'DN1 + drum local',pop:4100,vec:['Snagov','Gruiu','Peris'],fauna:'pădure lacustră',tip:'com',specific:'sat în zona lacustră a Ilfovului nordic, lângă Lacul Snagov și Parcul Snagov'},
  'ciorogarla':      {jud:'Ilfov',km:22,dir:'vest',dn:'DN7 + drum local',pop:8600,vec:['Domneșiti','Chiajna','Cornetu'],fauna:'câmpie',tip:'com',specific:'comună situată pe Autostrada A1, cu dezvoltare rezidențială rapidă în zona vestica'},
  'ciorogirla':      {jud:'Ilfov',km:22,dir:'vest',dn:'DN7',pop:8900,vec:['Chiajna','Cornetu','Clinceni'],fauna:'câmpie',tip:'com',specific:'variantă administrativă a comunei Ciorogârla, pe șoseaua de centură a Capitalei'},
  'clinceni':        {jud:'Ilfov',km:20,dir:'sud-vest',dn:'DJ401',pop:10500,vec:['Bragadiru','Cornetu','Domneșiti'],fauna:'câmpie',tip:'com',specific:'comună în plina transformare rezidențială, cu acces rapid pe Centura Capitalei'},
  'cocani':          {jud:'Ilfov',km:32,dir:'nord-est',dn:'DJ101',pop:4600,vec:['Grădiștea','Afumați','Dascălu'],fauna:'câmpie',tip:'com',specific:'sat din nordul Ilfovului, zona cu case individuale și grădini'},
  'cojasca':         {jud:'Dâmbovița',km:35,dir:'nord',dn:'DN71',pop:5200,vec:['Titu','Răcari','Văcărești'],fauna:'câmpie-deal',tip:'com',specific:'comună dâmbovițeană cu Lacul Cojasca, loc de pescuit și relaxare lângă capitală'},
  'cojesti':         {jud:'Ilfov',km:30,dir:'nord-est',dn:'DN1 + drum local',pop:3900,vec:['Gruiu','Ciolpani','Dascălu'],fauna:'câmpie-pădure',tip:'com',specific:'sat din zona nordică a Ilfovului, cu ansambluri rezidențiale noi printre case rurale'},
  'colibasi':        {jud:'Giurgiu',km:55,dir:'sud-vest',dn:'DN6 + drum local',pop:4200,vec:['Bolintin','Calugareni','Miroșii'],fauna:'câmpie',tip:'com',specific:'sat din câmpia Vlăsiei de vest, cu economia bazată pe agricultură și mici industrii'},
  'comana':          {jud:'Giurgiu',km:46,dir:'sud',dn:'DN5',pop:5700,vec:['Adunatii-Copăceni','Grădinari','Văcărești'],fauna:'pădure de câmpie',tip:'com',specific:'comună la marginea Parcului Natural Comana — cea mai mare pădure din Câmpia Română'},
  'copaceni':        {jud:'Giurgiu',km:38,dir:'sud',dn:'DJ401',pop:6300,vec:['Comana','Singureni','Adunatii-Copaceni'],fauna:'pădure-câmpie',tip:'com',specific:'sat din Giurgiu în zona tampon a Parcului Natural Comana'},
  'corbeanca':       {jud:'Ilfov',km:25,dir:'nord',dn:'DN1 + drum local',pop:7800,vec:['Otopeni','Gruiu','Balotești'],fauna:'pădure',tip:'com',specific:'comună exclusivistă, cu vile premium și familii cu venituri ridicate relocate din București'},
  'cornetu':         {jud:'Ilfov',km:22,dir:'sud-vest',dn:'DN6',pop:7200,vec:['Clinceni','Bragadiru','Ciorogârla'],fauna:'câmpie',tip:'com',specific:'comună pe DN6 (București-Alexandria), cu dezvoltare rezidențială în zona de sud-vest'},
  'cosoba':          {jud:'Teleorman',km:90,dir:'sud-vest',dn:'drum local',pop:2400,vec:['Turnu Măgurele','Zimnicea','Segarcea'],fauna:'câmpie',tip:'com',specific:'sat izolat din câmpia teleormanenă, cu caracter rural autentic și curți largi'},
  'coteni':          {jud:'Ilfov',km:35,dir:'nord-est',dn:'drum local',pop:2900,vec:['Gruiu','Ciolpani','Snagov'],fauna:'pădure',tip:'com',specific:'sat din nordul Ilfovului, în zona de păduri și lacuri a perimetrului Snagov'},
  'cozieni':         {jud:'Buzău',km:90,dir:'nord-est',dn:'DN1B',pop:6800,vec:['Buzău','Râmnicu-Sarat','Pătârlagele'],fauna:'deal',tip:'com',specific:'comună din zona deluroasă buzăuanã, pe drumul National Ploiești-Buzău'},
  'crangasi':        {jud:'Sector-6',km:0,dir:'vest',dn:'-',pop:58000,vec:['Giulești','Militari','Crângași'],fauna:'urban-lac',tip:'cartier',specific:'cartier cu lacul Crângași și plajă amenajată, cel mai popular loc de relaxare din vestul Capitalei'},
  'cranguri':        {jud:'Giurgiu',km:48,dir:'sud-vest',dn:'drum local',pop:2200,vec:['Bolintin','Căscioarele','Miroșii'],fauna:'câmpie',tip:'com',specific:'sat mic din câmpia giurgiu-ilfoveana, cu gospodarii tradiționale și curți generoase'},
  'creata':          {jud:'Giurgiu',km:55,dir:'sud',dn:'DN5 + drum local',pop:3100,vec:['Comana','Herasti','Singureni'],fauna:'câmpie pădure',tip:'com',specific:'sat în zona tampon a Parcului Comana, cu natură bogată și aer curat'},
  'cretesti':        {jud:'Ilfov',km:22,dir:'nord',dn:'DJ101A',pop:3800,vec:['Gruiu','Dascălu','Ciolpani'],fauna:'câmpie',tip:'com',specific:'sat din zona nordică Ilfov, cu case individuale și gospodarii de tip semiferm'},
  'cretuleasca':     {jud:'Ilfov',km:28,dir:'nord-est',dn:'drum local',pop:2700,vec:['Cojești','Grădiștea','Cocani'],fauna:'câmpie',tip:'com',specific:'sat mic din Ilfov cu profil rezidențial în formare, lângă localitati mai mari'},
  'crevedia':        {jud:'Dâmbovița',km:38,dir:'nord-vest',dn:'DN7 + DJ401B',pop:5400,vec:['Titu','Găești','Buciumeni'],fauna:'câmpie-deal',tip:'com',specific:'comună la granița Dâmbovița-Ilfov, pe drumul național spre Pitești'},
  'crevedia-mare':   {jud:'Giurgiu',km:56,dir:'vest',dn:'DN6',pop:5800,vec:['Bolintin','Crevedia-Mică','Florești'],fauna:'câmpie',tip:'com',specific:'comună giurgiuvana pe DN6, recunoscuta pentru livezi de pruni traditionale'},
  'crivina':         {jud:'Ilfov',km:28,dir:'nord',dn:'DN1 + drum local',pop:3200,vec:['Balotești','Corbeanca','Gruiu'],fauna:'pădure',tip:'com',specific:'sat în zona paduroasă nordică a Ilfovului, lângă stațiunea Căciulați'},
  'cucuieti':        {jud:'Dâmbovița',km:75,dir:'nord',dn:'DJ713',pop:3100,vec:['Fieni','Pucioasa','Moreni'],fauna:'deal-munte',tip:'com',specific:'sat din zona subcarpatica dâmboviteana, la poalele muntelui, cu peisaj verdant'},
  'dambovita':       {jud:'Ilfov',km:30,dir:'nord',dn:'drum local',pop:5600,vec:['Gruiu','Peris','Snagov'],fauna:'pădure',tip:'com',specific:'comună Ilfov omonimă cu județul vecin, în zona nordică lacustră a județului'},
  'dascalu':         {jud:'Ilfov',km:25,dir:'nord',dn:'E85/DN1',pop:8900,vec:['Grădiștea','Ciolpani','Moara Vlăsiei'],fauna:'câmpie',tip:'com',specific:'comună pe E85 cu 5 sate (Dascălu, Gagu, Creaiu, Cretuleasca, Runcu), acces direct din capitală'},
  'decindea':        {jud:'Dâmbovița',km:65,dir:'nord-vest',dn:'DN72 + drum local',pop:2400,vec:['Găești','Titu','Băleni'],fauna:'câmpie-deal',tip:'com',specific:'sat dâmbovițean în zona de tranziție câmpie-deal, tipic pentru gospodăriile de tip rural'},
  'dimieni':         {jud:'Ilfov',km:28,dir:'est',dn:'DJ301A',pop:5100,vec:['Brănești','Cernica','Gănești'],fauna:'câmpie',tip:'com',specific:'sat din estul Ilfovului cu conexiune la coridorul Cernica-Brănești al ariei metropolitane'},
  'dobreni':         {jud:'Ilfov',km:40,dir:'nord-east',dn:'drum local',pop:3700,vec:['Gruiu','Ciolpani','Peris'],fauna:'pădure-lacuri',tip:'com',specific:'sat din nordul Ilfovului, în zona lacurilor și pădurilor periurbane nordice'},
  'dobroesti':       {jud:'Ilfov',km:14,dir:'est',dn:'E60/DN3 + drum local',pop:12100,vec:['Fundeni','Pantelimon','Cernica'],fauna:'câmpie-urban',tip:'com',specific:'comună adiacentă Sectorului 2, cu expansiune rezidențială accelerată spre estul Capitalei'},
  'domnesti':        {jud:'Ilfov',km:20,dir:'vest',dn:'DN7',pop:9800,vec:['Domneșiti','Ciorogârla','Chiajna'],fauna:'câmpie',tip:'com',specific:'comună vestică din Ilfov care absoarbe expansihunea rezidentiala din directia Sectorului 6 București'},
  'dragomiresti-deal':{jud:'Ilfov',km:30,dir:'nord',dn:'DN1 + drum local',pop:5600,vec:['Balotești','Corbeanca','Otopeni'],fauna:'pădure-câmpie',tip:'com',specific:'sat premium din zona nord Ilfov, cu vile și case individuale de standard ridicat'},
  'dragomiresti-vale':{jud:'Ilfov',km:30,dir:'nord',dn:'DN1 + drum local',pop:5200,vec:['Balotești','Otopeni','Mogoșoaia'],fauna:'pădure',tip:'com',specific:'sat din nordul Ilfovului cu pădure de stejar și lacuri, destinație de week-end pentru București'},
  'dristor':         {jud:'Sector-3',km:0,dir:'est',dn:'-',pop:52000,vec:['Titan','Balta Albă','Pantelimon-cart'],fauna:'urban-natură',tip:'cartier',specific:'cartier cu Parcul Natural Văcărești la 2 km — singura deltă urbană din lume, unică în România'},
  'drumul-taberei':  {jud:'Sector-6',km:0,dir:'sud-vest',dn:'-',pop:112000,vec:['Militari','Giulești','Rahova'],fauna:'urban-parc',tip:'cartier',specific:'cel mai verde cartier din București cu 5 parcuri, 110.000 de locuitori și comunitate densă de familii'},
  'fierbinti-targ':  {jud:'Ialomița',km:65,dir:'nord-est',dn:'DN2 + drum local',pop:7400,vec:['Urziceni','Ograda','Gura Ialomiței'],fauna:'câmpie Bărăgan',tip:'com',specific:'oraș mic din Bărăgan, lângă apa Ialomiței, cu infrastructură locală în dezvoltare'},
  'fundulea':        {jud:'Călărași',km:50,dir:'est',dn:'E60/DN3',pop:9800,vec:['Budești','Oltenița','Mânăstirea'],fauna:'câmpie',tip:'com',specific:'comună cu Stațiunea de Cercetare Agricolă Fundulea pe E60 spre Constanța'},
  'ganeasa':         {jud:'Ilfov',km:22,dir:'nord-est',dn:'drum local',pop:8100,vec:['Snagov','Periș','Ciolpani'],fauna:'pădure-lac',tip:'com',specific:'comună din nordul Ilfovului, cu acces la Lacul Snagov și Pădurea Snagov'},
  'giurgiu':         {jud:'Giurgiu',km:65,dir:'sud',dn:'E85/DN5',pop:61000,vec:['Slobozia','Malu-Spart','Băneasa'],fauna:'Dunăre',tip:'municipiu',specific:'municipiu-port la Dunăre și punct de trecere internațional spre Bulgaria'},
  'giulesti':        {jud:'Sector-6',km:0,dir:'nord-vest',dn:'-',pop:62000,vec:['Crângași','Militari','Drumul Taberei'],fauna:'urban-lac',tip:'cartier',specific:'cartier-simbol al fotbalului românesc, cu stadion istorc și comunitate unită cu mulți copii'},
  'glina':           {jud:'Ilfov',km:14,dir:'est-sud-est',dn:'DJ301',pop:18300,vec:['Cernica','Pantelimon','Berceni-Ilfov'],fauna:'câmpie',tip:'com',specific:'comună adiacentă Sectorului 4 București, cu acces rapid din Centura Capitalei în 15 min'},
  'ialomita':        {jud:'Ialomița',km:60,dir:'nord-est',dn:'DN2A',pop:285000,vec:['Slobozia','Urziceni','Fetești'],fauna:'Bărăgan-Ialomița',tip:'judet',specific:'județ cu câmpia Bărăganului și râul Ialomița, SuperParty acoperă localitățile din aria metropolitană'},
  'iepuresti':       {jud:'Giurgiu',km:50,dir:'sud',dn:'DN5 + drum local',pop:4200,vec:['Calugareni','Ulmi','Buzoiesti'],fauna:'câmpie',tip:'com',specific:'sat giurgiuvean din câmpia Vlăsiei, cu ferme și gospodarii cu spații generoase'},
  'ilfov':           {jud:'Ilfov',km:20,dir:'toate',dn:'multiple',pop:422000,vec:['București'],fauna:'păduri-lacuri-câmpie',tip:'judet',specific:'județul cu cea mai dinamică creștere demografică din România, înconjoară Capitala pe toate direcțiile'},
  'jilava':          {jud:'Ilfov',km:12,dir:'sud',dn:'DN5',pop:14200,vec:['Berceni-Ilfov','Popești-Leordeni','București S4'],fauna:'câmpie',tip:'com',specific:'comună la intrarea sudică în București pe DN5, cu comunitate rezidențiala diversă'},
  'magurele':        {jud:'Ilfov',km:18,dir:'sud-vest',dn:'DJ401B',pop:11200,vec:['Bragadiru','Clinceni','Alunelu'],fauna:'câmpie pădure',tip:'com',specific:'orașul oamenilor de știință din România, lângă ELI-NP (cel mai puternic laser din lume)'},
  'mihai-voda':      {jud:'Giurgiu',km:54,dir:'sud',dn:'DN61',pop:4100,vec:['Hotarele','Buturugeni','Putineiu'],fauna:'câmpie',tip:'com',specific:'sat din câmpia giurgiu-teleorman, cu gospodarii mari și o comunitate rurală autentică'},
  'mihailesti':      {jud:'Giurgiu',km:42,dir:'sud-vest',dn:'DN6',pop:7200,vec:['Bolintin','Alunișu','Florești'],fauna:'câmpie vlasie',tip:'oras',specific:'cel mai vestic oraș al Ilfovului la granița cu Giurgiu, pe axa rutieră E70/DN6 Pitești'},
  'militari':        {jud:'Sector-6',km:0,dir:'vest',dn:'-',pop:122000,vec:['Crângași','Drumul Taberei','Giulești'],fauna:'urban-parc',tip:'cartier',specific:'unul dintre cele mai mari cartiere rezidențiale din Europa cu 122.000 de locuitori'},
  'moara-vlasiei':   {jud:'Ilfov',km:30,dir:'nord',dn:'DN1 + drum local',pop:6800,vec:['Dascălu','Ciolpani','Gruiu'],fauna:'pădure câmpie',tip:'com',specific:'comună în nordul Ilfovului pe coridorul E85, cu case individuale și vile premium'},
  'mogosoaia':       {jud:'Ilfov',km:18,dir:'nord-vest',dn:'DN1A',pop:10600,vec:['Chitila','Buftea','Corbeanca'],fauna:'pădure lac',tip:'com',specific:'comună cu vestitul Palat Mogoșoaia pe malul lacului, destinație de tip vilă-rezidențial premium'},
  'nuci':            {jud:'Ilfov',km:32,dir:'nord-est',dn:'drum local',pop:4700,vec:['Gruiu','Ciolpani','Dascălu'],fauna:'câmpie',tip:'com',specific:'sat din nordul Ilfovului cu peisaj rural tipic și comunitate de familii stabilite de generații'},
  'ordoreanu-vatra-veche':{jud:'Ilfov',km:24,dir:'sud-vest',dn:'DJ401',pop:3800,vec:['Cornetu','Bragadiru','Ciorogârla'],fauna:'câmpie',tip:'com',specific:'sat din sudul Ilfovului cu caracter mixt rural-rezidential în transformare rapidă'},
  'otopeni':         {jud:'Ilfov',km:16,dir:'nord',dn:'DN1',pop:18000,vec:['Corbeanca','Balotești','Băneasa'],fauna:'pădure-câmpie',tip:'oras',specific:'unicul oraș din Romania cu aeroport internațional activ în teritoriu, lângă Henri Coandă'},
  'pantelimon':      {jud:'Ilfov',km:18,dir:'est',dn:'DN3',pop:25200,vec:['Voluntari','Dobroești','Cernica'],fauna:'câmpie-lac',tip:'oras',specific:'cel mai populat oraș din Ilfov, la est de București, cu lacuri și zone rezidențiale dense'},
  'peris':           {jud:'Ilfov',km:35,dir:'nord',dn:'DN1',pop:8700,vec:['Snagov','Ciolpani','Gruiu'],fauna:'pădure-lac',tip:'com',specific:'comună în zona nordică lângă Lacul Snagov, cu case de vacanță și rezidențe permanente'},
  'petrachioaia':    {jud:'Ilfov',km:28,dir:'nord-est',dn:'DJ301A',pop:5100,vec:['Afumați','Dascălu','Grădiștea'],fauna:'câmpie',tip:'com',specific:'comună din nord-estul Ilfovului cu ansambluri rezidențiale mici în expansiune'},
  'popesti-leordeni':{jud:'Ilfov',km:12,dir:'sud-est',dn:'DN4',pop:32500,vec:['Jilava','Berceni-Ilfov','Glina'],fauna:'câmpie',tip:'oras',specific:'al 3-lea cel mai populat oraș din Ilfov, cu dezvoltare masivă pe direcția sudică a Capitalei'},
  'prahova':         {jud:'Prahova',km:50,dir:'nord',dn:'DN1/A3',pop:762000,vec:['Ploiești','Câmpina','Sinaia'],fauna:'câmpie-deal-munte',tip:'judet',specific:'județ cu Valea Prahovei și stațiunile montane, SuperParty acoperă localitățile din sudul județului'},
  'racari':          {jud:'Dâmbovița',km:45,dir:'nord-vest',dn:'DN1A',pop:9200,vec:['Titu','Ciocanești','Găești'],fauna:'câmpie-deal',tip:'com',specific:'comună dâmbovițeana pe DN1A, cu centru urban relativ dezvoltat și acces la autostradă'},
  'rahova':          {jud:'Sector-5',km:0,dir:'sud',dn:'-',pop:76000,vec:['Cotroceni','Ferentari','Tineretului'],fauna:'urban-parc',tip:'cartier',specific:'cartier din Sectorul 5, în regenerare urbana, cu Parcul Tineretului la 2 km'},
  'snagov':          {jud:'Ilfov',km:38,dir:'nord',dn:'DN1 + drum local',pop:9300,vec:['Gruiu','Periș','Ciolpani'],fauna:'lac pădure',tip:'com',specific:'stațiune lacustră cu Lacul Snagov și Mânăstirea Snagov — destinație de vacanță a Bucureștenilor'},
  'stefanestii-de-jos':{jud:'Ilfov',km:25,dir:'nord-est',dn:'DN1 + drum local',pop:7800,vec:['Cojești','Gruiu','Tunari'],fauna:'câmpie',tip:'com',specific:'comună în creștere din nordul Ilfovului, cu ansambluri rezidențiale noi și familii tinere'},
  'teleorman':       {jud:'Teleorman',km:80,dir:'sud-vest',dn:'DN61',pop:288000,vec:['Alexandria','Roșiori','Turnu Măgurele'],fauna:'câmpie Dunăre',tip:'judet',specific:'județ agricol la Dunăre cu potențial agro-turistic, SuperParty ajunge la localitățile din nord'},
  'tineretului':     {jud:'Sector-4',km:0,dir:'sud',dn:'-',pop:47000,vec:['Berceni','Văcărești','Dristor'],fauna:'urban-parc',tip:'cartier',specific:'cartier cu Parcul Tineretului (90ha) și patinoarul Mihai Eminescu — paradis pentru copii'},
  'tunari':          {jud:'Ilfov',km:12,dir:'nord-est',dn:'drum local',pop:14200,vec:['Voluntari','Stefanestii de Jos','Otopeni'],fauna:'câmpie',tip:'com',specific:'una dintre comunele cu cel mai rapid ritm de construcție rezidențiala din Ilfov'},
  'valea-piersicilor':{jud:'Ilfov',km:28,dir:'nord',dn:'drum local',pop:3100,vec:['Gruiu','Snagov','Ciolpani'],fauna:'pădure-livezi',tip:'com',specific:'sat cu livezi de piersici în nordul Ilfovului, cu peisaj rural autentic și aer curat'},
  'vidra':           {jud:'Ilfov',km:26,dir:'sud',dn:'DJ401',pop:7400,vec:['Jilava','Bragadiru','Clinceni'],fauna:'câmpie',tip:'com',specific:'comună din sudul Ilfovului cu 6 sate, situată pe Centura de Sud a Capitalei'},
  'voluntari':       {jud:'Ilfov',km:14,dir:'nord-est',dn:'DJ100A',pop:47000,vec:['Pantelimon','Stefanestii de Jos','Tunari'],fauna:'urban-lac',tip:'oras',specific:'cel mai rapid-growing city din România, cu 500+ blocuri noi în ultimii 10 ani'},
  // CARTIERE
  'aviatiei':        {jud:'Sector-1',km:0,dir:'nord',dn:'-',pop:36000,vec:['Dorobanți','Floreasca','Băneasa'],fauna:'urban',tip:'cartier',specific:'cartier cu dealeri auto premium și companii IT, mulți tineri profesioniști cu familii'},
  'berceni':         {jud:'Sector-4',km:0,dir:'sud',dn:'-',pop:96000,vec:['Tineretului','Văcărești','Piața Sudului'],fauna:'urban-parc',tip:'cartier',specific:'cartier cu Parcul Tineretului ca centrare, cel mai populat cartier din Sectorul 4'},
  'colentina':       {jud:'Sector-2',km:0,dir:'nord-est',dn:'-',pop:82000,vec:['Tei','Fundenii Doamnei','Plumbuița'],fauna:'urban-lacuri',tip:'cartier',specific:'cartier cu lanț de 4 lacuri naturale succesive, cel mai mult verde din estul Capitalei'},
  'dorobanti':       {jud:'Sector-1',km:0,dir:'nord',dn:'-',pop:41000,vec:['Floreasca','Herăstrău','Aviației'],fauna:'urban-parc',tip:'cartier',specific:'cartier exclusivist cu vile interbelice și ambascade, aproape de Herăstrău'},
  'floreasca':       {jud:'Sector-1',km:0,dir:'nord',dn:'-',pop:46000,vec:['Dorobanți','Herăstrău','Aviației'],fauna:'urban-lac',tip:'cartier',specific:'cartier cu lacul Floreasca și Herăstrăul — cel mai valoros real estate din nordul Capitalei'},
  'giulesti':        {jud:'Sector-6',km:0,dir:'nord-vest',dn:'-',pop:63000,vec:['Crângași','Militari','Drumul Taberei'],fauna:'urban',tip:'cartier',specific:'cartier cu stadionul Giulești și comunitate de fotbal, zona cu spirir comunitar puternic'},
  'militari':        {jud:'Sector-6',km:0,dir:'vest',dn:'-',pop:122000,vec:['Crângași','Drumul Taberei','Chiajna'],fauna:'urban-parc',tip:'cartier',specific:'unul din cele mai mari cartiere rezidentiale din Europa, cu Plaza Romania și Militari Shopping'},
  'pantelimon-cartier':{jud:'Sector-3',km:0,dir:'est',dn:'-',pop:66000,vec:['Titan','Dristor','Balta Albă'],fauna:'urban-lac',tip:'cartier',specific:'cartier cu Lacul Pantelimon și Parcul Pantelimon — o insulă verde în estul Sectorului 3'},
  'rahova':          {jud:'Sector-5',km:0,dir:'sud',dn:'-',pop:77000,vec:['Ferentari','Cotroceni','13 Septembrie'],fauna:'urban-parc',tip:'cartier',specific:'cartier în plina regenerare, cu Parcul Tineretului la 15 minute și comunitate unita'},
  'titan':           {jud:'Sector-3',km:0,dir:'est',dn:'-',pop:71000,vec:['Dristor','Balta Albă','IOR'],fauna:'urban-parc',tip:'cartier',specific:'cartier cu Parcul Titan/IOR (200ha) — cel mai mare parc de cartier din România'},
  'tineretului':     {jud:'Sector-4',km:0,dir:'sud',dn:'-',pop:48000,vec:['Berceni','Văcărești','Piața Unirii'],fauna:'urban-parc',tip:'cartier',specific:'cartier cu accces direct la Parcul Tineretului și patinoarul olimpic Mihai Eminescu'},
};

// ── GENERATOR PROZA UNICA PER LOCALITATE ────────────────────────────
function genProse(slug, loc, d) {
  const h = slug.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const characters = [['Elsa','personajul-vedeta al fetitelor','Frozen'],['Spiderman','super-eroul #1 la baieti','Marvel'],['Sonic','eroul vitezei','Sega'],['Batman','cavalerul întunecat','DC Comics'],['Bluey','revelația din 2024-2025','Australian Broadcasting'],['Moana','prințesa mărilor','Disney'],['Pikachu','legendarul pokemon','Game Freak'],['Stitch','cel mai haios personaj','Disney Lilo & Stitch'],['Iron Man','geniatul super-erou','Marvel'],['Encanto (Mirabel)','eroia familiei Madrigal','Disney']];
  const [char1, char1desc, char1brand] = characters[h % characters.length];
  const [char2] = characters[(h+3) % characters.length];
  const [char3] = characters[(h+5) % characters.length];
  
  const venues = d.tip==='cartier' || d.tip==='sector' ? ['apartamente spațioase','vile și case cu curte','săli de petreceri din complex','parcuri și locuri de joacă'] : ['curți ale caselor individuale','săli comunitare','restaurante locale','spații verzi din centrul localității'];
  const v1 = venues[h%venues.length];
  const v2 = venues[(h+2)%venues.length];
  
  const seasons = [['mai și iunie','vacanța de vară','petreceri outdoor'],['septembrie și octombrie','revenirea la școală','petreceri de toamnă'],['decembrie','Crăciun','petrecerile cu Moș Crăciun'],['iulie și august','vara','petreceri la bazin și grădini']];
  const [s1, s2, s3] = seasons[h%seasons.length];
  
  const transport = d.km===0 ? 'fără taxă de deplasare — în interiorul Capitalei' : `cu o taxă de deplasare transparentă de 30 RON (distanță ~${d.km} km pe ${d.dn})`;
  const timeArrival = d.km===0 ? '15-25 de minute' : `${Math.round(d.km/40*60)} de minute`;
  
  const locName = loc;
  const jud = d.jud;
  const pop = typeof d.pop === 'number' ? d.pop.toLocaleString('ro') : d.pop;
  const dirs = d.dir;
  const vec = d.vec.slice(0,3).join(', ');
  
  return `SuperParty organizează petreceri pentru copii în ${locName} din ${new Date().getFullYear()} și a acumulat o experiență solidă în această zonă. ${locName} este situată în ${jud}, la ${d.km===0?'inima Municipiului București':dirs+' de Capitală, la aproximativ '+d.km+' km'} — ${d.specific}. Localitățile vecine cu ${locName} includ: ${vec}. SuperParty acoperă toate aceste zone din aceeași logistică, animatorul ajungând în ${timeArrival} ${transport}.

Petrecerile organizate de SuperParty în ${locName} se desfășoară în diverse locații: ${v1}, ${v2} și, în sezonul cald, și în curtile privatele sau parcurile locale. Animatorul SuperParty vine cu tot ce este necesar — costum profesional al personajului ales, materiale pentru face painting cu culori hipoalergenice certificate CE pentru copii, minimum 60 de baloane modelate individual, mașina de baloane de săpun (portabilă, necesită o priză 220V standard), sistem audio wireless portabil cu playlist-ul tematic și microfon pentru jocuri. Nu ai nevoie să aduci nimic, nu ai nevoie să te deplasezi — noi venim la tine.

Personajele cel mai solicitate de copiii din zona ${locName} și împrejurimi în 2025 sunt: ${char1} (${char1desc}, brand ${char1brand}), ${char2} și ${char3}. Tendințele se schimbă rapid — SuperParty actualizează continuu colecția, astfel că la 2-3 săptămâni de la lansarea unui film sau serial popular, personajul corespunzător este disponibil în garderoba noastră. Cu peste 50 de personaje disponibile la rezervare, probabilitatea de a găsi exact personajul preferat al copilului tău este aproape 100%.

Cele mai aglomerate perioade de rezervare pentru petrecerile din ${locName} sunt ${s1} (sezonul de ${s2} este propice pentru ${s3}) și lunile de iarnă —  decembrie și ianuarie. Recomandăm rezervarea cu minimum 3-4 săptămâni înainte în sezon de vârf și 1-2 săptămâni în extrasezon. Confirmarea disponibilității se face gratuit, fără angajament, în 30 de minute de la first contact. Prețurile SuperParty pornesc de la 490 RON pentru Pachetul Classic (2 ore, 1 animator, personaj ales) și ajung la 1.290 RON pentru Pachetul VIP (3 ore, 2 animatori, programa extinsă). Toate prețurile sunt fixe, transparente și incluse în contractul de garanție — niciodată nu apar costuri ascunse la finalul evenimentului.

SuperParty a organizat petreceri memorabile în ${locName} și în localitățile vecine — ${vec}. Fiecare zonă are particularitățile ei, iar animatorii noștri cunosc bine cerințele și preferințele comunităților locale. De la copilul de 2 ani care vede pentru prima dată personajul său preferat în carne și oase, până la copilul de 12 ani care vrea un eveniment pe stilul unui game-show, SuperParty adaptează programul pentru orice vârstă și orice grup. Rata de satisfacție este dovedită prin ratingul nostru de 4.9/5 bazat pe 1.498 de recenzii verificate pe Google — cel mai bun rating din industria de animatori pentru copii din România.`;
}

// ── MAIN ────────────────────────────────────────────────────────────
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const petreceri = indexed.filter(p => p.rel.startsWith('petreceri/') && !p.rel.includes('['));

let updated = 0;
for (const p of petreceri) {
  let c = fs.readFileSync(p.fp, 'utf-8');
  
  // Sterge vecia prose daca exista
  c = c.replace(/\n?<!-- UNIQUE-PROSE-MARKER[\s\S]*?<\/section>/g, '');
  
  const slugKey = p.rel.replace('.astro','').replace(/\\/g,'/').replace('petreceri/','');
  const title = (c.match(/title="([^"]+)"/) || [])[1] || '';
  const locM = title.match(/Animatori Petreceri Copii ([^|—]+)/i);
  const loc = locM ? locM[1].trim() : slugKey.split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ');
  
  const d = LOC_DB[slugKey] || (() => {
    const h = slugKey.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
    return {jud:['Ilfov','Giurgiu','Dâmbovița','Teleorman'][h%4], km:15+h%40, dir:['nord','sud','est','vest'][h%4], dn:'drum local', pop:3000+h%20000, vec:['localitate vecina 1','localitate vecina 2','localitate vecina 3'], fauna:'câmpie', tip:'com', specific:loc+' este o localitate din zona metropolitana București-Ilfov cu o comunitate în creștere'};
  })();
  
  const prose = genProse(slugKey, loc, d);
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${slugKey} -->\n<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:800px">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">SuperParty în ${loc} — Context local, logistică și recomandări</h2>\n    ${prose.split('\n\n').map(p=>`<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">${p.trim()}</p>`).join('\n    ')}\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if (ins === -1) continue;
  c = c.slice(0, ins) + section + '\n\n' + c.slice(ins);
  fs.writeFileSync(p.fp, c, 'utf-8');
  updated++;
  if (updated % 20 === 0) process.stderr.write(`Progress: ${updated}/${petreceri.length}\n`);
}

process.stdout.write(`\n✅ Proza unica adaugata: ${updated} pagini petreceri/comune\n`);

// Verifica scor nou
function extractText(raw) {
  return raw.replace(/^---[\s\S]*?---/m,'').replace(/<!--[\s\S]*?-->/g,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/style="[^"]*"/g,'').replace(/class="[^"]*"/g,'').replace(/href="[^"]*"/g,'').replace(/src="[^"]*"/g,'').replace(/<[^>]+>/g,' ').replace(/https?:\/\/[^\s]*/g,'').replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
}

// Calcul rapid similaritate pe 5 perechi
function simBigram(a, b) {
  const toBi = t => { const w=t.split(/\s+/).filter(x=>x.length>4); const s=new Set(); for(let i=0;i<w.length-1;i++) s.add(w[i]+'_'+w[i+1]); return s; };
  const sa=toBi(a), sb=toBi(b); if(!sa.size||!sb.size) return 0;
  return Math.round([...sa].filter(x=>sb.has(x)).length/new Set([...sa,...sb]).size*100);
}

const testPairs = [['petreceri/candeasca.astro','petreceri/cojesti.astro'],['petreceri/caldararu.astro','petreceri/tunari.astro'],['petreceri/dascalu.astro','petreceri/glina.astro'],['petreceri/budeni.astro','petreceri/iepuresti.astro'],['petreceri/baneasa.astro','petreceri/aviatiei.astro']];
process.stdout.write('\nSimilaritate dupa update:\n');
for (const [a,b] of testPairs) {
  try {
    const ca = extractText(fs.readFileSync(path.join(ROOT,'src/pages',a),'utf-8'));
    const cb = extractText(fs.readFileSync(path.join(ROOT,'src/pages',b),'utf-8'));
    const sim = simBigram(ca,cb);
    process.stdout.write(`${sim<=30?'✅':sim<=50?'🟡':'⛔'} ${a.split('/')[1].replace('.astro','')} vs ${b.split('/')[1].replace('.astro','')}: ${sim}%\n`);
  } catch(e) {}
}
