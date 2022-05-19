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

    def _inorder(self, cur):
        if cur == None: return

        for i, son in enumerate(cur.child):
            if i > 0:
                yield cur.keys[i - 1]
            yield from self._inorder(son)

    def inorder(self):
        yield from self._inorder(self.root)

    def _preorder(self, cur):
        if cur == None: return
        for key in cur.keys:
            yield key
        for son in cur.child:
            yield from self._preorder(son)

    def preorder(self):
        yield from self._preorder(self.root)

    def _split(self, node, parnode, pos):

        # root case
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
            parnode.keys = parnode.keys[:pos] + [node.keys[self.t - 1]] + parnode.keys[pos:]
            parnode.child = parnode.child[:pos] + [left, right] + parnode.child[pos + 1:]

    def _insert(self, key, node, parnode):
        if node is None: return None

        # node is full, and must be root
        if len(node.keys) == 2 * self.t - 1:
            assert node == self.root
            node = self._split(node, parnode, -1)
            assert len(node.keys) == 1

            # to the right
            if node.keys[0] <= key:
                self._insert(key, node.child[1], node)
            else:
                self._insert(key, node.child[0], node)

            return

        # only possible for root at the beginning
        if len(node.child) == 0:
            assert node == self.root
            node.child.append(None)
            node.keys.append(key)
            node.child.append(None)

            return

        pos = node._lower_bound(key)

        # we are in a leaf
        if node.child[pos] is None:
            node.keys = node.keys[:pos] + [key] + node.keys[pos:]
            node.child.append(None)
        else:

            # son is full, doing split from here
            if node.child[pos] is not None and len(node.child[pos].keys) == 2 * self.t - 1:
                self._split(node.child[pos], node, pos)
                # go to right
                if node.keys[pos] <= key:
                    self._insert(key, node.child[pos + 1], node)
                else:
                    self._insert(key, node.child[pos], node)
            else:
                self._insert(key, node.child[pos], node)

    def insert(self, key):
        self._insert(key, self.root, None)

    def _find(self, key, node):
        if node is None or len(node.child) == 0:
            return None

        pos = node._lower_bound(key)

        if pos >= 1 and node.keys[pos - 1] == key:
            return node.keys[pos - 1]
        else:
            return self._find(key, node.child[pos])

    def find(self, key):
        return self._find(key, self.root)

    def _find_predecessor(self, key, node):
        if node.child[0] == None:
            return node.keys[-1]
        else:
            return self._find_predecessor(key, node.child[-1])

    def _find_succesor(self, key, node):
        if node.child[0] is None:
            return node.keys[0]
        else:
            return self._find_succesor(key, node.child[0])

    def _delete_key_leaf(self, key, node, pos):

        # condition for correctness of algorithm
        assert node == self.root or len(node.child) >= self.t

        assert node.keys[pos] == key

        node.keys = node.keys[:pos] + node.keys[pos + 1:]
        node.child.pop()

    def _merge_children_around_key(self, key, node, pos):

        assert 0 <= pos < len(node.child) - 1

        y = self.Node()
        y.child = node.child[pos].child + node.child[pos + 1].child
        y.keys = node.child[pos].keys + [node.keys[pos]] + node.child[pos + 1].keys

        node.keys = node.keys[:pos] + node.keys[pos + 1:]
        node.child = node.child[:pos] + [y] + node.child[pos + 2:]

    def _move_node_from_left_child(self, node, pos):

        assert pos > 0 and len(node.child[pos - 1].keys) >= self.t

        node.child[pos].keys = [node.keys[pos - 1]] + node.child[pos].keys
        node.child[pos].child = [node.child[pos - 1].child[-1]] + node.child[pos].child

        node.keys[pos - 1] = node.child[pos - 1].keys[-1]

        node.child[pos - 1].child = node.child[pos - 1].child[:-1]
        node.child[pos - 1].keys = node.child[pos - 1].keys[:-1]

    def _move_node_from_right_child(self, node, pos):

        assert pos < len(node.child) - 1 and len(node.child[pos + 1].keys) >= self.t

        node.child[pos].keys = node.child[pos].keys + [node.keys[pos]]
        node.child[pos].child = node.child[pos].child + [node.child[pos + 1].child[0]]

        node.keys[pos] = node.child[pos + 1].keys[0]

        node.child[pos + 1].child = node.child[pos + 1].child[1:]
        node.child[pos + 1].keys = node.child[pos + 1].keys[1:]

    def _fix_empty_root(self, node):
        if node == self.root and len(node.child) == 1:
            self.root = node.child[0]
            return self.root
        else:
            return node

    def _delete(self, key, node):
        if node is None or len(node.child) == 0: return

        pos = node._lower_bound(key)

        # the key to delete is here
        if pos > 0 and node.keys[pos - 1] == key:

            # this node is a leaf
            if node.child[pos] is None:
                self._delete_key_leaf(key, node, pos - 1)
            # left child node has enough keys
            elif len(node.child[pos - 1].keys) >= self.t:
                kp = self._find_predecessor(key, node.child[pos - 1])
                node.keys[pos - 1] = kp
                self._delete(kp, node.child[pos - 1])
            # right child node has enough keys
            elif len(node.child[pos].keys) >= self.t:
                kp = self._find_succesor(key, node.child[pos])
                node.keys[pos - 1] = kp
                self._delete(kp, node.child[pos])
            # both children have minimal number of keys, must combine them
            else:
                self._merge_children_around_key(key, node, pos - 1)

                # here I should take care of missing root
                node = self._fix_empty_root(node)

                self._delete(key, node)
        else:

            # we are on a leave and haven't found the key, we have nothing to do
            if node.child[pos] is None:
                pass
            # the amount of keys in the child is enough, simply recurse
            elif len(node.child[pos].keys) >= self.t:
                self._delete(key, node.child[pos])
            # we must push a key to the child
            else:
                # left sibbling has enough keys
                if pos > 0 and len(node.child[pos - 1].keys) >= self.t:
                    self._move_node_from_left_child(node, pos)
                    self._delete(key, node.child[pos])
                # right sibbling has enough keys
                elif pos < len(node.child) - 1 and len(node.child[pos + 1].keys) >= self.t:
                    self._move_node_from_right_child(node, pos)
                    self._delete(key, node.child[pos])
                # must merge with one of sibblings
                else:

                    if pos > 0:
                        self._merge_children_around_key(key, node, pos - 1)

                        # here I should take care of missing root
                        node = self._fix_empty_root(node)

                        self._delete(key, node)
                    elif pos < len(node.child) - 1:
                        self._merge_children_around_key(key, node, pos)

                        # here I should take care of missing root
                        node = self._fix_empty_root(node)

                        self._delete(key, node)
                    # this shouldn't be possible
                    else:
                        assert False

    def delete(self, key):
        self._delete(key, self.root)

    def _find_all(self, key, node, ans):
        if node is None or len(node.child) == 0: return
        b = 0
        e = len(node.child) - 1
        while b < e:
            mid = (b + e + 1) // 2
            if mid == 0:  # mid is never 0 actually
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
            if mid == 0:  # mid is never 0 actually
                pass
            elif node.keys[mid - 1] > key:
                e = mid - 1
            else:
                b = mid
        right = b

        # print(left, right, len(node.sons))
        for i in range(left, right + 1):
            self._find_all(key, node.sons[i], ans)

            if i < right:
                assert node.keys[i] == key
                ans.append(node.keys[i])

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
    rangeSize = 1_000_000

    randomInsertion(rangeSize)
    randomFind(rangeSize)
    randomDeletion(rangeSize)

    print()

    sequentalInsertion(rangeSize)
    sequentalFind(rangeSize)
    sequentalDeletion(rangeSize)
