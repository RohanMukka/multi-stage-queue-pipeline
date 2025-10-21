# to run this code use the below command
#python .\convert_txt_to_mtx.py .\graphs\facebook_combined.txt .\graphs\facebook_combined.mtx
#!/usr/bin/env python3
import sys

if len(sys.argv) != 3:
    print("Usage: python convert_txt_to_mtx.py input.txt output.mtx")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# First pass: count nodes and edges
max_node = 0
edges = []

with open(input_file, "r") as f:
    for line in f:
        if line.startswith("#") or line.strip() == "":
            continue
        u, v = map(int, line.split())
        edges.append((u, v))
        max_node = max(max_node, u, v)

num_nodes = max_node + 1
num_edges = len(edges)

# Write MTX file
with open(output_file, "w") as f:
    f.write("%%MatrixMarket matrix coordinate pattern general\n")
    f.write(f"% Converted from {input_file}\n")
    f.write(f"{num_nodes} {num_nodes} {num_edges}\n")
    for u, v in edges:
        f.write(f"{u+1} {v+1}\n")  # +1 because MatrixMarket is 1-based

print(f" Wrote {output_file} with {num_nodes} nodes and {num_edges} edges.")
