class Review:
    def __init__(self, id: int, prod_name: str, price: str, country: str, source: str, author: str, review_txt: str, rating: float, nums_of_reviews: int, bought_in_past_month: str):
        self.id = id
        self.prod_name = prod_name
        self.price = price
        self.country = country
        self.source = source
        self.author = author
        self.review_txt = review_txt
        self.rating = rating
        self.nums_of_reviews = nums_of_reviews
        self.bought_in_past_month = bought_in_past_month

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'prod_name': self.prod_name,
            'price': self.price,
            'country': self.country,
            'source': self.source,
            'author': self.author,
            'review_txt': self.review_txt,
            'rating': self.rating,
            'nums_of_reviews': self.nums_of_reviews,
            'bought_in_past_month': self.bought_in_past_month
        }
