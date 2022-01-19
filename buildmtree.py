#!/usr/bin/env python3

import hashlib
import sys
import math


class MerkleNode:
    def __init__(self, data, left, right, level=None):
        self.data = data
        self.left_child = left
        self.right_child = right
        self.hash = self.generate_hash()
        self.level = level

    def generate_hash(self):
        if self.data:  # is a leaf node
            return hashlib.sha256(self.data.encode('utf8')).digest()
        else:  # is an intermediate node
            left = self.left_child.hash if self.left_child else b''
            right = self.right_child.hash if self.right_child else b''
            combined_hashes = left + right
            return hashlib.sha256(combined_hashes).digest()

    def update_left_child(self, left):
        self.left_child = left
        self.hash = self.generate_hash()

    def update_right_child(self, right):
        self.right_child = right
        self.hash = self.generate_hash()


class MerkleTree:
    def __init__(self):
        self.hashes = []

    def get_root(self, hashes=None):
        return int(math.pow(2, self.get_num_layers(hashes)-1)) - 1

    def get_num_layers(self, hashes=None):
        if not hashes:
            hashes = self.hashes
        return math.floor(math.log(len(hashes), 2)) + 1

    def hash_tree(self, root=None, bound_l=None, bound_r=None):
        if root is None:
            root = self.get_root()
            self.hashes[root].level = self.get_num_layers()
            bound_l = root
            bound_r = root

        if self.hashes[root].data:
            return

        left_child = self.get_left_child(root, bound_l)
        right_child = self.get_right_child(root, bound_r)

        self.hash_tree(left_child, bound_l=min(left_child, bound_l), bound_r=min(root, bound_r))
        self.hash_tree(right_child, bound_l=max(root, bound_l), bound_r=max(right_child, bound_r))

        self.hashes[root].update_left_child(self.hashes[left_child])
        self.hashes[root].update_right_child(self.hashes[right_child])
        self.hashes[root].generate_hash()
        return

    def get_left_child(self, index, bound_l=None):
        root_level = self.get_level(index)
        if index <= self.get_root():
            level = root_level
            child = index - int(math.pow(2, level - 2))
        else:
            child = bound_l + 1 + self.get_root(self.hashes[bound_l+1:index])
        self.hashes[child].level = root_level-1
        return child

    def get_right_child(self, index, bound_r=None):
        root_level = self.get_level(index)
        if index < self.get_root():
            level = root_level
            child = index + int(math.pow(2, level - 2))
        else:
            if bound_r <= index:
                child = index + 1 + self.get_root(self.hashes[index + 1:])
            else:
                child = index + 1 + self.get_root(self.hashes[index + 1:bound_r])
        self.hashes[child].level = root_level-1
        return child

    def get_level(self, index):
        root = self.get_root()
        top = self.get_num_layers()
        if index == root:
            return self.get_num_layers()
        elif index < root:
            if index % 2 == 0:
                return 1
            else:
                level = top
                tmp = root+1
                index += 1
                while tmp != index:
                    if tmp > index:
                        tmp -= int(math.pow(2, level-2))
                    else:
                        tmp += int(math.pow(2, level-2))
                    level -= 1
                return level
        else:
            level = top
            right_level = self.get_num_layers(self.hashes[root+1:])
            effective_level = right_level+1
            effective_root = root
            while effective_root < index:
                effective_root += self.get_root(self.hashes[effective_root + 1:]) + 1
                effective_level -= 1

            if effective_root == index:
                return (level-right_level)+effective_level-1

            tmp = effective_root + 1
            index += 1
            while tmp != index:
                if tmp > index:
                    tmp -= int(math.pow(2, effective_level - 2))
                else:
                    tmp += int(math.pow(2, effective_level - 2))
                effective_level -= 1
            return (level-right_level)+effective_level-1

    def insert_data(self, data):
        if not self.hashes:
            self.hashes.append(MerkleNode(data, None, None))
            return
        new_node = MerkleNode(data, None, None)
        self.hashes.append(MerkleNode(None, None, None))
        self.hashes.append(new_node)

    def pretty_print(self):
        output = ''
        for node in self.hashes:
            data = node.data if node.data else ''
            tabs = '\t\t\t\t\t'*(node.level-1)

            if not data:
                max_len = max(len('| Hash: {}\n'.format(node.hash)),
                              len('| - Left Child: {}\n'.format(str(node.left_child.hash))),
                              len('| - Right Child: {}\n'.format(str(node.right_child.hash))))
            else:
                max_len = len('Hash: {}\n'.format(node.hash))

            output += tabs + '-'*max_len + '\n'
            output += '{}| Hash: {}\n'.format(tabs, node.hash)
            if data:
                output += '{}| - Data: {}\n'.format(tabs, data)
            else:
                output += '{}| - Left Child: {}\n'.format(tabs, str(node.left_child.hash))
                output += '{}| - Right Child: {}\n'.format(tabs, str(node.right_child.hash))
            output += '{}| - Level: {}\n'.format(tabs, node.level)
            output += tabs+'-'*max_len + '\n'
            output += '\n'
        return output

    def write_to_file(self, file='merkle.tree'):
        with open(file, 'w+') as f:
            f.write(self.pretty_print())


def main():
    args = sys.argv[1].split(', ')
    mt = MerkleTree()
    for arg in args:
        mt.insert_data(arg)
    mt.hash_tree()
    mt.write_to_file()


if __name__ == '__main__':
    main()
