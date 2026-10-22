class DivideAndConquer:
    def __init__(self):
        self.operation_count = 0

    def merge_sort(self, items: list, key=lambda x: x, reverse: bool = False) -> list:
        """
        Merge Sort estable. Divide la lista a la mitad, ordena cada mitad y combina.
        T(n) = 2T(n/2) + O(n) = O(n log n)
        """
        self.operation_count = 0

        def sort(part):
            if len(part) <= 1:
                return part
            mid = len(part) // 2
            return merge(sort(part[:mid]), sort(part[mid:]))

        def merge(left, right):
            merged, i, j = [], 0, 0
            while i < len(left) and j < len(right):
                self.operation_count += 1
                a, b = key(left[i]), key(right[j])
                # Con '<=' / '>=' se toma primero el de la izquierda en empates (estabilidad)
                if (a >= b) if reverse else (a <= b):
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
            return merged

        return sort(list(items))

    def lower_bound(self, items: list, target, key=lambda x: x, left: int = 0, right: int = None) -> int:
        """Primer índice con key(item) >= target en una lista ordenada ascendente (D&C: O(log n))."""
        if right is None:
            right = len(items)
        if left >= right:
            return left
        self.operation_count += 1
        mid = (left + right) // 2
        if key(items[mid]) < target:
            return self.lower_bound(items, target, key, mid + 1, right)
        return self.lower_bound(items, target, key, left, mid)

    def upper_bound(self, items: list, target, key=lambda x: x, left: int = 0, right: int = None) -> int:
        """Primer índice con key(item) > target en una lista ordenada ascendente."""
        if right is None:
            right = len(items)
        if left >= right:
            return left
        self.operation_count += 1
        mid = (left + right) // 2
        if key(items[mid]) <= target:
            return self.upper_bound(items, target, key, mid + 1, right)
        return self.upper_bound(items, target, key, left, mid)

    def range_query(self, sorted_items: list, low, high, key=lambda x: x) -> list:
        """Elementos con low <= key <= high en una lista ordenada ascendente: O(log n + m)."""
        start = self.lower_bound(sorted_items, low, key)
        end = self.upper_bound(sorted_items, high, key)
        return sorted_items[start:end]
