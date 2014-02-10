#!/usr/bin/python

class linkedList:
    class node:
        def __init__(self,v,n,l):
            self.next = n
            self.last = l
            self.value = v
        
        def setNext(self,node):
            self.next = node

        def setLast(self, node):
            self.last = node

        def getVal(self):
            return self.value

	def __str__(self):
            return str(self.last.value)+'<'+str(self.value)+'>'+str(self.next.value)

    def __init__(self):
        self.size = 0
        self.head = None
        self.tail = None

    def insert(self, value):
        self.size += 1
        tnode = None
        if self.head == None:
            tnode = self.node(value, None, None)
            tnode.setNext(tnode)
            tnode.setLast(tnode)
            self.head = tnode
            self.tail = tnode
        else:
            tnode = self.node(value, self.head, self.tail)
            self.head.setLast(tnode)
            self.tail.setNext(tnode)
            self.head = tnode
        return tnode

    def removeTail(self):
        oldTail = self.tail
        self.tail = oldTail.last
        self.tail.setNext(self.head)
        self.head.setLast(self.tail)
        self.size -= 1
        return oldTail

    def __str__(self):
	return 'head: '+str(self.head)+', tail: '+str(self.tail)
        

class objectCache:
    def __init__(self, size):
        self.size = size
        self.ll = linkedList()
        self.tree = {}

    def size(self):
        return self.ll.size

    def put(self, key, value):
        if key in self.tree.keys():
            self.tree[key].value =(key, value)
        else:
            self.tree[key] = self.ll.insert((key,value))
            if self.ll.size > self.size:
                tail = self.ll.removeTail()
                del self.tree[tail.getVal()[0]]
		del tail

    def get(self, key):
	if key in self.tree.keys():
            return self.tree[key].getVal()
        return None

