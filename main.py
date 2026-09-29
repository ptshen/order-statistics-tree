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
            self.root = TreeNode(value=value,num_left=0)
            self.length = 1
            return
        cur = self.root
        parent = self.root
        while cur:
            if cur.value <= value:
                parent = cur
                cur = cur.right
            else:
                cur.num_left += 1
                parent = cur
                cur = cur.left
        newNode = TreeNode(value=value,num_left=0)
        if parent.value <= value:
            parent.right = newNode
        else:
            parent.left = newNode



    def p_percentile(self, p):
        pass
        


