import math

class TreeNode: 
    def __init__(self, value, left=None, right=None, num_left = 0):
        self.value = value
        self.left = None
        self.right = None
        self.num_left = num_left # nodes strictly left (current node not inclusive)

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
        if self.root:
            if p == 1:
                k = self.length - 1
            else:
                k = math.floor(p * self.length) # interested in the kth treenode

            foo = self.root
            while foo.num_left != k:
                if foo.num_left < k: 
                    foo = foo.right
                elif foo.num_left > k:
                    foo = foo.left
            
            return foo.val
        else:
            return 

            
        

        

        


