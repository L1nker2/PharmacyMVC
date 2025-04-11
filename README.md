# readme
я переписал большую(весь по сути) часть кода заново, 
осталось настроить оставшиеся тесты и подправить контроллеры чтобы тесты проходили

# How run this?
1. Пускаем сервер MySql на `localhost:3306`
2. Создаем базу данных "apteka"
3. Создаем пользователя БД с логином python и паролем python, пользователя, название БД и адрес сервера можно поменять в строке подключения расположенной в `models/base.py`
4. Выполняем SQL скрипты из папки `sqripts` , чтобы создать таблицы необходимые для работы
5. Устанавливаем зависимости через `pip3 install -r requirements.txt`
6. Запускаем `main.py`


# ToDo
- [x] - ~~Модели таблиц~~
- [x] - ~~Контроллеры для управления моделями 5/5~~
- [ ] - Представления для вывода моделей 1.5/5
- [x] - ~~Тесты контроллеров 5/5~~








# Требования
Система должна обеспечивать выполнение следующих функций:
-	добавление новых товаров: возможность занесения в базу данных информации о новых медикаментах, включая название, состав, производитель, цену, срок годности и способ применения;
-	удаление товаров: возможность удаления информации о медикаментах, которые больше не продаются или срок годности которых истек;
-	редактирование информации о товарах: изменение данных о медикаментах, таких как цена, наличие, производитель и форма выпуска;
-	поиск товаров: поиск медикаментов по названию, категории, цене, производителю и сроку годности;
-	управление продажами: оформление продаж, создание чеков и регистрация транзакций;
-	учет клиентов: хранение информации о покупателях, включая их историю покупок и возможные скидки или бонусы;
-	автоматизация складского учета: контроль остатков медикаментов, анализ сроков годности и автоматическое формирование заказов у поставщиков.
Должны быть отражены сведения о следующих атрибутах предметной области:
-	категория медикаментов;
-	клиенты (личный кабинет);
-	товары (медикаменты);
-	сотрудники аптеки;
-	продажи (акты реализации лекарств);
-	складской учет (остатки, поставки).







# Notes
Удаляем клиентов
в сотрудников добавляем роль
добавляем таблицу с поставкой для пополнения склада


заходит на форму -> делает список с количеством и заказывает 
-> через время товар падает на остатки
[1-10;]


создавал поставку -> выбирал несколько препаратов
-> создаются несколько записей в промежуточной таблице
со связью айди поставки и айди препарата с количеством

для выборки нужно будет получить айди поставки
из промежуточной таблицы получить все записи указывающие на эту поставку
получить все препараты и их количество из этой таблицы