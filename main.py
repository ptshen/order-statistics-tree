import math

class TreeNode: 
    def __init__(self, value, left=None, right=None, num_below = 1):
        self.value = value
        self.left = left
        self.right = right
        self.num_below = num_below # inclusive

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
            parent = cur
            cur.num_below += 1
            if cur.value <= value:
                cur = cur.right
            else:
                cur.num_left += 1
                cur = cur.left
        newNode = TreeNode(value=value,num_left=0)
        if parent.value <= value:
            parent.right = newNode
        else:
            parent.left = newNode
        self.length += 1


    def p_percentile(self, p): 
        pass

        

            
        

        

        


