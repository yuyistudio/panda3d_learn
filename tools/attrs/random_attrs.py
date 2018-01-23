# encoding: utf8

import json
import random

attributes = eval(open('attributes.json').read())


def random_attrs():
    chosen_attrs = []
    chosen_categories = set()
    chosen_effects = set()
    chosen_factors = {}
    while len(chosen_attrs) < 3:
        attr = random.choice(attributes)

        # 判重
        category = attr['category']
        if category in chosen_categories:
            continue

        effect = attr['effect']
        if effect in chosen_effects:
            continue

        factors = attr.get("factors", {})
        for factor_name, factor_value in factors.iteritems():
            if factor_name in chosen_factors:
                continue

        exclusives = attr.get('exclusive', [])
        if any([id in chosen_categories for id in exclusives]):
            continue

        # 记录
        for id in exclusives:
            chosen_categories.add(id)
        chosen_effects.add(effect)
        chosen_categories.add(category)
        for factor_name, factor_value in factors.iteritems():
            chosen_factors[factor_name] = factor_value

        chosen_attrs.append(attr)
    return chosen_attrs


for i in range(10):
    chosen_attrs = random_attrs()
    factors = {}
    for attr in chosen_attrs:
        factors.update(attr.get('factors', {}))
        print attr['id']  #, '\n\t', attr['effect'], attr['detailed_desc']
    for k, v in factors.iteritems():
        print '\t', k, v
    print
