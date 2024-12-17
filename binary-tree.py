#!/usr/bin/env python3

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self, root):
        self.root = Node(root)

    # Function to insert a new node
    def insert(self, data):
        self._insert_recursive(self.root, data)

    def _insert_recursive(self, node, data):
        if node is None:
            return Node(data)

        if data < node.data:
            node.left = self._insert_recursive(node.left, data)
        else:
            node.right = self._insert_recursive(node.right, data)

        return node

    # Function to perform inorder traversal
    def inorder_traversal(self):
        self._inorder_recursive(self.root)

    def _inorder_recursive(self, node):
        if node:
            self._inorder_recursive(node.left)
            print(node.data, end=" ")
            self._inorder_recursive(node.right)

    # Function to perform preorder traversal
    def preorder_traversal(self):
        self._preorder_recursive(self.root)

    def _preorder_recursive(self, node):
        if node:
            print(node.data, end=" ")
            self._preorder_recursive(node.left)
            self._preorder_recursive(node.right)

    # Function to perform postorder traversal
    def postorder_traversal(self):
        self._postorder_recursive(self.root)

    def _postorder_recursive(self, node):
        if node:
            self._postorder_recursive(node.left)
            self._postorder_recursive(node.right)
            print(node.data, end=" ")

    # Function to search for a node
    def search(self, data):
        return self._search_recursive(self.root, data)

    def _search_recursive(self, node, data):
        if node is None:
            return False

        if node.data == data:
            return True

        if data < node.data:
            return self._search_recursive(node.left, data)
        else:
            return self._search_recursive(node.right, data)

    # Function to find the minimum value in the tree
    def find_min(self):
        current = self.root
        while current.left:
            current = current.left
        return current.data

    # Function to find the maximum value in the tree
    def find_max(self):
        current = self.root
        while current.right:
            current = current.right
        return current.data

    # Function to delete a node
    def delete(self, data):
        self.root = self._delete_recursive(self.root, data)

    def _delete_recursive(self, node, data):
        if node is None:
            return node

        if data < node.data:
            node.left = self._delete_recursive(node.left, data)
        elif data > node.data:
            node.right = self._delete_recursive(node.right, data)
        else:
            # Node with one or no child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: Get the inorder successor (smallest
            # in the right subtree)
            temp = node.right  # Start from the right child
            while temp.left:
              temp = temp.left
            node.data = temp.data
            node.right = self._delete_recursive(node.right, temp.data)

        return node

tree = BinaryTree(10)
tree.insert(5)
tree.insert(15)
tree.insert(3)
tree.insert(7)
tree.insert(13)
tree.insert(18)

print("Inorder Traversal:")
tree.inorder_traversal()
print("\nPreorder Traversal:")
tree.preorder_traversal()
print("\nPostorder Traversal:")
tree.postorder_traversal()
print("\nSearch for 7:", tree.search(7))
print("Minimum value:", tree.find_min())
print("Maximum value:", tree.find_max())
tree.delete(10)
print("\nInorder Traversal after deletion:")
tree.inorder_traversal()
