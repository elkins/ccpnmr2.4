"""Debug script to check store file contents."""

import numpy as np
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.store_handler import StoreHandler
from memops.global_.python_impl.store_file import StoreFile

# Create test file
fname = '/tmp/debug_store.dat'

# Write
handler = StoreHandler(fname)

ndim = 2
npoints = np.array([100, 100])
first = np.array([0, 0])
last = np.array([100, 100])
block_size = np.array([100, 100])
nblocks = np.array([1, 1])
levels = np.array([1.0])

print("Writing file...")
print(f"  ndim={ndim}, block_size={block_size}, nblocks={nblocks}")
print(f"  first={first}, last={last}")

handler.init_store_save(ndim, 0, 1, npoints, first, last,
                      block_size, nblocks, 1, levels)

block = np.array([0, 0])
plane = np.array([0, 0])

print(f"\nSetting block={block}, plane={plane}")
handler.init_store_block(block)
handler.init_store_plane(plane)
handler.init_store_level(1.0)

# Write polyline
vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]])
print(f"  Writing polyline with {len(vertices)} vertices")
print(f"  Current offset before draw: {handler.offset}")
print(f"  Current directory: {handler.directory}")
handler.draw_polyline(vertices)
print(f"  Current offset after draw: {handler.offset}")
print(f"  Current directory: {handler.directory}")

print("  Ending plane")
handler.end_store_plane()

print("  Ending save")
handler.end_store_save()

print("\nWritten file successfully")

# Now read it back
print("\nReading file back...")
store_file = StoreFile(fname, ndim, 0, 1, block_size)

print(f"  File position after header read: {store_file.fp.tell()}")
print(f"  ndim={store_file.ndim}")
print(f"  xdim={store_file.xdim}, ydim={store_file.ydim}")
print(f"  have_pos={store_file.have_pos}, have_neg={store_file.have_neg}")
print(f"  nblocks={store_file.nblocks}")
print(f"  block_size={store_file.block_size}")
print(f"  block_min={store_file.block_min}")
print(f"  first={store_file.first}")
print(f"  header_size (words)={store_file.header_size}")
print(f"  dir_size (words)={store_file.dir_size}")
print(f"  Directory size={len(store_file.directory)}")
print(f"  Directory contents={store_file.directory[:10]}")  # Show first 10 entries

# Calculate the file offset for directory entry 0
dir_index = 0
offset = store_file.directory[dir_index]
file_offset = (offset + store_file.header_size + store_file.dir_size) * 4
print(f"\n  For dir_index={dir_index}, offset={offset}")
print(f"  Calculated file_offset = ({offset} + {store_file.header_size} + {store_file.dir_size}) * 4 = {file_offset}")

# Try to process
results = []

def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
    print(f"\nCallback called: block={block}, plane={plane}, level={level}, npolylines={npolylines}")
    results.append((npolylines, polylines))
    return True

print("\nProcessing contours...")
success = store_file.process_contours(np.array([0, 0]), np.array([0, 0]), collect)
print(f"  Success={success}")
print(f"  Results collected={len(results)}")

if results:
    for i, (n, polys) in enumerate(results):
        print(f"  Result {i}: {n} polylines")
        for j, poly in enumerate(polys):
            print(f"    Polyline {j}: {poly.nvertices} vertices, closed={poly.closed}")

store_file.close()
