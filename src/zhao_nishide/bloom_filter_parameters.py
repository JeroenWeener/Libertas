"""Bloom filter parameters.

The parameters depend on the use case. Lower FP rates and longer keywords require more bits.
Suppose we have keywords w with length 7. Then, S_K(w) will contain 64 elements. We set the FP rate to 0.01.

Bloom filter size
-----------------
m = -(n * log(p)) / (log(2)^2)
m : int
    number of bits in the Bloom filter
n : int
    number of items expected to be stored in the Bloom filter
p : float
    FP rate (0-1)

n = 64      -\
             |-> m ~ 614
p = 0.01    -/
-----------------

Number of hash functions
-----------------
k = (m/n) * log(2)
k : int
    number of hash functions
m : int
    size of bits in the Bloom filter
n : int
    number of items expected to be stored in the Bloom filter

m = 614    -\
            |-> ceil(k) = 7
n = 64     -/
"""
BF_ARRAY_SIZE = 614
BF_HASH_FUNCTIONS = 7
