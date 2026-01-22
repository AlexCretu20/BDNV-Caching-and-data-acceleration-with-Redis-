# BDNV-Caching-and-data-acceleration-with-Redis

# Raport – T4 Caching and Data Acceleration with Redis

## Scopul proiectului

Scopul acestui proiect a fost realizarea unei aplicatii care sa demonstreze utilizarea unui sistem de caching in-memory, folosind Redis, pentru accelerarea raspunsurilor la interogari frecvente catre surse de date externe. Aplicatia ofera informatii despre restaurante si cafenele din diferite orase, pe baza unor cereri repetate ale utilizatorilor. In loc ca fiecare cerere sa apeleze un API extern, ceea ce implica un timp mare de asteptare si ocuparea memoriei, folosirea caching-ului aduce eficienta.

Aplicatia este construita pe baza unui API Flask scris in Python, care expune mai multe endpoint-uri pentru cautarea de restaurante, cafenele si gestionarea listelor de favorite. Pentru datele externe este folosit Overpass API (OpenStreetMap), iar pentru persistenta unor informatii este utilizat MongoDB. Redis este integrat ca sistem central de caching, iar pentru monitorizare si analiza performantei sunt folosite Prometheus si Grafana, rulate in containere Docker.

## Arhitectura aplicatiei

Arhitectura aplicatiei este urmatoarea: cererile HTTP ajung mai intai la aplicatia Flask, care decide ce strategie de caching se aplica. In cazul in care cererea a mai fost facuta inainte si exista in Redis, raspunsul este returnat imediat din cache. Daca nu, aplicatia face apel la sursa externa (OpenStreetMap), apoi salveaza rezultatul in Redis pentru cereri viitoare.

Monitorizarea functioneaza in paralel, Prometheus colectand metrici expusi de aplicatie si de Redis, iar Grafana afisand graficele intr-un dashboard.

- Diagrama arhitectura
<img width="420" height="291" alt="image" src="https://github.com/user-attachments/assets/01c6735f-dffc-4222-9364-47bf539a7d32" />

- Diagrama flow Cache Aside

## Implementarea strategiilor de caching

### Implementarea strategiei Cache-Aside

Strategia Cache-Aside este folosita pentru endpoint-ul de cautare a restaurantelor. In acest caz, aplicatia este responsabila atat de citirea din cache, cat si de popularea acestuia.

Atunci cand utilizatorul acceseaza endpoint-ul `/restaurants?city=...`, aplicatia verifica mai intai daca exista o intrare corespunzatoare in Redis, folosind o cheie construita pe baza orasului cautat. Daca datele sunt gasite, raspunsul este returnat direct din cache, iar aplicatia marcheaza acest eveniment ca fiind un cache hit. Daca datele nu exista in cache, aplicatia face un apel catre Overpass API, preia lista de restaurante, o proceseaza si o salveaza in Redis cu un timp de viata (TTL), dupa care raspunsul este trimis utilizatorului. Acest scenariu este considerat un cache miss.

### Implementarea strategiei Read-Through

Pentru cautarea cafenelelor, proiectul foloseste strategia read-through, implementata prin clasa `CafeReadThrough`. Metoda `get` a clasei este responsabila de gestionarea completa a citirii datelor.

Daca datele nu sunt gasite in Redis, metoda apeleaza sursa externa, obtine informatiile necesare si populeaza automat cache-ul, fara ca acest lucru sa fie gestionat explicit in endpoint. Astfel, cache-ul devine transparent pentru restul aplicatiei.

### Implementarea strategiei Write-Through

Pentru gestionarea favoritelor este implementata strategia write-through. Datele sunt scrise simultan in cache si in baza de date, asigurand consistenta intre cele doua.

Atunci cand un utilizator adauga un loc favorit prin endpoint-ul `POST /addFavorites`, aplicatia salveaza informatia atat in Redis, folosind un set, cat si in MongoDB. In cazul in care datele sunt solicitate ulterior prin `GET /getFavorites`, aplicatia incearca mai intai sa le obtina din Redis. Daca acestea nu sunt disponibile, sunt citite din MongoDB si reintroduse in cache.

## Utilizarea structurilor de date Redis

- Pentru caching al listelor de restaurante si cafenele sunt utilizate chei de tip string.
- Pentru gestionarea favoritelor se folosesc set-uri, deoarece acestea previn automat aparitia duplicatelor.
- Pentru pastrarea unui istoric al cautarilor recente este utilizata o lista Redis, limitata la un numar maxim de elemente.
- Pentru realizarea unui clasament al oraselor in functie de numarul de cautari este folosit un sorted set, care permite incrementarea scorului fiecarui oras.
- Sunt folosite Redis Streams pentru a inregistra evenimente de tip add sau remove asupra oraselor favorite, oferind un mecanism de logare a actiunilor.
- Pentru cautari de proximitate este utilizata functionalitatea geospatiala a Redis, permitand identificarea locatiilor aflate in apropierea unei pozitii date.

## TTL, LRU si politici de eviction

Fiecare intrare din cache are asociat un timp de viata (TTL). Dupa expirarea acestui timp, datele sunt eliminate automat din Redis, iar urmatoarea cerere va forta reincarcarea datelor din sursa originala.

Redis este configurat sa foloseasca politica de eviction LRU (Least Recently Used), prin setarea parametrului `allkeys-lru`. Aceasta asigura eliminarea automata a cheilor cel mai putin utilizate atunci cand memoria maxima este atinsa. Comportamentul LRU este demonstrat in proiect prin rularea unui script dedicat care forteaza umplerea memoriei cache.

## Invalidare pentru updates, deletes si stale handling

Invalidarea cache-ului este tratata explicit pentru operatiile de delete. In cazul stergerii unui favorit, cheia corespunzatoare din Redis este eliminata manual, fortand aplicatia sa citeasca din MongoDB la urmatoarea cerere.

Pentru datele externe, invalidarea este realizata implicit prin expirarea TTL-ului, prevenind astfel utilizarea de date invechite. La adaugare este folosita strategia write-through (scriere simultana in Redis si MongoDB), ceea ce asigura consistenta cache-ului si elimina posibilitatea de date stale.

## Evaluarea performantei si diagramele

Aplicatia expune metrici Prometheus care masoara:
- cache hit/miss ratio
- latenta citirilor din cache si din sursa externa
- rata de cereri pe secunda
- numarul de evictii

Aceste metrici sunt colectate de Prometheus si afisate intr-un dashboard Grafana.

Scalabilitatea sub incarcare este testata cu un script de load testing care genereaza cereri concurente timp de o perioada fixa. In timpul testului se observa cresterea ratei de cereri pe secunda si imbunatatirea raportului hit/miss pe masura ce cache-ul se repeta. Graficele din Grafana evidentiaza diferenta de latenta intre cererile servite din cache si cele care ajung la sursa externa.

## Output din terminal

```text
(.venv) PS D:\Nicola\BDNSV\BDNV-Caching> python load_test.py
Threads: 20
Duration: 60s
Total requests: 194  OK: 150  ERR: 44
Approx RPS: 3.18


link Demo partea 1: https://youtu.be/jlaBPiAnJEE
link Demo partea 2: https://youtu.be/F7T2mBYGy2A
