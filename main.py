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
        pass 
        


    def p_percentile(self, p): 
        if self.length == 0:
            return None 
        
        foo = self.root
        k = math.floor(p * self.length)

        if k == 0:
            k = 1

        while k > 0:
            num_left = foo.left.num_below if foo.left else 0
            if num_left + 1 == k:
                return foo.val
            elif num_left + 1 > k: 
                foo = foo.left
            else:
                foo = foo.right
                k -= num_left + 1
        
            

            

                
                
                

            



        

            
        

        

        


