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
<img width="360" height="487" alt="image" src="https://github.com/user-attachments/assets/9f431f27-4c3f-48d8-baa4-b64e25e0b7e2" />

## Implementarea strategiilor de caching

### Implementarea strategiei Cache-Aside

Strategia Cache-Aside este folosita pentru endpoint-ul de cautare a restaurantelor. In acest caz, aplicatia este responsabila atat de citirea din cache, cat si de popularea acestuia.

Atunci cand utilizatorul acceseaza endpoint-ul `/restaurants?city=...`, aplicatia verifica mai intai daca exista o intrare corespunzatoare in Redis, folosind o cheie construita pe baza orasului cautat. Daca datele sunt gasite, raspunsul este returnat direct din cache, iar aplicatia marcheaza acest eveniment ca fiind un cache hit. Daca datele nu exista in cache, aplicatia face un apel catre Overpass API, preia lista de restaurante, o proceseaza si o salveaza in Redis cu un timp de viata (TTL), dupa care raspunsul este trimis utilizatorului. Acest scenariu este considerat un cache miss.

<img width="502" height="268" alt="image" src="https://github.com/user-attachments/assets/7693c3cb-aef5-49d8-ad14-24a3e6bae9bd" />
<img width="602" height="325" alt="image" src="https://github.com/user-attachments/assets/9448b790-193e-47ad-960d-4d34423748b7" />
<img width="602" height="126" alt="image" src="https://github.com/user-attachments/assets/e491c6d1-e35a-4c5f-b746-956ce76e378c" />

### Implementarea strategiei Read-Through

Pentru cautarea cafenelelor, proiectul foloseste strategia read-through, implementata prin clasa `CafeReadThrough`. Metoda `get` a clasei este responsabila de gestionarea completa a citirii datelor.

Daca datele nu sunt gasite in Redis, metoda apeleaza sursa externa, obtine informatiile necesare si populeaza automat cache-ul, fara ca acest lucru sa fie gestionat explicit in endpoint. Astfel, cache-ul devine transparent pentru restul aplicatiei.

<img width="542" height="289" alt="image" src="https://github.com/user-attachments/assets/c9ebd3aa-77c6-4508-8ef3-551901ebce58" />
<img width="602" height="143" alt="image" src="https://github.com/user-attachments/assets/9f5ee38e-5022-4cb3-b61d-95f261a0a3d1" />
<img width="602" height="101" alt="image" src="https://github.com/user-attachments/assets/aa6b0b74-feec-427f-8e14-7c82ffaf7caa" />

### Implementarea strategiei Write-Through

Pentru gestionarea favoritelor este implementata strategia write-through. Datele sunt scrise simultan in cache si in baza de date, asigurand consistenta intre cele doua.

Atunci cand un utilizator adauga un loc favorit prin endpoint-ul `POST /addFavorites`, aplicatia salveaza informatia atat in Redis, folosind un set, cat si in MongoDB. In cazul in care datele sunt solicitate ulterior prin `GET /getFavorites`, aplicatia incearca mai intai sa le obtina din Redis. Daca acestea nu sunt disponibile, sunt citite din MongoDB si reintroduse in cache.

<img width="602" height="154" alt="image" src="https://github.com/user-attachments/assets/5b3a87b9-e34b-480b-9179-b2af1e1a99c6" />
<img width="602" height="225" alt="image" src="https://github.com/user-attachments/assets/d5d032eb-643b-47b4-adc3-f1f5303a02ce" />

## Utilizarea structurilor de date Redis

- Pentru caching al listelor de restaurante si cafenele sunt utilizate chei de tip string.
- Pentru gestionarea favoritelor se folosesc set-uri, deoarece acestea previn automat aparitia duplicatelor.
- Pentru pastrarea unui istoric al cautarilor recente este utilizata o lista Redis, limitata la un numar maxim de elemente.
- Pentru realizarea unui clasament al oraselor in functie de numarul de cautari este folosit un sorted set, care permite incrementarea scorului fiecarui oras.
- Sunt folosite Redis Streams pentru a inregistra evenimente de tip add sau remove asupra oraselor favorite, oferind un mecanism de logare a actiunilor.
- Pentru cautari de proximitate este utilizata functionalitatea geospatiala a Redis, permitand identificarea locatiilor aflate in apropierea unei pozitii date.
  
