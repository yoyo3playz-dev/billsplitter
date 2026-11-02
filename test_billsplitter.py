import random

import pytest

import project
from project import (
    add_item,
    add_person,
    calculate_owed,
    find_people,
    format_money,
    parse_money,
    remove_item,
    remove_person,
    show_split,
    split_item,
)


def feed(monkeypatch, lines):
    answers = iter(lines)

    def fake_input(prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)


def run(monkeypatch, capsys, lines):
    feed(monkeypatch, lines)
    project.main()
    return capsys.readouterr().out


def test_parse_money():
    assert parse_money("12.50") == 1250
    assert parse_money("$3") == 300
    assert parse_money(" 1,000.05 ") == 100005
    assert parse_money(".5") == 50


@pytest.mark.parametrize("bad", ["", "abc", "-5", "0", "1.234", "nan", "1e3",
                                 "5 5", "99999999999", "1,00", "1,2,3", "$$5"])
def test_parse_money_bad(bad):
    with pytest.raises(ValueError):
        parse_money(bad)


def test_format_money():
    assert format_money(1250) == "12.50"
    assert format_money(5) == "0.05"
    assert format_money(0) == "0.00"


def test_find_people():
    people = ["Ann", "Bob", "Cy"]
    assert find_people("", people) == people
    assert find_people("bob, ANN", people) == ["Bob", "Ann"]
    assert find_people("Ann, ann", people) == ["Ann"]
    with pytest.raises(ValueError):
        find_people("Dave", people)


def test_split_item():
    assert split_item(1000, 2) == [500, 500]
    assert split_item(100, 3) == [34, 33, 33]
    assert split_item(5, 1) == [5]


def test_calculate_owed():
    items = [
        {"name": "Pizza", "price": 3000, "shared_by": ["Ann", "Bob", "Cy"]},
        {"name": "Salad", "price": 900, "shared_by": ["Ann", "Bob"]},
    ]
    owed = calculate_owed(["Ann", "Bob", "Cy"], items)
    assert owed == {"Ann": 1450, "Bob": 1450, "Cy": 1000}


def test_person_with_no_items_owes_nothing():
    items = [{"name": "X", "price": 500, "shared_by": ["A"]}]
    assert calculate_owed(["A", "B"], items) == {"A": 500, "B": 0}


def test_random_bills_never_lose_a_cent():
    rng = random.Random(1)
    for _ in range(300):
        people = [f"P{i}" for i in range(rng.randint(1, 6))]
        items = [{"name": "x", "price": rng.randint(1, 9000),
                  "shared_by": rng.sample(people, rng.randint(1, len(people)))}
                 for _ in range(rng.randint(1, 6))]
        owed = calculate_owed(people, items)
        assert sum(owed.values()) == sum(i["price"] for i in items)


def test_add_person(monkeypatch):
    bill = {"people": ["Ann", "Bob"], "items": []}
    feed(monkeypatch, ["  Cy   Lee "])
    add_person(bill)
    assert bill["people"] == ["Ann", "Bob", "Cy Lee"]
    for bad in ("", "ann", "a,b", "x" * 21):
        feed(monkeypatch, [bad])
        with pytest.raises(ValueError):
            add_person(bill)


def test_remove_person(monkeypatch):
    bill = {"people": ["Ann", "Bob"],
            "items": [{"name": "Tea", "price": 400, "shared_by": ["Ann"]}]}
    feed(monkeypatch, ["bob"])
    remove_person(bill)
    assert bill["people"] == ["Ann"]
    feed(monkeypatch, ["Ann"])
    with pytest.raises(ValueError):
        remove_person(bill)
    feed(monkeypatch, ["Zed"])
    with pytest.raises(ValueError):
        remove_person(bill)


def test_add_item(monkeypatch):
    bill = {"people": ["Ann", "Bob"], "items": []}
    feed(monkeypatch, ["Tea", "4.50", "ann"])
    add_item(bill)
    assert bill["items"] == [{"name": "Tea", "price": 450, "shared_by": ["Ann"]}]
    feed(monkeypatch, ["Soup", "6", ""])
    add_item(bill)
    assert bill["items"][1]["shared_by"] == ["Ann", "Bob"]
    feed(monkeypatch, ["", "5", ""])
    with pytest.raises(ValueError):
        add_item(bill)
    with pytest.raises(ValueError):
        add_item({"people": [], "items": []})


def test_remove_item(monkeypatch):
    bill = {"people": ["Ann"], "items": [
        {"name": "Tea", "price": 400, "shared_by": ["Ann"]},
        {"name": "Soup", "price": 600, "shared_by": ["Ann"]},
    ]}
    feed(monkeypatch, ["2"])
    remove_item(bill)
    assert [item["name"] for item in bill["items"]] == ["Tea"]
    for bad in ("x", "0", "5"):
        feed(monkeypatch, [bad])
        with pytest.raises(ValueError):
            remove_item(bill)
    bill["items"].clear()
    with pytest.raises(ValueError):
        remove_item(bill)


def test_show_split(capsys):
    bill = {"people": ["Ann", "Bob"], "items": [
        {"name": "Tea", "price": 501, "shared_by": ["Ann", "Bob"]},
    ]}
    show_split(bill)
    lines = [line.split() for line in capsys.readouterr().out.splitlines()]
    assert ["Ann", "2.51"] in lines
    assert ["Bob", "2.50"] in lines
    assert ["Total", "5.01"] in lines
    with pytest.raises(ValueError):
        show_split({"people": ["Ann"], "items": []})


def test_main_full_run(monkeypatch, capsys):
    out = run(monkeypatch, capsys, [
        "1", "Ann", "1", "Bob", "1", "Cy",
        "3", "Pizza", "30", "",
        "3", "Salad", "9", "ann, bob",
        "5", "6",
    ])
    lines = [line.split() for line in out.splitlines()]
    assert ["Ann", "14.50"] in lines
    assert ["Bob", "14.50"] in lines
    assert ["Cy", "10.00"] in lines
    assert ["Total", "39.00"] in lines
    assert "Bye!" in out


def test_main_bad_input_does_not_crash(monkeypatch, capsys):
    out = run(monkeypatch, capsys, [
        "banana",
        "3",
        "1", "Ann", "1", "ann",
        "1", "a,b",
        "3", "Soup", "abc",
        "3", "Soup", "5", "Zed",
        "4",
        "5",
        "6",
    ])
    for text in ("from 1 to 6", "add some people first", "already added",
                 "no commas", "enter an amount", "don't know 'Zed'",
                 "there are no items", "add some items first"):
        assert text in out


def test_main_remove_person_and_item(monkeypatch, capsys):
    out = run(monkeypatch, capsys, [
        "1", "Ann", "1", "Bob", "3", "Tea", "4", "ann",
        "2", "Ann",
        "4", "9",
        "4", "1",
        "2", "Ann",
        "6",
    ])
    assert "remove those items first" in out
    assert "pick a number" in out
    assert "Removed Tea." in out
    assert "Removed Ann." in out


def test_main_ends_cleanly_on_eof(monkeypatch, capsys):
    assert "Bye!" in run(monkeypatch, capsys, ["1"])
