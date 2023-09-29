"""Chances de morts en cas de debordement sur hordes."""

import random, math, re
import click
import sqlite3
from collections import Counter
from itertools import repeat, chain
from typing import Iterable
from bs4 import BeautifulSoup as soup


def _generate_distribution() -> list[float]:
    distribution = [random.random() for _ in range(10)]
    distribution[0] += 0.3
    total = sum(distribution)
    distribution = [x / total for x in distribution]

    return distribution


def _nb_death(debord: int, def_perso: [int]) -> int:
    #def_perso = [17] * 23 + [13] * 4 + [10] * 7 + [16] * 5 + [9]

    return sum(_def_perso < (debord * percent)
               for _def_perso, percent in zip(
                random.choices(def_perso, k=10),
                _generate_distribution()))


def _generate_attacks(day: int, estim_min: int, estim_max: int) -> Iterable[int]:
    theorical = {
        1: [23, 31],
        2: [23, 83],
        3: [42, 125],
        4: [107, 275],
        5: [166, 381],
        6: [244, 512],
        7: [343, 670],
        8: [465, 857],
        9: [614, 1077],
        10: [791, 1331],
        11: [1000, 1622],
        12: [1242, 1953],
        13: [1521, 2326],
        14: [1838, 2744],
        15: [2197, 3209],
        16: [2600, 3724],
        17: [3049, 4291],
        18: [3547, 4913],
        19: [4096, 5592],
        20: [4699, 6332],
        21: [5359, 7133],
        22: [6078, 8000],
        23: [6859, 8934],
        24: [7704, 9938],
        25: [8615, 11015],
        26: [9596, 12167],
        27: [10648, 13396],
        28: [11775, 14706],
        29: [12978, 16098],
        30: [14261, 17576],
        31: [15625, 19141],
    }
    attack_positions = [item for sublist in sqlite3.connect("attack-mhordes.sqlite3").cursor().execute("""
            SELECT (CAST (attaque AS float) - estim_min) / (estim_max - estim_min) FROM no_fda;
            """) for item in sublist] # flatten the cursor into a simple list
    while True:
        attack = math.inf
        while attack > theorical[day][1]:
            attack_position = random.choice(attack_positions)
            attack = estim_min + (attack_position * (estim_max - estim_min))

        yield attack


def _get_debord(attack: int, hard_def: int) -> int:
    return attack - round((hard_def + random.randrange(0, 150) * 1.14))



@click.command
@click.argument("day", type=int)
#@click.argument("def_perso", type=int, required=False)
@click.argument("min_attack", type=int)
@click.argument("max_attack", type=int)
@click.argument("hard_def", type=int)
@click.argument("citizen_def", type=click.File('rb'))
def main( day: int, min_attack: int, max_attack: int, hard_def: int,
         citizen_def ) -> None:
    test_cases = 1000000
    random.seed()
    #attacks = _generate_attacks(day,min_attack, max_attack)
#    valid_attacks = (a for a in attacks if (a >= min_attack and a <= max_attack))
    def_perso = [int(re.search(r'\d+', x.get_text())[0])
                 for x in soup(citizen_def, 'html.parser').find_all(
                     "span", class_="citizen-defense")]
    results = Counter(
        _nb_death(attack - hard_def, def_perso)
        for attack, _ in zip(_generate_attacks(day,min_attack, max_attack)
                             , range(test_cases))
    )
    print(
        f"Chances de morts pour {hard_def} de défense:\n"
        + "\n".join(
            f"{key} morts: {value / test_cases * 100}%"
            for key, value in sorted(results.items())
        )
    )
