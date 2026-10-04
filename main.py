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

    """
    Inserts node at correct position in binary tree. If node with value already exists, prefer the new node to be on the left. 
    """
    def insert(self, value): 
        if not self.root:
            self.root = TreeNode(value, num_below=1)
            self.length += 1
            return 
    
        foo = self.root
        while foo:
            foo.num_below += 1
            
            if value <= foo.value: 
                if not foo.left: 
                    c = TreeNode(value, num_below=1)
                    foo.left = c
                    self.length += 1
                    return 
                else: 
                    foo = foo.left
            else:
                if not foo.right: 
                    c = TreeNode(value, num_below=1)
                    foo.right = c
                    self.length += 1
                    return 
                else:
                    foo = foo.right

    """
    Returns the value of the node associated with the pth percentile in the tree.     
    """
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
                return foo.value
            elif num_left + 1 > k: 
                foo = foo.left
            else:
                foo = foo.right
                k -= num_left + 1
        
            

            

                
                
                

            



        

            
        

        

        


