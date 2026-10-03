from catalog.demo_data import seed_demo_data


def run():
    counts = seed_demo_data()
    print("Demo catalog reset.")
    for name, count in counts.items():
        print(f"{name.capitalize()}: {count}")
