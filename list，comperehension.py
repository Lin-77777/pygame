L = []

for i in range(10):
    L.append(i)
print(L)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]

# 使用 list comprehension
L = [
    i for i in range(10)
]  # for 的結果會在前面因此直接在[]中使用i再用中括號包起來即可append到L中
print(L)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]

# 使用 list comprehension加條件判斷
L = [i for i in range(10) if i % 2 == 0]

"""
if 的結果會在後面因此直接在[]中使用i再用中括號包起來即可append到L中
，if在後面是因為有其他在前面的函式了
"""
print(L)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
