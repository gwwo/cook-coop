from typing import Union


class Ingredient:
    def __init__(self, value: str):
        self.value = value

    def new_one(self):
        return Ingredient(self.value)


class Dish:
    def __init__(self):
        self.content: Union[list[Ingredient], None] = None

    def new_one(self):
        return Dish()  # with empty content


class Pot:
    def __init__(self):
        self.need_cooking = 0
        self.soup: list[Ingredient] = []

    def cooking(self):
        if self.need_cooking > 0:
            self.need_cooking -= 1

    def dump(self):
        soup, reward = None, 0
        if self.need_cooking == 0 and len(self.soup) == 3:
            soup, reward = self.soup, 6
            self.soup = []
        return soup, reward

    def add(self, ingred: Ingredient):
        success, reward = False, 0
        if len(self.soup) < 3:
            self.soup.append(ingred)
            success, reward = True, 2
            # self.need_cooking += 5
        return success, reward


class Server:
    def __init__(self, can_serve_ingredient: bool):
        self.serve_ingredient = can_serve_ingredient

    def serve(self, dish: Union[Dish, Ingredient]):
        success, reward = False, 0
        if type(dish) is Ingredient and self.serve_ingredient:
            success, reward = True, 1
        elif type(dish) is Dish and dish.content != None and len(dish.content) == 3:
            success, reward = True, 10
        return success, reward


class Counter:
    def __init__(
        self,
        holding: Union[Pot, Ingredient, Dish, Server, None],
        dispense_new_one: bool = False,
    ):
        self.holding = holding
        self.dispense_new_one = dispense_new_one

    def describe_holding(self):
        if self.holding == None:
            return "empty"
        elif type(self.holding) is Ingredient:
            if self.dispense_new_one:
                return self.holding.value + "_dispenser"
            else:
                return self.holding.value
        elif type(self.holding) is Server:
            return "server"
        elif type(self.holding) is Dish:
            if self.dispense_new_one:
                return "plate_dispenser"
            else:
                if self.holding.content == None:
                    return "plate"
                else:
                    return "soup"
        elif type(self.holding) is Pot:
            num = len(self.holding.soup)
            if num == 0:
                return "pot"
            elif num == 1:
                return "pot_with_1_cooking"
            elif num == 2:
                return "pot_with_2_cooking"
            elif num == 3:
                if self.holding.need_cooking > 0:
                    return "pot_with_3_cooking"
                else:
                    return "pot_ready"
        raise ValueError("must be holding something wrong")


class Chef:
    def __init__(self):
        self.holding: Union[Ingredient, Dish, None] = None

    def describe_holding(self):
        if self.holding == None:
            return "empty"
        elif type(self.holding) is Dish:
            if self.holding.content == None:
                return "plate"
            else:
                return "soup"
        elif type(self.holding) is Ingredient:
            return self.holding.value
        raise ValueError("must be holding something wrong")

    def interact(self, counter: Counter):
        reward = 0
        if self.holding == None:
            if type(counter.holding) in [Dish, Ingredient]:
                if counter.dispense_new_one:
                    self.holding = counter.holding.new_one()
                else:
                    self.holding, counter.holding = counter.holding, None
        elif type(self.holding) is Dish:
            if counter.holding == None:
                counter.holding, self.holding = self.holding, None
            elif type(counter.holding) is Pot:
                if self.holding.content == None:
                    self.holding.content, r = counter.holding.dump()
                    reward += r
            elif type(counter.holding) is Server:
                success, r = counter.holding.serve(self.holding)
                reward += r
                if success:
                    self.holding = None
        elif type(self.holding) is Ingredient:
            if counter.holding == None:
                counter.holding, self.holding = self.holding, None
            elif type(counter.holding) is Pot:
                success, r = counter.holding.add(self.holding)
                reward += r
                if success:
                    self.holding = None
            elif type(counter.holding) is Server:
                success, r = counter.holding.serve(self.holding)
                reward += r
                if success:
                    self.holding = None
        return reward
