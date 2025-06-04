import mysql.connector
import sys
import os

# Přidá root složku projektu do sys.path, aby šel najít 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def vytvoreni_test_tabulky():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="task_manager_test"
    )
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS Ukoly")

    cursor.execute("""
        CREATE TABLE Ukoly (
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
    print("Tabulka 'ukoly' byla v databazi 'task_manager_test' úspěšně vytvořena (nebo již existuje).")


if __name__ == "__main__":
    vytvoreni_test_tabulky()
