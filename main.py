from datetime import datetime
from random import *


class BTree:
    class Node:
        def __init__(self):
            self.child = []
            self.keys = []

        def __repr__(self):
            return 'Node' + str(self.keys) + str(self.child)

        def _lower_bound(self, key):
            b = 0
            e = len(self.child) - 1
            while b < e:
                mid = (b + e + 1) // 2
                if mid == 0:
                    pass
                elif self.keys[mid - 1] <= key:
                    b = mid
                else:
                    e = mid - 1
            return b

    def __init__(self, t):
        self.root = self.Node()
        self.t = t

    def _inorder(self, current):
        if current is None:
            return

        for i, son in enumerate(current.child):
            if i > 0:
                yield current.keys[i - 1]
            yield from self._inorder(son)

    def inorder(self):
        yield from self._inorder(self.root)

    def _preorder(self, current):
        if current is None:
            return
        for key in current.keys:
            yield key
        for son in current.child:
            yield from self._preorder(son)

    def preorder(self):
        yield from self._preorder(self.root)

    def _split(self, node, parnode, position):
        if parnode is None:
            self.root = self.Node()
            left = self.Node()
            right = self.Node()

            left.keys = node.keys[:self.t - 1]
            right.keys = node.keys[self.t:]
            left.child = node.child[:self.t]
            right.child = node.child[self.t:]

            self.root.keys = [node.keys[self.t - 1]]
            self.root.child = [left, right]
            return self.root
        else:
            left = self.Node()
            right = self.Node()

            left.keys = node.keys[:self.t - 1]
            right.keys = node.keys[self.t:]
            left.child = node.child[:self.t]
            right.child = node.child[self.t:]

            parnode.keys = parnode.keys[:position] + [node.keys[self.t - 1]] + parnode.keys[position:]
            parnode.child = parnode.child[:position] + [left, right] + parnode.child[position + 1:]

    def _insert(self, key, node, parnode):
        if node is None:
            return None

        if len(node.keys) == 2 * self.t - 1:
            assert node == self.root
            node = self._split(node, parnode, -1)
            assert len(node.keys) == 1

            if node.keys[0] <= key:
                self._insert(key, node.child[1], node)
            else:
                self._insert(key, node.child[0], node)

            return

        if len(node.child) == 0:
            assert node == self.root
            node.child.append(None)
            node.keys.append(key)
            node.child.append(None)

            return

        position = node._lower_bound(key)

        if node.child[position] is None:
            node.keys = node.keys[:position] + [key] + node.keys[position:]
            node.child.append(None)
        else:

            if node.child[position] is not None and len(node.child[position].keys) == 2 * self.t - 1:
                self._split(node.child[position], node, position)

                if node.keys[position] <= key:
                    self._insert(key, node.child[position + 1], node)
                else:
                    self._insert(key, node.child[position], node)
            else:
                self._insert(key, node.child[position], node)

    def insert(self, key):
        self._insert(key, self.root, None)

    def _find(self, key, node):
        if node is None or len(node.child) == 0:
            return None

        position = node._lower_bound(key)

        if position >= 1 and node.keys[position - 1] == key:
            return node.keys[position - 1]
        else:
            return self._find(key, node.child[position])

    def find(self, key):
        return self._find(key, self.root)

    def _find_predecessor(self, key, node):
        if node.child[0] is None:
            return node.keys[-1]
        else:
            return self._find_predecessor(key, node.child[-1])

    def _find_succesor(self, key, node):
        if node.child[0] is None:
            return node.keys[0]
        else:
            return self._find_succesor(key, node.child[0])

    def _delete_key_leaf(self, key, node, position):
        assert node == self.root or len(node.child) >= self.t

        assert node.keys[position] == key

        node.keys = node.keys[:position] + node.keys[position + 1:]
        node.child.pop()

    def _merge_children_around_key(self, key, node, position):
        assert 0 <= position < len(node.child) - 1

        value = self.Node()
        value.child = node.child[position].child + node.child[position + 1].child
        value.keys = node.child[position].keys + [node.keys[position]] + node.child[position + 1].keys

        node.keys = node.keys[:position] + node.keys[position + 1:]
        node.child = node.child[:position] + [value] + node.child[position + 2:]

    def _move_node_from_left_child(self, node, position):
        assert position > 0 and len(node.child[position - 1].keys) >= self.t

        node.child[position].keys = [node.keys[position - 1]] + node.child[position].keys
        node.child[position].child = [node.child[position - 1].child[-1]] + node.child[position].child

        node.keys[position - 1] = node.child[position - 1].keys[-1]

        node.child[position - 1].child = node.child[position - 1].child[:-1]
        node.child[position - 1].keys = node.child[position - 1].keys[:-1]

    def _move_node_from_right_child(self, node, position):
        assert position < len(node.child) - 1 and len(node.child[position + 1].keys) >= self.t

        node.child[position].keys = node.child[position].keys + [node.keys[position]]
        node.child[position].child = node.child[position].child + [node.child[position + 1].child[0]]

        node.keys[position] = node.child[position + 1].keys[0]

        node.child[position + 1].child = node.child[position + 1].child[1:]
        node.child[position + 1].keys = node.child[position + 1].keys[1:]

    def _fix_empty_root(self, node):
        if node == self.root and len(node.child) == 1:
            self.root = node.child[0]
            return self.root
        else:
            return node

    def _delete(self, key, node):
        if node is None or len(node.child) == 0:
            return

        position = node._lower_bound(key)

        if position > 0 and node.keys[position - 1] == key:

            if node.child[position] is None:
                self._delete_key_leaf(key, node, position - 1)

            elif len(node.child[position - 1].keys) >= self.t:
                kp = self._find_predecessor(key, node.child[position - 1])
                node.keys[position - 1] = kp
                self._delete(kp, node.child[position - 1])

            elif len(node.child[position].keys) >= self.t:
                kp = self._find_succesor(key, node.child[position])
                node.keys[position - 1] = kp
                self._delete(kp, node.child[position])

            else:
                self._merge_children_around_key(key, node, position - 1)

                node = self._fix_empty_root(node)

                self._delete(key, node)
        else:

            if node.child[position] is None:
                pass
            elif len(node.child[position].keys) >= self.t:
                self._delete(key, node.child[position])
            else:
                if position > 0 and len(node.child[position - 1].keys) >= self.t:
                    self._move_node_from_left_child(node, position)
                    self._delete(key, node.child[position])
                elif position < len(node.child) - 1 and len(node.child[position + 1].keys) >= self.t:
                    self._move_node_from_right_child(node, position)
                    self._delete(key, node.child[position])
                else:

                    if position > 0:
                        self._merge_children_around_key(key, node, position - 1)

                        node = self._fix_empty_root(node)

                        self._delete(key, node)
                    elif position < len(node.child) - 1:
                        self._merge_children_around_key(key, node, position)

                        node = self._fix_empty_root(node)

                        self._delete(key, node)
                    else:
                        assert False

    def delete(self, key):
        self._delete(key, self.root)

    def _find_all(self, key, node, line):
        if node is None or len(node.child) == 0:
            return
        b = 0
        e = len(node.child) - 1
        while b < e:
            mid = (b + e + 1) // 2
            if mid == 0:
                pass
            elif node.keys[mid - 1] < key:
                b = mid
            else:
                e = mid - 1

        left = b

        b = 0
        e = len(node.child) - 1
        while b < e:
            mid = (b + e + 1) // 2
            if mid == 0:
                pass
            elif node.keys[mid - 1] > key:
                e = mid - 1
            else:
                b = mid
        right = b

        for i in range(left, right + 1):
            self._find_all(key, node.sons[i], line)

            if i < right:
                assert node.keys[i] == key
                line.append(node.keys[i])

    def find_all(self, key):
        ans = []
        self._find_all(key, self.root, ans)
        return ans


