# Merkle Tree Implementation

03/01/2021

Python version 3.6+

What Is This?
-------------
This is a simple python script that opens a file called "hashes.txt" and for each MD5 hash in it (separated by a newline), it will attempt to crack it. A sample hashes.txt is given.


How To Use This
---------------
1. Give test.sh permission to execute with `chmod +x test.sh`
2. Run (and/or modify) test.sh with `./test.sh`


Explanation
---------------
Each of the Python scripts have three parts: a MerkleNode class, a MerkleTree class, and main function to drive the functionality each script should have. The MerkleTree classes are very similar across files.

The core of MerkleTree is based on appending to an array that contains MerkleNode elements. MerkleNode elements come in two types: one has data (hereinafter leaf node) and one has two children (hereinafter hash node). Both have hashes associated with them. When someone wants to insert data into the Merkle tree, only two things are done: a hash node is appended to the array and then a leaf node is added to the array. This makes visualizing the array very easy. For example, if we have an array with labeled nodes [1, 2, 3, 4, 5,], it will look like this:

                 4
              /      \
          2             5
       /     \
     1         3

And an array with labelled nodes [1, 2, 3, 4, 5, 6, 7] will look like this:

                 4
              /      \
          2             6
       /     \       /     \
     1         3   5         7


So after the array is built, the tree is hashed in a top-down manner. Starting from the root node (in this case 4) which we can find with some math, we set the left and right children and the height as we move down the tree recursively. We use the height to pretty print the graph in the files.

Checkinclusion.py uses regex to collect all of the data from the merkle.tree file in the same order as it was inputted and rebuilds the tree using that data. It then starts from the root and it executes a depth-first search to find the data being queried. If the data is found, the opposite child’s hash is passed up the call stack and appended to an array. The opposite child as in if 1 is queried in the above tree, the hash for 3 is passed up (to make the hash for 2), then 6 (to make the hash for 4), and lastly 4 for verification.

Checkconsistency.py simply builds each inputted tree and finds the root hash of the first tree. It uses much the same structure as checkinclusion.py for verification but instead of checking data, it searches for the old root hash in the new Merkle tree and propagates the hash as well as all the opposite hashes stated above until the root of the new tree is hit.
