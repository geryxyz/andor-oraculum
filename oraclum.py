import typing

letter_mapping = {
    'cs': 'C',
    'dz': 'D',
    'dzs': 'Đ',
    'gy': 'G',
    'ly': 'L',
    'ny': 'N',
    'sz': 'S',
    'ty': 'T',
    'zs': 'Z',
    'í': 'i',
    'ó': 'o',
    'ú': 'u',
    'ő': 'ö',
    'ű': 'ő'
}


def mono_lettering(text: str) -> str:
    result = text
    for original, token in sorted(letter_mapping.items(), key=lambda item: len(item[0]), reverse=True):
        result = result.replace(original, token)
    return result


# (place, manner, voicing)
consonant = {
    'm': (0, 0, 1),
    'n': (1, 0, 1),

    'p': (0, 1, 0),
    'b': (0, 1, 1),
    't': (1, 1, 0),
    'd': (1, 1, 1),
    'T': (3, 1, 0),
    'G': (3, 1, 1),
    'k': (4, 1, 0),
    'g': (4, 1, 1),

    'c': (1, 2, 0),
    'D': (1, 2, 1),
    'C': (2, 2, 0),
    'Đ': (2, 2, 1),

    'f': (0, 3, 0),
    'v': (0, 3, 1),
    'S': (1, 3, 0),
    'z': (1, 3, 1),
    's': (2, 3, 0),
    'Z': (2, 3, 1),
    'h': (5, 3, 0),

    'r': (1, 4, 1),

    'l': (1, 5, 1),
    'j': (3, 5, 1)
}

# (place, openness, rounded)
vowel = {
    'i': (0, 0, 0),
    'ü': (0, 0, 1),
    'u': (2, 0, 1),

    'é': (0, 1, 0),
    'ö': (0, 1, 1),
    'o': (2, 1, 1),

    'e': (0, 2, 0),

    'á': (1, 3, 0),
    'a': (2, 3, 1)
}


def sound_distance(letter_a: str, letter_b: str) -> typing.Union[None, float]:
    if letter_a in consonant and letter_b in consonant:
        return sum([(a - b) ** 2 for a, b in zip(consonant[letter_a], consonant[letter_b])]) ** (1/2)
    elif letter_a in vowel and letter_b in vowel:
        return sum([(a - b) ** 2 for a, b in zip(vowel[letter_a], vowel[letter_b])]) ** (1/2)
    else:
        return None


def alike(text_a: str, text_b: str, offset_gamma: float = 1, verbose: bool = False) -> typing.Tuple[float, float]:
    corrected_a = mono_lettering(text_a.lower())
    corrected_b = mono_lettering(text_b.lower())
    shortest_length = min(len(corrected_a), len(corrected_b))
    all_sound_distance_for_adjusted = [sound_distance(a, b) for a in corrected_a for b in corrected_b]
    all_valid_distance_for_adjusted = [item for item in all_sound_distance_for_adjusted if item is not None]
    if all_valid_distance_for_adjusted:
        max_sound_distance_for_adjusted = max(all_valid_distance_for_adjusted)
    else:
        max_sound_distance_for_adjusted = 0
    all_sound_distance_for_nonadjusted = [sound_distance(corrected_a[i], corrected_b[i]) for i in range(shortest_length)]
    all_valid_distance_for_nonadjusted = [item for item in all_sound_distance_for_nonadjusted if item is not None]
    if all_valid_distance_for_nonadjusted:
        max_sound_distance_for_nonadjusted = max(all_valid_distance_for_nonadjusted)
    else:
        max_sound_distance_for_nonadjusted = 0
    adjusted_score = 0
    score = 0
    if verbose:
        print('   ' + ' '.join([f'        {b}        ' for b in corrected_b]))
    for index_a, letter_a in enumerate(corrected_a):
        if verbose:
            print(f"{letter_a} ", end=' ')
        for index_b, letter_b in enumerate(corrected_b):
            norm_offset = 1 - (abs(index_a - index_b) / max(len(corrected_a), len(corrected_b))) ** offset_gamma
            letter_distance = sound_distance(letter_a, letter_b)
            norm_letter_distance_adjusted = 0
            norm_letter_distance = 0
            if letter_distance is not None:
                norm_letter_distance_adjusted = 1
                if max_sound_distance_for_adjusted != 0:
                    norm_letter_distance_adjusted = 1 - letter_distance / max_sound_distance_for_adjusted
                norm_letter_distance = 1
                if max_sound_distance_for_nonadjusted != 0:
                    norm_letter_distance = 1 - letter_distance / max_sound_distance_for_nonadjusted
            adjusted_score += (norm_offset * norm_letter_distance_adjusted) / max(len(corrected_a), len(corrected_b))
            if index_a == index_b:
                score += norm_letter_distance
            if verbose:
                print(f"{norm_letter_distance:.3f},{norm_letter_distance_adjusted:.3f}@{norm_offset:.3f}", end=' ')
        if verbose:
            print()
    return adjusted_score, score


