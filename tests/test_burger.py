import pytest
from unittest.mock import Mock
from praktikum.bun import Bun
from praktikum.ingredient import Ingredient
from praktikum.burger import Burger
from praktikum.ingredient_types import *


class TestBurger:

    # Проверяем, что новый объект Burger создается в "чистом" состоянии:
    # - булочка  изначально отсутствует (None)
    # - список ингредиентов пуст
    def test_initial_state(self, burger):
        burger = Burger()
        assert burger.bun is None
        assert burger.ingredients == []
    
    # Добавляем в "чистый" бургер булку и ингредиент,
    # проверяем новое состояние :
    # у бургера теперь есть булка и пополнился список ингредиентов
    def test_burger_with_bun_and_ingredient_state(self):
        mock_bun = Mock()
        mock_ingredient = Mock()
        bun = mock_bun('black bun', 100.0)
        ingredient = mock_ingredient(INGREDIENT_TYPE_SAUCE, 'hot sauce', 100.0)
        burger = Burger()
        burger.set_buns(bun)
        burger.add_ingredient(ingredient)
        assert burger.bun == bun
        assert len(burger.ingredients) == 1
        assert burger.ingredients[0] == ingredient

    # Проверяем корректность установки булки методом set_buns
    # Используем моковый объект mock_bun для изоляции теста
    def test_set_buns(self, burger, mock_bun):
        burger.set_buns(mock_bun)
        assert burger.bun == mock_bun

    # Проверяем добавление ингредиента в список ingredients
    # Создаем мок-ингредиент и убеждаемся, что он добавлен в burger
    def test_add_ingredient(self, burger, mock_ingredient):
        ingredient = mock_ingredient("TOPPING", "Pepperoni", 50.0)
        burger.add_ingredient(ingredient)
        assert ingredient in burger.ingredients

    # Тестируем удаление ингредиента по индексу (0 - первый элемент, -1 - последний)
    # Параметризация позволяет проверить оба сценария
    @pytest.mark.parametrize("index", [0, -1])
    def test_remove_ingredient(self, burger, mock_ingredient, index):
        ingredient = mock_ingredient("SAUCE", "Barbecue", 30.0)
        burger.add_ingredient(ingredient)
        burger.remove_ingredient(index)
        assert len(burger.ingredients) == 0

    # Проверяем перемещение ингредиента в списке ingredients
    # Тестируем следующие сценарии:
    #   - перемещение первого элемента на вторую позицию
    #   - перемещение второго элемента на первую позицию
    #   - попытка перемещения на ту же позицию (без изменений)
    @pytest.mark.parametrize(
        "start_index, new_index",
        [(0, 1), (1, 0), (0, 0)]
    )
    def test_move_ingredient(self, burger, mock_ingredient, start_index, new_index):
        ingredient1 = mock_ingredient("TOPPING", "Pepperoni", 50.0)
        ingredient2 = mock_ingredient("SAUCE", "Barbecue", 30.0)
        burger.add_ingredient(ingredient1)
        burger.add_ingredient(ingredient2)

        # Запоминаем исходные имена для сравнения
        original_names = [ingredient1.get_name(), ingredient2.get_name()]

        burger.move_ingredient(start_index, new_index)

        current_names = [ing.get_name() for ing in burger.ingredients]

        # Формируем ожидаемый порядок:
        # - удаляем элемент по start_index
        # - вставляем его на позицию new_index
        expected_names = original_names.copy()
        expected_names.insert(new_index, expected_names.pop(start_index))

        assert current_names == expected_names

    # Проверяем расчет итоговой цены бургера
    # С помощью параметризации тестируем 3 сценрария:
    #   1. Булочка за 100 + ингредиентов нет = итого 200 космических рублей
    #   2. Булочка за 150 + 1 ингредиент за 50 = 350
    #   3. Булочка за 100 + 2 ингредиента (50 и 30) = 280
    @pytest.mark.parametrize(
        "bun_price, ingredient_prices, expected_price",
        [
            (100.0, [], 200.0),
            (150.0, [50.0], 350.0),
            (100.0, [50.0, 30.0], 280.0),
        ]
    )
    def test_get_price(self, burger, mock_bun, mock_ingredient, bun_price, ingredient_prices, expected_price):
        mock_bun.get_price.return_value = bun_price
        burger.set_buns(mock_bun)

        for i, price in enumerate(ingredient_prices):
            ingredient = mock_ingredient(f"TYPE_{i}", f"Ingredient_{i}", price)
            burger.add_ingredient(ingredient)

        assert burger.get_price() == expected_price

    # Проверяем форматирование чека для бургера с ингредиентами
    # Ожидаем строку, которая содержит:
    # - верхнюю и нижнюю булку
    # - добавленный ингредиент
    # - итоговую цену (200 за булку + 50 за ингредиент)
    def test_get_receipt(self, burger, mock_bun, mock_ingredient):
        burger.set_buns(mock_bun)
        ingredient = mock_ingredient("TOPPING", "Pepperoni", 50.0)
        burger.add_ingredient(ingredient)

        receipt = burger.get_receipt()
        expected_lines = [
            '(==== Black Bun ====)',
            '= topping Pepperoni =',
            '(==== Black Bun ====)\n',
            f'Price: {200.0 + 50.0}'
        ]
        expected_receipt = '\n'.join(expected_lines)

        assert receipt == expected_receipt

    # Проверяем форматирование чека для бургера без ингредиентов
    # Ожидаем, что в чеке будут только две булки и цена 200.0
    def test_get_receipt_no_ingredients(self, burger, mock_bun):
        burger.set_buns(mock_bun)
        receipt = burger.get_receipt()
        expected_lines = [
            '(==== Black Bun ====)',
            '(==== Black Bun ====)\n',
            'Price: 200.0'
        ]
        expected_receipt = '\n'.join(expected_lines)
        assert receipt == expected_receipt