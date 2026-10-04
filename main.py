import math

class TreeNode: 
    def __init__(self, value, left=None, right=None, num_below = 1):
        self.value = value
        self.left = left
        self.right = right
        self.num_below = num_below # inclusive of current node

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


    def p_percentile(self, p): 
        if self.length == 0:
            return None 
        
        foo = self.root
        k = math.floor(p * self.length)

        if k == 0:
            k = 1

        while k > 0:
            num_left = foo.left.val if foo.left else 0
            if num_left + 1 == k:
                return foo.val
            elif num_left + 1 > k: 
                foo = foo.left
            else:
                foo = foo.right
                k -= num_left + 1
        
            

            

                
                
                

            



        

            
        

        

        


