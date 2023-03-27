from data_visualization.visconfig import ConfigAndShared
order_df = ConfigAndShared.ORDER_DF

class OrderTimeQuery:
    def __init__(self):
        self.move_to_create_time_click = 0
        self.move_to_assigned_time_click = 0 
        self.move_to_meal_finished_time_click = 0 
        self.move_to_picked_up_time_click = 0 
        self.move_to_finished_time_click = 0 

    def move_to_create(self, order_id, n_clicks, val):
        if order_id and n_clicks != self.move_to_create_time_click:
            self.move_to_create_time_click = n_clicks
            return order_df.loc[order_df['id']==int(order_id)]['created_time'].item()/30
        else:
            return val
    
    def move_to_assigned(self, order_id, n_clicks, val):
        if order_id and n_clicks != self.move_to_assigned_time_click:
            self.move_to_assigned_time_click = n_clicks
            return order_df.loc[order_df['id']==int(order_id)]['assigned_time'].item()/30
        else:
            return val

    def move_to_meal_finished_time(self, order_id, n_clicks, val):
        if order_id and n_clicks != self.move_to_meal_finished_time_click:
            self.move_to_meal_finished_time_click = n_clicks
            return order_df.loc[order_df['id']==int(order_id)]['meal_finished_time'].item()/30
        else:
            return val

    def move_to_picked_up(self, order_id, n_clicks, val):
        if order_id and n_clicks != self.move_to_picked_up_time_click:
            self.move_to_picked_up_time_click = n_clicks
            return order_df.loc[order_df['id']==int(order_id)]['picked_up_time'].item()/30
        else:
            return val

    def move_to_finished(self, order_id, n_clicks, val):
        if order_id and n_clicks != self.move_to_finished_time_click:
            self.move_to_finished_time_click = n_clicks
            return order_df.loc[order_df['id']==int(order_id)]['finished_time'].item()/30
        else:
            return val

order_time_query = OrderTimeQuery()