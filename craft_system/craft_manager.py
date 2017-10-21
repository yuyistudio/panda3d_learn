#encoding: utf8


class Recipe(object):
    def __init__(self, resultant, ingredients):
        """
        :param resultant:  string, eg. "stone_axe"
        :param ingredients:  string, eg. "stick 1 stone 1"
        :return:
        """
        self._resultant = resultant
        ingredients = ingredients.split()
        assert len(ingredients) % 2 == 0, 'invalid ingredients config'
        self._ingredient2count = {}
        for i in range(0, len(ingredients), 2):
            self._ingredient2count[ingredients[i]] = int(ingredients[i + 1])


class CraftManager(object):

    def __init__(self):
        self._configs = {}

    def register_recipe(self, recipe_name, ingredients, ignore_conficts=False):
        if not ignore_conficts and recipe_name in self._configs:
            raise RuntimeError("duplicated craft configuration, name `%s`" % recipe_name)
        self._configs[recipe_name] = Recipe(recipe_name, ingredients)

    def register_recipes(self, recipes, ignore_conficts=False):
        """
        :param recipes:
        eg.
            {
              "stone_axe": {
                "ingredients": "stick 1 stone 1"
              },
              "steal_axe": {
                "ingredients": "stick 1 steal 1"
              }
            }

        :return:
        """
        for item_name, item_config in recipes.iteritems():
            if not ignore_conficts and item_name in self._configs:
                raise RuntimeError("duplicated craft configuration, name `%s`" % item_name)
            try:
                ingredients = item_config['ingredients']
            except:
                raise RuntimeError("ingredients not found for recipe: %s" % item_name)
            self._configs[item_name] = Recipe(item_name, ingredients)

    def get_recipe(self, name):
        config = self._configs.get(name)
        assert config, 'cannot craft `%s` because config not found' % name
        return self._configs



