import pickle
from pprint import pprint
import sys

with open(sys.argv[1], "rb") as f:
    state = pickle.load(f)
    with open("state.txt", "w") as f2:
        pprint(state, stream=f2)