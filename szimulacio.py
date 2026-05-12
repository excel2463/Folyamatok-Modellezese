import csv

# --- 1. ADATSTRUKTÚRÁK ---

class Auto:
    def __init__(self, id, tipus, erkezes, hatarido, muveletek):
        self.id = id
        self.tipus = tipus
        self.erkezes = int(erkezes)
        self.hatarido = int(hatarido)
        # muveletek: [("GepNev", ido), ...]
        self.muveletek = muveletek
        self.aktualis_muvelet_index = 0
        self.befejezesi_ido = 0

class Gep:
    def __init__(self, nev, puffer_kapacitas=10):
        self.nev = nev
        self.puffer_kapacitas = puffer_kapacitas
        self.felszabadul_ekkor = 0
        self.varolista = []

    def is_free(self, current_time):
        return current_time >= self.felszabadul_ekkor

# --- 2. ADATOK BEOLVASÁSA ---

def adatok_betoltese(fajlnev):
    autok_listaja = []
    try:
        with open(fajlnev, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for sor in reader:
                muveleti_lista = [
                    ("Hegeszto", int(sor['hegesztes_ido'])),
                    ("Festo", int(sor['festes_ido'])),
                    ("Szerelo", int(sor['szereles_ido']))
                ]
                uj_auto = Auto(
                    sor['auto_id'], 
                    sor['tipus'], 
                    sor['prioritas'], 
                    sor['hatarido'], 
                    muveleti_lista
                )
                autok_listaja.append(uj_auto)
        return autok_listaja
    except FileNotFoundError:
        print(f"Hiba: A '{fajlnev}' nem található!")
        return []
    except KeyError as e:
        print(f"Hiba: Hiányzó oszlop a CSV-ben: {e}")
        return []

# --- 3. SZIMULÁCIÓS MOTOR ---

def szimulacio_futtatasa(beolvasott_autok):
    current_time = 0
    befejezett_autok = []
    szallitas_alatt = [] # Azok az autók, amik épp egyik géptől a másikig tartanak
    
    gepek = {
        "Hegeszto": Gep("Hegeszto", puffer_kapacitas=5),
        "Festo": Gep("Festo", puffer_kapacitas=5),
        "Szerelo": Gep("Szerelo", puffer_kapacitas=5)
    }

    print("--- Szimuláció indítása ---")

    # Addig futunk, amíg van autó bárhol a rendszerben
    while beolvasott_autok or szallitas_alatt or any(len(g.varolista) > 0 for g in gepek.values()) or any(g.felszabadul_ekkor > current_time for g in gepek.values()):
        
        # A. Új autók érkezése a gyárkapun
        for auto in list(beolvasott_autok):
            if auto.erkezes <= current_time:
                elso_gep = auto.muveletek[0][0]
                gepek[elso_gep].varolista.append(auto)
                beolvasott_autok.remove(auto)
                print(f"[{current_time}] {auto.id} megérkezett a gyárba -> Sorban áll: {elso_gep}")

        # B. Gépek közötti átmenet kezelése (Szállítás kész)
        for transzfer in list(szallitas_alatt):
            if transzfer['mikor_er_oda'] <= current_time:
                cel_gep = transzfer['hova']
                gepek[cel_gep].varolista.append(transzfer['auto'])
                szallitas_alatt.remove(transzfer)
                print(f"[{current_time}] {transzfer['auto'].id} megérkezett a következő géphez: {cel_gep}")

        # C. Gépek munkájának indítása
        for nev, gep in gepek.items():
            if gep.is_free(current_time) and gep.varolista:
                # Jeles szintű optimalizálás: Határidő (EDD - Earliest Due Date) szerint rendezünk
                gep.varolista.sort(key=lambda x: x.hatarido)
                
                mostani_auto = gep.varolista.pop(0)
                
                # Mennyi ideig dolgozik ezen a gépen?
                muveleti_ido = next(ido for g_nev, ido in mostani_auto.muveletek if g_nev == nev)
                
                befejezes_ideje = current_time + muveleti_ido
                gep.felszabadul_ekkor = befejezes_ideje
                
                print(f"[{current_time}] {mostani_auto.id} megmunkálása a {nev} gépen elkezdődött. (Várható kész: {befejezes_ideje})")

                # Következő lépés meghatározása
                mostani_auto.aktualis_muvelet_index += 1
                
                if mostani_auto.aktualis_muvelet_index < len(mostani_auto.muveletek):
                    # Ha van még hátra gép, "útra bocsátjuk"
                    kov_gep_nev = mostani_auto.muveletek[mostani_auto.aktualis_muvelet_index][0]
                    szallitas_alatt.append({
                        'auto': mostani_auto,
                        'mikor_er_oda': befejezes_ideje,
                        'hova': kov_gep_nev
                    })
                else:
                    # Kész az autó az összes folyamattal
                    mostani_auto.befejezesi_ido = befejezes_ideje
                    befejezett_autok.append(mostani_auto)

        current_time += 1
        if current_time > 20000: # Biztonsági korlát
            print("Hiba: Túl hosszú szimuláció, leállás.")
            break 

    return befejezett_autok

# --- 4. KIÉRTÉKELÉS ---

if __name__ == "__main__":
    autok_kiindulovall = adatok_betoltese('autok.csv')
    
    if autok_kiindulovall:
        eredmenyek = szimulacio_futtatasa(autok_kiindulovall)
        
        print("\n" + "="*50)
        print("STATISZTIKAI KIÉRTÉKELÉS (JELES SZINT)")
        print("="*50)
        
        max_csuszas = 0
        osszes_keses = 0
        kesett_autok_szama = 0
        utolso_befejezes = 0
        
        for a in eredmenyek:
            keses = max(0, a.befejezesi_ido - a.hatarido)
            osszes_keses += keses
            if keses > 0: kesett_autok_szama += 1
            if keses > max_csuszas: max_csuszas = keses
            if a.befejezesi_ido > utolso_befejezes: utolso_befejezes = a.befejezesi_ido
            
            print(f"ID: {a.id:10} | Kész: {a.befejezesi_ido:4} | Határidő: {a.hatarido:4} | Késés: {keses:4}")

        print("-" * 50)
        print(f"1. Utolsó munka befejezése: {utolso_befejezes}")
        print(f"2. Legnagyobb csúszás:      {max_csuszas}")
        print(f"3. Késések összege:         {osszes_keses}")
        print(f"4. Késő munkák száma:       {kesett_autok_szama}")
        print("-" * 50)