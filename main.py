class TreeNode: 
    def __init__(self, value, left=None, right=None, num_left = 0):
        self.value = value
        self.left = None
        self.right = None
        self.num_left = num_left

class OrderStatisticsTree:
    def __init__(self):
        self.root = None
        self.length = 0

    def insert(self, value): 
        if not self.root: 
            self.root = TreeNode(value)
            return 
        else:
            pass

    def p_percentile(self, p):
        pass
        


