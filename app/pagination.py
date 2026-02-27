from math import ceil

class Pagination:
       
    def __init__(self, total_count: int, current_page: int, limit: int):
        self.total_count = total_count
        self.limit = limit
        self.page = current_page
        self.total_pages = ceil(total_count / limit) if limit > 0 else 1

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = 0
        for num in range(1, self.total_pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.total_pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num