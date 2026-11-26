from parser import parse_line

def total(lines, discount=0):
    items = [parse_line(l) for l in lines]
    subtotal = sum(i["qty"] * i["price"] for i in items)
    return round(subtotal * (1 - discount / 100), 2)
