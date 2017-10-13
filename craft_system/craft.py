#encoding: utf8


class Recipe(object):
    def __init__(self, resultant, ingrediants):
        """
        :param resultant:  string, eg. "stone_axe"
        :param ingrediants:  string, eg. "stick 1 stone 1"
        :return:
        """
        self._resultant = resultant
        ingrediants = ingrediants.split()
        assert len(ingrediants) % 2 == 0, 'invalid ingrediants config'
        self._ingrediant2count = {}
        for i in range(0, len(ingrediants), 2):
            self._ingrediant2count[ingrediants[i]] = int(self._ingrediant2count[ingrediants[i + 1]])


class Craft(object):
    instance = None

    def __init__(self):
        Craft.instance = self
        self._configs = {}

    def register_recipe(self, recipe_name, ingrediants, ignore_conficts=False):
        if not ignore_conficts and recipe_name in self._configs:
            raise RuntimeError("duplicated craft configuration, name `%s`" % recipe_name)
        self._configs[recipe_name] = Recipe(recipe_name, ingrediants)

    def register_recipes(self, recipes, ignore_conficts=False):
        """
        :param recipes:
        eg.
            {
                "stone_axe": "stick 1 stone 1",
                "steal_axe": "stick 1 steal 1",
            }
        :return:
        """
        for item_name, item_config in recipes.iteritems():
            if not ignore_conficts and item_name in self._configs:
                raise RuntimeError("duplicated craft configuration, name `%s`" % item_name)
            self._configs[item_name] = Recipe(item_name, item_config)

    def get_recipe(self, name):
        config = self._configs.get(name)
        assert config, 'cannot craft `%s` because config not found' % name
        return self._configs



