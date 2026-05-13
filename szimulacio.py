import csv
 
class Auto:
    def __init__(self, id, tipus, erkezes, prioritas, hatarido, muveletek):
        self.id = id
        self.tipus = tipus
        self.erkezes = int(erkezes)       
        self.prioritas = int(prioritas)
        self.hatarido = int(hatarido)
        self.muveletek = muveletek
        self.aktualis_muvelet_index = 0
        self.befejezesi_ido = 0
        self.hatralevo_munkaido = 0
 
class Gep:
    def __init__(self, nev, puffer_kapacitas=5):
        self.nev = nev
        self.puffer_kapacitas = puffer_kapacitas
        self.varolista = []
        self.aktiv_auto = None
 
    def is_free(self):
        return self.aktiv_auto is None
 
def munkaido_van(perc):
    napi_perc = perc % 1440
    return 480 <= napi_perc < 960
 
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
                    sor['erkezes'],      
                    sor['prioritas'],    
                    sor['hatarido'],
                    muveleti_lista
                )
                autok_listaja.append(uj_auto)
        return autok_listaja
    except Exception as e:
        print(f"Hiba a beolvasásnál: {e}")
        return []
 
def szimulacio_futtatasa(beolvasott_autok):
    if not beolvasott_autok: return []
 
    legkorabbi_erkezes = min(a.erkezes for a in beolvasott_autok)
    napi_perc = legkorabbi_erkezes % 1440
    if napi_perc < 480:
        current_time = legkorabbi_erkezes - napi_perc + 480
    elif napi_perc >= 960:
        current_time = legkorabbi_erkezes - napi_perc + 480 + 1440
    else:
        current_time = legkorabbi_erkezes
 
    befejezett_autok = []
    szallitas_alatt = []
    varakozik_puffer_elott = []
 
    gepek = {
        "Hegeszto": Gep("Hegeszto", puffer_kapacitas=5),
        "Festo": Gep("Festo", puffer_kapacitas=5),
        "Szerelo": Gep("Szerelo", puffer_kapacitas=5)
    }
 
    print(f"Szimuláció indítása a(z) {current_time}. perctől...")
 
    while (beolvasott_autok or szallitas_alatt or varakozik_puffer_elott or
           any(not g.is_free() or g.varolista for g in gepek.values())):
        for transzfer in list(szallitas_alatt):
            if transzfer['mikor_er_oda'] <= current_time:
                cel = transzfer['hova']
                if len(gepek[cel].varolista) < gepek[cel].puffer_kapacitas:
                    gepek[cel].varolista.append(transzfer['auto'])
                    szallitas_alatt.remove(transzfer)

        for auto in list(beolvasott_autok):
            if auto.erkezes <= current_time:
                elso_gep = auto.muveletek[0][0]
                if len(gepek[elso_gep].varolista) < gepek[elso_gep].puffer_kapacitas:
                    gepek[elso_gep].varolista.append(auto)
                    beolvasott_autok.remove(auto)
                    print(f"[{current_time}] {auto.id} megérkezett. (prioritás: {auto.prioritas})")
                else:
                    if auto not in varakozik_puffer_elott:
                        varakozik_puffer_elott.append(auto)
                        beolvasott_autok.remove(auto)
                        print(f"[{current_time}] {auto.id} megérkezett, de a puffer teli — várakozik.")

        for auto in list(varakozik_puffer_elott):
            elso_gep = auto.muveletek[0][0]
            if len(gepek[elso_gep].varolista) < gepek[elso_gep].puffer_kapacitas:
                gepek[elso_gep].varolista.append(auto)
                varakozik_puffer_elott.remove(auto)
                print(f"[{current_time}] {auto.id} bekerült a pufferbe.")
 
        if munkaido_van(current_time):
            for nev, gep in gepek.items():
                if gep.aktiv_auto:
                    gep.aktiv_auto.hatralevo_munkaido -= 1
                    if gep.aktiv_auto.hatralevo_munkaido <= 0:
                        kesz_auto = gep.aktiv_auto
                        gep.aktiv_auto = None
 
                        kesz_auto.aktualis_muvelet_index += 1
                        if kesz_auto.aktualis_muvelet_index < len(kesz_auto.muveletek):
                            kov_gep = kesz_auto.muveletek[kesz_auto.aktualis_muvelet_index][0]
                            szallitas_alatt.append({
                                'auto': kesz_auto,
                                'mikor_er_oda': current_time + 1,
                                'hova': kov_gep
                            })
                        else:
                            kesz_auto.befejezesi_ido = current_time
                            befejezett_autok.append(kesz_auto)
                            print(f"[{current_time}] {kesz_auto.id} TELJESEN KÉSZ.")
 
                if gep.is_free() and gep.varolista:
                    gep.varolista.sort(key=lambda x: (x.prioritas, x.hatarido))
                    mostani_auto = gep.varolista.pop(0)
 
                    muveleti_ido = next(ido for g_nev, ido in mostani_auto.muveletek if g_nev == nev)
                    mostani_auto.hatralevo_munkaido = muveleti_ido
                    gep.aktiv_auto = mostani_auto
                    print(f"[{current_time}] {mostani_auto.id} munka megkezdve: {nev} "
                          f"(prioritás: {mostani_auto.prioritas}, határidő: {mostani_auto.hatarido})")
 
        current_time += 1
        if current_time > legkorabbi_erkezes + 100000: break
 
    return befejezett_autok
 
def statisztika_megjelenitese(eredmenyek):
    if not eredmenyek:
        return
 
    befejezesi_idok = [a.befejezesi_ido for a in eredmenyek]
    kesesek = [max(0, a.befejezesi_ido - a.hatarido) for a in eredmenyek]
    atfutasi_idok = [a.befejezesi_ido - a.erkezes for a in eredmenyek]
    keso_munkak = [k for k in kesesek if k > 0]
 
    print(f"\n--- STATISZTIKÁK ---")
    print(f"1. Utolsó munka befejezése (Cmax):  {max(befejezesi_idok)} perc")
    print(f"2. Legnagyobb késés (Tmax):         {max(kesesek)} perc")
    print(f"3. Késések összege (Sum T):         {sum(kesesek)} perc")
    print(f"4. Határidőt túllépő munkák száma:  {len(keso_munkak)} db")
    print(f"5. Átlagos átfutási idő:            {sum(atfutasi_idok)/len(atfutasi_idok):.2f} perc")
 
if __name__ == "__main__":
    autok = adatok_betoltese('autok.csv')
    if autok:
        eredmenyek = szimulacio_futtatasa(autok)
        statisztika_megjelenitese(eredmenyek)
