import csv

class Auto:
    def __init__(self, id, tipus, erkezes, hatarido, muveletek):
        self.id = id
        self.tipus = tipus
        self.erkezes = int(erkezes)
        self.hatarido = int(hatarido)
        self.muveletek = muveletek

def adatok_betoltese(fajlnev):
    autok_listaja = []  # Ebbe gyűjtjük az autókat
    try:
        # Itt a 'fajlnev' változót használjuk, ami egy szöveg (string)
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
        print(f"Hiba: A '{fajlnev}' fájl nem található!")
        return []

# Használat a kért fájlnévvel:
gyartosor_lista = adatok_betoltese('autok.csv')

for a in gyartosor_lista:
    print(f"Beolvasva: {a.tipus} (ID: {a.id}), Érkezik: {a.erkezes}")