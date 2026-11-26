def parse_line(line):
    name, qty, price = line.split(",")
    return {"name": name, "qty": int(qty), "price": float(price)}
