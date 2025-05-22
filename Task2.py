import csv
import timeit
from BTrees.OOBTree import OOBTree


def load_data(file_path):
    items = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            item = {
                "ID": int(row["ID"]),
                "Name": row["Name"],
                "Category": row["Category"],
                "Price": float(row["Price"]),
            }
            items.append(item)
    return items


def add_item_to_tree(tree, item):
    price = item["Price"]
    if price in tree:
        tree[price].append(item)
    else:
        tree[price] = [item]


def add_item_to_dict(dictionary, item):
    dictionary[item["ID"]] = item


def range_query_tree(tree, min_price, max_price):
    result = []
    for _, items in tree.items(min_price, max_price):
        result.extend(items)
    return result


def range_query_dict(dictionary, min_price, max_price):
    return [
        item
        for item in dictionary.values()
        if min_price <= item["Price"] <= max_price
    ]


if __name__ == "__main__":
    file_path = "generated_items_data.csv"
    items = load_data(file_path)

    tree = OOBTree()
    dictionary = {}

    for item in items:
        add_item_to_tree(tree, item)
        add_item_to_dict(dictionary, item)

    min_price = 10.0
    max_price = 100.0

    tree_time = timeit.timeit(
        stmt=lambda: range_query_tree(tree, min_price, max_price), number=100
    )

    dict_time = timeit.timeit(
        stmt=lambda: range_query_dict(dictionary, min_price, max_price), number=100
    )

    print(f"Total range_query time for OOBTree: {tree_time:.6f} seconds")
    print(f"Total range_query time for Dict: {dict_time:.6f} seconds")
