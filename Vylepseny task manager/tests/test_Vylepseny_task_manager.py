import mysql.connector
import pytest
from tests.test_init import vytvoreni_test_tabulky
from src.Vylepseny_task_manager import pridat_ukol, aktualizovat_ukol, odstranit_ukol

#vytvoreni tabulky pred testy
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    vytvoreni_test_tabulky()

#oddelena databaze
@pytest.fixture(scope="module")
def db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="task_manager_test"
    )
    yield conn
    conn.close()

#uklid testovaci databaze pred prvnim testem a po kazdem testu
@pytest.fixture(autouse=True) 
def clean_ukoly_table(db_connection):
    # Před prvním testem
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM Ukoly")
    cursor.execute("ALTER TABLE Ukoly AUTO_INCREMENT = 1")
    db_connection.commit()
    cursor.close()
    # test proběhne
    yield  
    # Po každém testu
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM Ukoly")
    cursor.execute("ALTER TABLE Ukoly AUTO_INCREMENT = 1")
    db_connection.commit()
    cursor.close()



#testovani funkcnosti databaze funkce 'pridat_ukol' pro ruzne vstupy 'nazev' a 'popis'
@pytest.mark.pridat_ukol
@pytest.mark.parametrize("nazev, popis, validni", [
    ("Test_nazev", "Test_popis", True),
    ("Duplicitni_nazev", "Duplicitni_popis", False),
    ("BezPopisu", None, False),
    (None, "BezNazvu", False),
    (None, None, False)
],
ids=["Test s platnymi vstupy", "Test na duplicitni nazev", "Test bez zadaneho popisu", "Test bez zadaneho nazvu", "Test bez zadaneho nazvu i popisu"]                   
)
def test_db_pridat_ukol(nazev, popis, validni, db_connection, monkeypatch):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Duplicitni_nazev', 'Duplicitni_popis')")
    db_connection.commit()
    cursor.close()

    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ukoly WHERE Nazev = %s", (nazev,))
    pocet_pred = cursor.fetchone()[0]
    print(f"\nPočet úkolů před použitím funkce 'pridat_ukol': {pocet_pred}")
    cursor.close()

    vstupy = iter([
        "" if nazev is None else nazev,
        "" if popis is None else popis
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    pridat_ukol(test_mode=True, conn=db_connection)

    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ukoly WHERE Nazev = %s", (nazev,))
    pocet_po = cursor.fetchone()[0]
    print(f"Počet úkolů po použití funkce 'pridat_ukol': {pocet_po}")
    cursor.close()

    if validni:
        assert pocet_po > pocet_pred
    else:
        assert pocet_po == pocet_pred



#testovani vystupnich hlasek funkce 'pridat_ukol' pro ruzne vstupy 'nazev' a 'popis'
@pytest.mark.pridat_ukol
@pytest.mark.parametrize("nazev, popis, ocekavany_vystup", [
    ("Test_nazev", "Test_popis", "byl přidán"),
    ("Duplicitni_nazev", "Duplicitni_popis", "už existuje"),
    ("BezPopisu", None, "musí být vyplněny"),
    (None, "BezNazvu", "musí být vyplněny"),
    (None, None, "musí být vyplněny")
],
ids=["Test s platnymi vstupy", "Test na duplicitni nazev", "Test bez zadaneho popisu", "Test bez zadaneho nazvu", "Test bez zadaneho nazvu i popisu"]
)
def test_print_pridat_ukol(nazev, popis, ocekavany_vystup, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Duplicitni_nazev', 'Duplicitni_popis')")
    db_connection.commit()
    cursor.close()
    
    vstupy = iter([
        "" if nazev is None else nazev,
        "" if popis is None else popis
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    pridat_ukol(test_mode=True, conn=db_connection)

    print(f"Očekávaný výstup by měl obsahovat: {ocekavany_vystup}")
    skutecny_vystup = capsys.readouterr().out
    print(f"\nSkutečný výstup: {skutecny_vystup}")
    assert ocekavany_vystup in skutecny_vystup



#testovani funkcnosti databaze funkce 'aktualizovat_ukol' pro ruzne vstupy 'id' a 'stav'
@pytest.mark.aktualizovat_ukol
@pytest.mark.parametrize("id, validni", [
    (1, True),
    (1000, False),
    ("Text", False),
    (None, False)
],
ids=["Test s platnym ID", "Test s ID = neplatne cislo", "Test s ID = retezec", "Test s nezadanym ID"]
)
@pytest.mark.parametrize("puvodni_stav, zvoleny_stav, ocekavany_stav", [
    ("Nezahájeno", "P", "Probíhá"),
    ("Nezahájeno", "H", "Hotovo"),
    ("Nezahájeno", "X", None), 
    ("Probíhá", "P", "Probíhá"),
    ("Probíhá", "H", "Hotovo"),
    ("Probíhá", "X", None),
    ("Hotovo", "P", "Probíhá"),
    ("Hotovo", "H", "Hotovo"),
    ("Hotovo", "X", None)
])
def test_db_aktualizovat_ukol(id, validni, puvodni_stav, zvoleny_stav, ocekavany_stav, db_connection, monkeypatch):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis, Stav) VALUES ('Nazev_k_aktualizaci', 'Popis_k_aktualizaci', %s)", (puvodni_stav,))
    db_connection.commit()
    cursor.close()

    vstupID = str(id) if id is not None else ""
    vstupy = iter([zvoleny_stav, vstupID])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    aktualizovat_ukol(test_mode=True, conn=db_connection)

    cursor = db_connection.cursor()
    cursor.execute("SELECT Stav FROM Ukoly WHERE Nazev = %s", ('Nazev_k_aktualizaci',))
    novy_stav = cursor.fetchone()[0]
    print(f"Skutečný nový stav: {novy_stav}")
    cursor.close()

    if validni and ocekavany_stav:
        print(f"Očekávaný nový stav při platných vstupech: {ocekavany_stav}")
        assert novy_stav == ocekavany_stav
    else:
        print(f"Očekávaný nový stav při neplatných vstupech: {puvodni_stav}")
        assert novy_stav == puvodni_stav



#testovani vystupnich hlasek funkce 'aktualizovat_ukol' pro ruzne vstupy 'id' a 'stav'
@pytest.mark.aktualizovat_ukol
@pytest.mark.parametrize("id, ocekavany_vystup", [
    (1, "byl změněn"),
    (1000, "nebylo nalezeno v seznamu úkolů"),
    ("Text", "musí být číslo ze zobrazeného seznamu úkolů"),
    (None, "musí být číslo ze zobrazeného seznamu úkolů")
],
ids=["Test s platnym ID", "Test s ID = neplatne cislo", "Test s ID = retezec", "Test s nezadanym ID"]
)
@pytest.mark.parametrize("puvodni_stav, zvoleny_stav, ocekavany_stav", [
    ("Nezahájeno", "P", "Probíhá"),
    ("Nezahájeno", "H", "Hotovo"),
    ("Nezahájeno", "X", None), 
    ("Probíhá", "P", "Probíhá"),
    ("Probíhá", "H", "Hotovo"),
    ("Probíhá", "X", None),
    ("Hotovo", "P", "Probíhá"),
    ("Hotovo", "H", "Hotovo"),
    ("Hotovo", "X", None)
])
def test_print_aktualizovat_ukol(id, ocekavany_vystup, puvodni_stav, zvoleny_stav, ocekavany_stav, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis, Stav) VALUES ('Nazev_k_aktualizaci', 'Popis_k_aktualizaci', %s)", (puvodni_stav,))
    db_connection.commit()

    vstupID = str(id) if id is not None else ""
    vstupy = iter([zvoleny_stav, vstupID])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    aktualizovat_ukol(test_mode=True, conn=db_connection)

    print(f"Očekávaný výstup by měl obsahovat: {ocekavany_vystup}")
    skutecny_vystup = capsys.readouterr().out
    print(f"\nSkutečný výstup: {skutecny_vystup}")

    if not ocekavany_stav:
        assert "Neplatná volba stavu, zkuste znovu." in skutecny_vystup  
    else:
        assert ocekavany_vystup in skutecny_vystup

    cursor.close()



#testovani funkcnosti databaze funkce 'odstranit_ukol' pro ruzne vstupy 'id'
@pytest.mark.odstranit_ukol
@pytest.mark.parametrize("id, validni", [
    (1, True),
    (1000, False),
    ("Text", False),
    (None, False)
],
ids=["Test s platnym ID", "Test s ID = neplatne cislo", "Test s ID = retezec", "Test s nezadanym ID"]
)
def test_db_odstranit_ukol(id, validni, db_connection, monkeypatch):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Nazev_k_smazani', 'Popis_k_smazani')")
    db_connection.commit()
    cursor.close()

    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ukoly")
    pocet_pred = cursor.fetchone()[0]
    print(f"\nPočet úkolů před použitím funkce 'odstranit_ukol': {pocet_pred}")
    cursor.close()

    vstupID = str(id) if id is not None else ""
    vstupy = iter([vstupID])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    odstranit_ukol(test_mode=True, conn=db_connection)

    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ukoly")
    pocet_po = cursor.fetchone()[0]
    print(f"Počet úkolů po použití funkce 'odstranit_ukol': {pocet_po}")
    cursor.close()

    if validni:
        assert pocet_po < pocet_pred
    else:
        assert pocet_po == pocet_pred



#testovani vystupnich hlasek funkce 'odstranit_ukol' pro ruzne vstupy 'id'
@pytest.mark.odstranit_ukol
@pytest.mark.parametrize("id, ocekavany_vystup", [
    (1, "byl odstraněn"),
    (1000, "nebylo nalezeno v seznamu úkolů"),
    ("Text", "musí být číslo ze zobrazeného seznamu úkolů"),
    (None, "musí být číslo ze zobrazeného seznamu úkolů")
],
ids=["Test s platnym ID", "Test s ID = neplatne cislo", "Test s ID = retezec", "Test s nezadanym ID"]
)
def test_print_odstranit_ukol(id, ocekavany_vystup, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Nazev_k_smazani', 'Popis_k_smazani')")
    db_connection.commit()
    cursor.close()

    vstup = str(id) if id is not None else ""
    vstupy = iter([vstup])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    odstranit_ukol(test_mode=True, conn=db_connection)

    print(f"Očekávaný výstup by měl obsahovat: {ocekavany_vystup}")
    skutecny_vystup = capsys.readouterr().out
    print(f"\nSkutečný výstup: {skutecny_vystup}")
    assert ocekavany_vystup in skutecny_vystup


