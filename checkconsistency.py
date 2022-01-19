#!/usr/bin/env python3

import hashlib
import sys
import math
import re


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
    def __init__(self, fromfile=None):
        self.hashes = []
        if fromfile:
            with open(fromfile, 'r') as f:
                tree = ''.join(f.readlines())
                data = re.findall('Data: .*.\n', tree)
                data = [x[6:-1] for x in data]
                for elem in data:
                    self.insert_data(elem)
                self.hash_tree()

    def get_root(self, hashes=None):
        return int(math.pow(2, self.get_num_layers(hashes)-1)) - 1

    def get_num_layers(self, hashes=None):
        if not hashes:
            hashes = self.hashes
        return math.floor(math.log(len(hashes), 2)) + 1

    def print_consistency_proof(self, data):
        root = self.get_root()
        verified_data = self.verify_data(data, root)
        if not verified_data:
            print('no')
        else:
            verified_data = verified_data[1:]
            verified_data.append(self.hashes[root].hash)
            print('yes {}'.format(verified_data))

    def verify_data(self, data, root=None, bound_l=None, bound_r=None):
        if bound_l is None or bound_r is None:
            bound_l = root
            bound_r = root

        if self.hashes[root].data:
            return [1] if self.hashes[root].data == data else []

        left_child = self.get_left_child(root, bound_l)
        right_child = self.get_right_child(root, bound_r)

        lc_data = self.verify_data(data, left_child, bound_l=min(left_child, bound_l), bound_r=min(root, bound_r))
        if len(lc_data):
            lc_data.append(self.hashes[right_child].hash)
            return lc_data

        rc_data = self.verify_data(data, right_child, bound_l=max(root, bound_l), bound_r=max(right_child, bound_r))
        if len(rc_data):
            rc_data.append(self.hashes[left_child].hash)
            return rc_data
        return []

    def print_subtree_consistency_proof(self, subtree_hash):
        root = self.get_root()
        verified_data = self.verify_subtree(subtree_hash, root)
        if not verified_data:
            print('no')
        else:
            verified_data.append(self.hashes[root].hash)
            print('yes {}'.format(verified_data))

    def verify_subtree(self, subtree_hash, root=None, bound_l=None, bound_r=None):
        if bound_l is None or bound_r is None:
            bound_l = root
            bound_r = root

        if self.hashes[root].hash == subtree_hash:
            return [subtree_hash]
        elif root % 2 == 0:
            return []

        left_child = self.get_left_child(root, bound_l)
        right_child = self.get_right_child(root, bound_r)

        lc_data = self.verify_subtree(subtree_hash, left_child, bound_l=min(left_child, bound_l), bound_r=min(root, bound_r))
        if len(lc_data):
            lc_data.append(self.hashes[right_child].hash)
            return lc_data

        rc_data = self.verify_subtree(subtree_hash, right_child, bound_l=max(root, bound_l), bound_r=max(right_child, bound_r))
        if len(rc_data):
            rc_data.append(self.hashes[left_child].hash)
            return rc_data
        return []

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
            child = bound_l + 1 + self.get_root(self.hashes[bound_l + 1:index])
        self.hashes[child].level = root_level - 1
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
        self.hashes[child].level = root_level - 1
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
                tmp = root + 1
                index += 1
                while tmp != index:
                    if tmp > index:
                        tmp -= int(math.pow(2, level - 2))
                    else:
                        tmp += int(math.pow(2, level - 2))
                    level -= 1
                return level
        else:
            level = top
            right_level = self.get_num_layers(self.hashes[root + 1:])
            effective_level = right_level + 1
            effective_root = root
            while effective_root < index:
                effective_root += self.get_root(self.hashes[effective_root + 1:]) + 1
                effective_level -= 1

            if effective_root == index:
                return (level - right_level) + effective_level - 1

            tmp = effective_root + 1
            index += 1
            while tmp != index:
                if tmp > index:
                    tmp -= int(math.pow(2, effective_level - 2))
                else:
                    tmp += int(math.pow(2, effective_level - 2))
                effective_level -= 1
            return (level - right_level) + effective_level - 1

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

    def write_to_file(self, file='merkle.trees'):
        with open(file, 'w+') as f:
            f.write('Merkle Tree #1\n\n')
            f.write(self.pretty_print())

    def append_to_file(self, file='merkle.trees'):
        with open(file, 'a') as f:
            f.write('\n\n\n')
            f.write('Merkle Tree #2\n\n')
            f.write(self.pretty_print())


def main():
    args = sys.argv[1].split(', ')
    mt = MerkleTree()
    for arg in args:
        mt.insert_data(arg)
    mt.hash_tree()
    mt.write_to_file()

    args = sys.argv[2].split(', ')
    mt1 = MerkleTree()
    for arg in args:
        mt1.insert_data(arg)
    mt1.hash_tree()
    mt1.append_to_file()

    mt1.print_subtree_consistency_proof(mt.hashes[mt.get_root()].hash)

if __name__ == '__main__':
    main()
