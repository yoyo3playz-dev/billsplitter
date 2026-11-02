# BillSplitter

A small terminal program that splits a restaurant bill between friends, even when everyone ordered different things.

## What it does

You add the people, then add each item with its price and say who shared it. When you are done, the program shows how much each person owes. Nobody has to do the math on a napkin.

An item is split evenly between the people who shared it. If you leave "shared by" empty, the item is split between everyone. You can also remove a person or an item if you made a mistake.

## How to use it

You need Python 3. The only extra package is pytest, and only for the tests.

```
python project.py
```

Then pick a number from the menu:

1. Add a person
2. Remove a person
3. Add an item
4. Remove an item
5. Split the bill
6. Quit

A normal run: add everyone, add the items, then choose 5.

To run the tests:

```
pip install -r requirements.txt
python -m pytest
```

## Files

- `project.py` has all the code.
- `test_project.py` has the pytest tests. There is a test for every function, and a few tests that run `main()` with fake typed input.
- `requirements.txt` only lists pytest.
- `README.md` is this file.

## The functions

- `parse_money` turns text like `12.50` or `$3` into cents and rejects anything that is not a normal price.
- `format_money` turns cents back into text like `12.50`.
- `find_people` matches typed names (any case, separated by commas) to the people who were added. An empty answer means everyone.
- `split_item` splits one price between a number of people so the shares add up to exactly the price.
- `calculate_owed` goes through all the items and adds up what each person owes.
- `add_person` and `remove_person` ask for a name and change the list of people. A person who is on an item can't be removed until the item is removed.
- `add_item` asks for the item name, the price and who shared it.
- `remove_item` shows the numbered items and removes the one you pick.
- `show_split` prints what each person owes, plus the total.
- `main` shows the menu, runs the choice you typed, and prints any error message instead of crashing.

## Design decisions

**Money is stored in cents.** Floats aren't exact (`0.1 + 0.2` is a good example), so I use whole numbers of cents. Text like `12.50` is converted once in `parse_money` and turned back into text when printing.

**Rounding never loses a cent.** If three people split 1.00, you can't give each 0.33 because a cent disappears. `split_item` gives everyone the rounded-down share, then hands out the leftover cents one by one. The shares always add up to the exact price. I wrote a test that makes 300 random bills and checks this every time.

**Errors are caught in one place.** The input functions raise `ValueError` with a short message and `main()` prints it, so a negative price or an unknown name never crashes the program. Ctrl+C and Ctrl+D exit nicely too.

**Commas are only for thousands.** `1,000` means one thousand, but `1,00` is rejected. Some people type a comma instead of a dot, and silently turning that into 100.00 would be a nasty surprise.

Nothing is saved to a file, so everything is lost when you quit.
