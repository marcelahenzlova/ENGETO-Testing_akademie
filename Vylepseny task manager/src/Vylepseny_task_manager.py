import mysql.connector
from mysql.connector import Error


def pripojeni_db(test_mode=False):
    databaze = "task_manager_test" if test_mode else "task_manager"
    try:
        spojeni = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",  
            database=databaze
        )
        if spojeni.is_connected():
            return spojeni
        
    except Error as e:
        print(f"❌ Chyba při připojení k databázi: {e}")
        return None


def vytvoreni_tabulky(test_mode=False):
    conn = pripojeni_db(test_mode=test_mode)
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ukoly (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            Nazev VARCHAR(255) NOT NULL UNIQUE,
            Popis VARCHAR(255) NOT NULL,
            Stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
            DatumVytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tabulka 'ukoly' byla v databazi 'task_manager' úspěšně vytvořena (nebo již existuje).")



def pridat_ukol(test_mode=False, conn=None):
    own_conn = False
    if conn is None:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return
        own_conn = True

    while True:
        cursor = conn.cursor()
        try:
            nazev = input("\nZadej název úkolu: ").strip()
            popis = input("Zadej popis úkolu: ").strip()

            if not nazev or not popis:
                raise ValueError("❌ Název i popis musí být vyplněny.")

            cursor.execute("SELECT COUNT(*) FROM Ukoly WHERE Nazev = %s", (nazev,))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                raise ValueError(f"❌ Úkol s názvem '{nazev}' už existuje.")
            
            cursor.execute("INSERT INTO Ukoly (Nazev, Popis, Stav) VALUES (%s, %s, 'Nezahájeno')", (nazev, popis))
            conn.commit()
            print(f"✅ Úkol '{nazev}' byl přidán.")
            cursor.close()
            break

        except ValueError as e:
            print(f"❌ Chyba: {e}")
            if test_mode:
                break

        except Exception as e:
            print(f"❌ Neočekávaná chyba: {e}")
            if cursor:
                cursor.close()
            break

        finally:
            cursor.close()

    if own_conn and not test_mode:
        conn.close()



def zobrazit_ukoly(test_mode=False):
    try:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly")
        rows = cursor.fetchall()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly WHERE Stav IN ('Nezahájeno', 'Probíhá')")
        filtr = cursor.fetchall()

        if not rows:
            print("\n✅ Seznam úkolů je prázdný.")
        elif rows and not filtr:
            print("\n✅ Všechny úkoly jsou již hotové.")
        else:
            print("\n✅ Seznam nehotových úkolů:")
            for row in filtr:
                print(f"{row[0]}. {row[1]} – {row[2]} ({row[3]})")

        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")



def seznam_ukolu(test_mode=False):
    try:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly")
        rows = cursor.fetchall()

        if not rows:
            print("\n✅ Seznam úkolů je prázdný.")
        else:
            print("\n✅ Seznam úkolů:")
            for row in rows:
                print(f"{row[0]}. {row[1]} – {row[2]} ({row[3]})")

        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")



def aktualizovat_ukol(test_mode=False, conn=None):
    own_conn = False
    if conn is None:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return
        own_conn = True

    while True:
        cursor = conn.cursor()
        try:
            stav = input("\nZadejte nový stav ('P' = Probíhá, 'H' = Hotovo): ").strip().upper()
            novy_stav = "Probíhá" if stav == "P" else "Hotovo" if stav == "H" else None
            if not novy_stav:
                print("❌ Neplatná volba stavu, zkuste znovu.")
                if test_mode:
                    break
                else:
                    continue

            ukol_id = input("Zadejte ID úkolu k aktualizaci: ")
            if not ukol_id.isdigit():
                print("❌ ID musí být číslo ze zobrazeného seznamu úkolů, zkuste znovu.")
                if test_mode:
                    break
                else:
                    continue

            ukol_id = int(ukol_id)

            cursor.execute("SELECT Nazev FROM Ukoly WHERE ID = %s", (ukol_id,))
            nazev = cursor.fetchone()

            if not nazev:
                print(f"❌ Číslo úkolu '{ukol_id}' nebylo nalezeno v seznamu úkolů, zkuste znovu.")
                if test_mode:
                    break
                else:
                    continue

            cursor.execute("UPDATE Ukoly SET Stav = %s WHERE ID = %s", (novy_stav, ukol_id))
            conn.commit()
            print(f"✅ Stav úkolu '{ukol_id}. {nazev[0]}' byl změněn na '{novy_stav}'.")
            break

        except Exception as e:
            print(f"❌ Neočekávaná chyba: {e}")
            conn.rollback()
            if test_mode:
                break

        finally:
            cursor.close()

    if own_conn and not test_mode:
        conn.close()



def odstranit_ukol(test_mode=False, conn=None):
    own_conn = False
    if conn is None:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return
        own_conn = True

    while True:
        cursor = conn.cursor()
        try:
            ukol_id = input("\nZadejte ID úkolu k odstranění: ")
            if not ukol_id.isdigit():
                print("❌ ID musí být číslo ze zobrazeného seznamu úkolů, zkuste znovu.")
                if test_mode:
                    break
                else:
                    continue

            ukol_id = int(ukol_id)

            cursor.execute("SELECT Nazev FROM Ukoly WHERE ID = %s", (ukol_id,))
            nazev = cursor.fetchone()

            if not nazev:
                print(f"❌ Číslo úkolu '{ukol_id}' nebylo nalezeno v seznamu úkolů, zkuste znovu.")
                if test_mode:
                    break
                else:
                    continue

            cursor.execute("DELETE FROM Ukoly WHERE ID = %s", (ukol_id,))
            conn.commit()
            print(f"✅ Úkol '{ukol_id}. {nazev[0]}' byl odstraněn.")
            break

        except Exception as e:
            print(f"❌ Neočekávaná chyba: {e}")
            conn.rollback()
            if test_mode:
                break

        finally:
            cursor.close()

    if own_conn and not test_mode:
        conn.close()



def hlavni_menu():
    while True:
        print("\nSprávce úkolu - Hlavní menu")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")
        volba = input("Vyberte možnost (0-5): ")

        if volba == "1":
            pridat_ukol()
            
        elif volba == "2":
            zobrazit_ukoly()

        elif volba == "3":
            seznam_ukolu()
            aktualizovat_ukol() 

        elif volba == "4":
            seznam_ukolu()
            odstranit_ukol()

        elif volba == "5":
            print("\nKonec programu.")
            break

        else:
            print("\nNeplatná volba, vyberte číslo 1–5.")


if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()