<img width="602" height="338" alt="image" src="https://github.com/user-attachments/assets/e8b2c6ec-63a0-4dcd-bbb0-a1e5b29c5573" />
<img width="602" height="338" alt="image" src="https://github.com/user-attachments/assets/2294f844-3450-47f4-be7e-fe46e37af9d9" />
<img width="602" height="338" alt="image" src="https://github.com/user-attachments/assets/c3f20f37-43ae-47c2-804d-9fff0f99acd7" />

## TTL, LRU si politici de eviction

Fiecare intrare din cache are asociat un timp de viata (TTL). Dupa expirarea acestui timp, datele sunt eliminate automat din Redis, iar urmatoarea cerere va forta reincarcarea datelor din sursa originala.

Redis este configurat sa foloseasca politica de eviction LRU (Least Recently Used), prin setarea parametrului `allkeys-lru`. Aceasta asigura eliminarea automata a cheilor cel mai putin utilizate atunci cand memoria maxima este atinsa. Comportamentul LRU este demonstrat in proiect prin rularea unui script dedicat care forteaza umplerea memoriei cache.

<img width="545" height="277" alt="image" src="https://github.com/user-attachments/assets/dc1f2f97-b6f9-49af-ac6a-f47debb6e4e9" />

## Invalidare pentru updates, deletes si stale handling

Invalidarea cache-ului este tratata explicit pentru operatiile de delete. In cazul stergerii unui favorit, cheia corespunzatoare din Redis este eliminata manual, fortand aplicatia sa citeasca din MongoDB la urmatoarea cerere.

Pentru datele externe, invalidarea este realizata implicit prin expirarea TTL-ului, prevenind astfel utilizarea de date invechite. La adaugare este folosita strategia write-through (scriere simultana in Redis si MongoDB), ceea ce asigura consistenta cache-ului si elimina posibilitatea de date stale.

<img width="624" height="351" alt="image" src="https://github.com/user-attachments/assets/5bf2fc95-6ed7-4703-b482-4005dd1d6668" />
<img width="624" height="80" alt="image" src="https://github.com/user-attachments/assets/e50d0f47-9895-4a5a-afa0-e3b8417d7f88" />
<img width="624" height="160" alt="image" src="https://github.com/user-attachments/assets/5856f360-85e0-46ca-a92f-e20682640ef1" />
<img width="624" height="104" alt="image" src="https://github.com/user-attachments/assets/ac5f797a-4a41-4ac6-81b5-410089e44cc5" />


## Evaluarea performantei si diagramele

Aplicatia expune metrici Prometheus care masoara:
- cache hit/miss ratio
- latenta citirilor din cache si din sursa externa
- rata de cereri pe secunda
- numarul de evictii

Aceste metrici sunt colectate de Prometheus si afisate intr-un dashboard Grafana.

Scalabilitatea sub incarcare este testata cu un script de load testing care genereaza cereri concurente timp de o perioada fixa. In timpul testului se observa cresterea ratei de cereri pe secunda si imbunatatirea raportului hit/miss pe masura ce cache-ul se repeta. Graficele din Grafana evidentiaza diferenta de latenta intre cererile servite din cache si cele care ajung la sursa externa.

<img width="602" height="279" alt="image" src="https://github.com/user-attachments/assets/dad57418-5ca1-443f-9005-fc882b1acbe0" />
<img width="602" height="285" alt="image" src="https://github.com/user-attachments/assets/1f37c1d7-3273-4232-af9b-83fd7cf41f5d" />
<img width="602" height="282" alt="image" src="https://github.com/user-attachments/assets/af14b9ef-f0c8-4d72-b379-67b290eab79a" />
<img width="602" height="284" alt="image" src="https://github.com/user-attachments/assets/c04a6f4b-e36b-4780-af8d-a564fd114fae" />

 Output din terminal

```text
(.venv) PS D:\Nicola\BDNSV\BDNV-Caching> python load_test.py
Threads: 20
Duration: 60s
Total requests: 194  OK: 150  ERR: 44
Approx RPS: 3.18
(.venv) PS D:\Nicola\BDNSV\BDNV-Caching> python load_test.py
Threads: 20
Duration: 60s
Total requests: 207  OK: 201  ERR: 6
Approx RPS: 3.39
```

link Demo partea 1: https://youtu.be/jlaBPiAnJEE

link Demo partea 2: https://youtu.be/F7T2mBYGy2A
