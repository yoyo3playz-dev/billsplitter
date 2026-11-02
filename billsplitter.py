import re
from decimal import Decimal

MENU = """
--- BillSplitter ---
1. Add a person
2. Remove a person
3. Add an item
4. Remove an item
5. Split the bill
6. Quit"""


def parse_money(text):
    text = text.strip().removeprefix("$").strip()
    if not re.fullmatch(r"([0-9]{1,3}(,[0-9]{3})+|[0-9]+)(\.[0-9]{0,2})?|\.[0-9]{1,2}", text):
        raise ValueError("enter an amount like 12.50 (max 2 decimals, no negatives)")
    cents = int(Decimal(text.replace(",", "")) * 100)
    if cents == 0:
        raise ValueError("the amount must be more than zero")
    if cents > 100_000_000:
        raise ValueError("that amount is too big")
    return cents


def format_money(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def find_people(text, people):
    if not text.strip():
        return list(people)
    by_lower = {p.lower(): p for p in people}
    found = []
    for part in text.split(","):
        name = by_lower.get(part.strip().lower())
        if name is None:
            raise ValueError(f"I don't know '{part.strip()}'")
        if name not in found:
            found.append(name)
    return found


def split_item(price, count):
    share, extra = divmod(price, count)
    return [share + 1 if i < extra else share for i in range(count)]


def calculate_owed(people, items):
    owed = {name: 0 for name in people}
    for item in items:
        shares = split_item(item["price"], len(item["shared_by"]))
        for name, share in zip(item["shared_by"], shares):
            owed[name] += share
    return owed


def add_person(bill):
    name = " ".join(input("Name: ").split())
    if not name or len(name) > 20 or "," in name:
        raise ValueError("name must be 1-20 characters with no commas")
    if name.lower() in (p.lower() for p in bill["people"]):
        raise ValueError(f"{name} is already added")
    bill["people"].append(name)
    print(f"Added {name}.")


def remove_person(bill):
    names = find_people(input("Who? "), bill["people"])
    if len(names) != 1:
        raise ValueError("type exactly one name")
    name = names[0]
    if any(name in item["shared_by"] for item in bill["items"]):
        raise ValueError(f"{name} is on some items, remove those items first")
    bill["people"].remove(name)
    print(f"Removed {name}.")


def add_item(bill):
    if not bill["people"]:
        raise ValueError("add some people first")
    name = " ".join(input("Item: ").split())
    if not name:
        raise ValueError("the item needs a name")
    price = parse_money(input("Price: "))
    shared_by = find_people(
        input("Shared by (names with commas, empty = everyone): "), bill["people"])
    bill["items"].append({"name": name, "price": price, "shared_by": shared_by})
    print(f"Added {name} for {format_money(price)}, shared by {', '.join(shared_by)}.")


def remove_item(bill):
    if not bill["items"]:
        raise ValueError("there are no items")
    for number, item in enumerate(bill["items"], 1):
        print(f"{number}. {item['name']} {format_money(item['price'])}")
    choice = input("Which number? ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(bill["items"]):
        raise ValueError("pick a number from the list")
    print(f"Removed {bill['items'].pop(int(choice) - 1)['name']}.")


def show_split(bill):
    if not bill["items"]:
        raise ValueError("add some items first")
    owed = calculate_owed(bill["people"], bill["items"])
    print()
    for name in bill["people"]:
        print(f"{name:20} {format_money(owed[name]):>8}")
    print(f"{'Total':20} {format_money(sum(owed.values())):>8}")


def main():
    bill = {"people": [], "items": []}
    actions = {"1": add_person, "2": remove_person, "3": add_item,
               "4": remove_item, "5": show_split}
    try:
        while True:
            print(MENU)
            choice = input("> ").strip()
            if choice == "6":
                break
            if choice not in actions:
                print("Please type a number from 1 to 6.")
                continue
            try:
                actions[choice](bill)
            except ValueError as error:
                print(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Bye!")


if __name__ == "__main__":
    main()