randomTree = BTree(3)


def randomInsertion(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        randomTree.insert(randint(1, 595959))
    endtime = datetime.now()

    print('insertion time:', (endtime - startTime))


def randomFind(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        randomTree.find(i)
    endtime = datetime.now()

    print('searching time:', (endtime - startTime))


def randomDeletion(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        randomTree.delete(i)
    endtime = datetime.now()

    print('deletion time:', (endtime - startTime))


sequentalTree = BTree(3)


def sequentalInsertion(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        sequentalTree.insert(i)
    endtime = datetime.now()

    print('insertion time:', (endtime - startTime))


def sequentalFind(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        randomTree.find(i)
    endtime = datetime.now()

    print('searching time:', (endtime - startTime))


def sequentalDeletion(rangeSize):
    startTime = datetime.now()
    for i in range(rangeSize):
        sequentalTree.delete(i)
    endtime = datetime.now()

    print('deletion time:', (endtime - startTime))


if __name__ == '__main__':
    rangeSize = 10_000_000

    print('The next result is for %d elements' % rangeSize)

    randomInsertion(rangeSize)
    randomFind(rangeSize)
    randomDeletion(rangeSize)

    print()

    sequentalInsertion(rangeSize)
    sequentalFind(rangeSize)
    sequentalDeletion(rangeSize)