male_names = []
with open('osszesffi.txt', 'r', encoding='utf-8') as name_file:
    next(name_file)
    for line in name_file:
        male_names.append(line.strip())
female_names = []
with open('osszesnoi.txt', 'r', encoding='utf-8') as name_file:
    next(name_file)
    for line in name_file:
        female_names.append(line.strip())

top_n = 10

if __name__ == '__main__':
    liked_names = [
        'Domonkos',
        'Máté',
        'Samu',
        'Péter',
        'Kornél',
        'Vince',
        'Anna',
        'Edit'
    ]

    for liked in liked_names:
        print("+" + '-' * len(liked) + "+")
        print(f"|{liked}| inspected name")
        print("+" + '-' * len(liked) + "+")
        print()
        print("ranked by score:")
        print("----------------")
        ranked_names = sorted({name: alike(liked, name) for name in male_names}.items(), key=lambda item: item[1][1], reverse=True)
        max_score_nonadjusted = max(ranked_names, key=lambda item: item[1][1])[1][1]
        max_score_adjusted = max(ranked_names, key=lambda item: item[1][0])[1][0]
        name: str
        for name, (adjusted_score, score) in ranked_names[:top_n]:
            print(f"{name.ljust(15)} score = {score/max_score_nonadjusted:.2f} (adjusted score = {adjusted_score/max_score_adjusted:.2f})")
        print()
        print("ranked by adjusted score:")
        print("-------------------------")
        ranked_names = sorted({name: alike(liked, name) for name in male_names}.items(), key=lambda item: item[1][0], reverse=True)
        for name, (adjusted_score, score) in ranked_names[:top_n]:
            print(f"{name.ljust(15)} adjusted score = {adjusted_score/max_score_adjusted:.2f} (score = {score/max_score_nonadjusted:.2f})")
        print()

    for liked in liked_names:
        print("+" + '-' * len(liked) + "+")
        print(f"|{liked}| inspected name")
        print("+" + '-' * len(liked) + "+")
        print()
        print("ranked by score:")
        print("----------------")
        ranked_names = sorted({name: alike(liked, name) for name in female_names}.items(), key=lambda item: item[1][1], reverse=True)
        max_score_nonadjusted = max(ranked_names, key=lambda item: item[1][1])[1][1]
        max_score_adjusted = max(ranked_names, key=lambda item: item[1][0])[1][0]
        name: str
        for name, (adjusted_score, score) in ranked_names[:top_n]:
            print(f"{name.ljust(15)} score = {score/max_score_nonadjusted:.2f} (adjusted score = {adjusted_score/max_score_adjusted:.2f})")
        print()
        print("ranked by adjusted score:")
        print("-------------------------")
        ranked_names = sorted({name: alike(liked, name) for name in female_names}.items(), key=lambda item: item[1][0], reverse=True)
        for name, (adjusted_score, score) in ranked_names[:top_n]:
            print(f"{name.ljust(15)} adjusted score = {adjusted_score/max_score_adjusted:.2f} (score = {score/max_score_nonadjusted:.2f})")
        print()
