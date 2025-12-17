from loader.csv_loader import load_temperatures


def main():
    temps = load_temperatures()
    print(f"{len(temps)} températures chargées")
    print(temps[:10])


if __name__ == "__main__":
    main()
