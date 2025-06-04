import subprocess

def run_tests():
    # Nejdříve vytvoříme test tabulky
    subprocess.run(["python", "tests/test_init.py"])

    while True:
        print("\nCo chceš testovat?")
        print("1. Přidat úkol")
        print("2. Aktualizovat úkol")
        print("3. Odstranit úkol")
        print("4. Spustit vše")
        print("5. Ukončit testování")

        choice = input("Zadej číslo testu: ")

        tests = {
            "1": ["-m", "pridat_ukol"],
            "2": ["-m", "aktualizovat_ukol"],
            "3": ["-m", "odstranit_ukol"],
            "4": [],
        }

        if choice in tests:
            print("\nSpouštím test...")
            subprocess.run(["pytest", "-v", "-s"] + tests[choice], text=True)
        elif choice == "5":
            print("\nKonec testování.")
            break
        else:
            print("\nNeplatná volba.")

if __name__ == "__main__":
    run_tests()