def binary_search_instance(x: int, y: int) -> int:
    x %= y 

    low, high = 1, y
    mid = (low + high) // 2
    for i in range(1, x + 1):
        mid = (low + high) // 2
        if mid < x:
            low = mid + 1
        else:
            high = mid - 1
    return mid
