class SpeedClickHandler:
    def __init__(self) -> None:
        self.n_clicks_5 = 0
        self.n_clicks_1 = 0
        self.n_clicks_2 = 0
    
    def speed_click_handler(self, n_clicks_5, n_clicks_1, n_clicks_2):
        if self.n_clicks_5 != n_clicks_5:
            self.n_clicks_5 = n_clicks_5
            return 2000
        if self.n_clicks_1 != n_clicks_1:
            self.n_clicks_1 = n_clicks_1
            return 1000
        if self.n_clicks_2 != n_clicks_2:
            self.n_clicks_2 = n_clicks_2
            return 500

speed_click_handler = SpeedClickHandler()