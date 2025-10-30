class Counter:
    """
    A class to keep track of the number of times the Enter key is pressed.
    Attributes:
        count_press_enter (int): Class variable that stores the count of Enter key presses.
    Methods:
        increment():
            Increments the count_press_enter by 1 and returns the updated count.
        get_count():
            Returns the current value of count_press_enter.
        reset():
            Resets count_press_enter to 0.
    *** In current implementation, this class is not used ***
    """
    count_press_enter = 0

    @staticmethod
    def increment():
        Counter.count_press_enter += 1
        return Counter.count_press_enter
    
    def get_count():
        return Counter.count_press_enter
    
    def reset():
        Counter.count_press_enter = 0