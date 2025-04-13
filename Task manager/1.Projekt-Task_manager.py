ukoly = []

def pridat_ukol():
    global ukoly
    nazev_ukolu = input("Zadejte název úkolu: ")
    popis_ukolu = input("Zadejte popis úkolu: ")
    if nazev_ukolu == "" or popis_ukolu == "":
        print("Zadali jste prázdnou hodnotu, zadejte vstupní hodnoty znovu.\n")
        pridat_ukol()
    else:
        ukoly.append(nazev_ukolu + " - " + popis_ukolu)
        print(f"Úkol '{nazev_ukolu}' byl přidán.\n")
    hlavni_menu()

def seznam_ukolu():
    global ukoly
    if ukoly:
        print("Seznam úkolů:")
        cislo_ukolu = 1
        for item in ukoly:
            print(f"{cislo_ukolu}. {item}")
            cislo_ukolu = cislo_ukolu + 1
        print("")
    else:
        print("Seznam úkolů je prázdný.\n")
        hlavni_menu()

def zobrazit_ukoly():
    seznam_ukolu()
    hlavni_menu()

def odstranit_ukol():
    seznam_ukolu()
    odstr_ukol = (input("Zadejte číslo úkolu, které chcete odstranit: "))
    if odstr_ukol.isdigit():
        odstr_ukol = int(odstr_ukol)
        interval = range(1, len(ukoly) + 1)
        if odstr_ukol in interval:
            odstraneny_ukol = ukoly.pop(odstr_ukol-1)
            odstraneny_ukol = odstraneny_ukol.split(" - ")
            print(f"Úkol '{odstraneny_ukol[0]}' byl odstraněn.\n")
            hlavni_menu()
        else:
            print(f"Zadaná hodnota musí být celé číslo v intervalu <1, {len(ukoly)}>, zkuste znovu.\n")
            odstranit_ukol()
    else:
        print(f"Zadaná hodnota musí být celé číslo v intervalu <1, {len(ukoly)}>, zkuste znovu.\n")
        odstranit_ukol()

def hlavni_menu():
    print("Správce úkolů - Hlavní menu")
    print("1. Přidat nový úkol")
    print("2. Zobrazit všechny úkoly")
    print("3. Odstranit úkol")
    print("4. Konec programu")
    vyber_ukolu = input("Vyberte možnost (1-4): ")
    print("")
    
    while vyber_ukolu != "4":
        if vyber_ukolu == "1":
            pridat_ukol()
        elif vyber_ukolu == "2":
            zobrazit_ukoly()
        elif vyber_ukolu == "3":
            odstranit_ukol()  
        else: 
            print("Zadána neplatná volba úkolu, zkuste znovu.\n")
            hlavni_menu()
    else:
        print("Konec programu.")
        exit()

hlavni_menu()