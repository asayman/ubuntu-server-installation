from invoice import total

LINES = ["pen,2,1.50", "book,1,10.25"]
assert total(LINES) == 13.25, total(LINES)
assert total(LINES, discount=10) == 11.93, total(LINES, discount=10)
assert total([]) == 0
print("PASS")
