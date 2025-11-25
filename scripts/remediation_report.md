# Wrapper Remediation Report

Generated on: 2025-11-24

Summary:
- Total wrappers found: 41
- Wrappers importing successfully: 1 (`memops.math.fit.fit`)
- Wrappers failing: 40

For each failing wrapper the automatic mapping found no pure-Python implementation and the wrapper attempted to import a compiled extension module (which is not present in this workspace). Recommended immediate action: generate minimal Python stubs to allow the wrapper imports to succeed; later replace stubs with real implementations or port C code as needed.

Failing wrappers and recommended action

| Wrapper Path | Expected module name | Recommendation |
|---|---:|---|
| `/ccpnmr2.4/c/memops/global/py_block_file.py` | `block_file` | Generate stub — create `block_file.py` |
| `/ccpnmr2.4/c/memops/global/py_shape_file.py` | `shape_file` | Generate stub — create `shape_file.py` |
| `/ccpnmr2.4/c/memops/global/py_pdf_handler.py` | `pdf_handler` | Generate stub — create `pdf_handler.py` |
| `/ccpnmr2.4/c/memops/global/py_store_file.py` | `store_file` | Generate stub — create `store_file.py` |
| `/ccpnmr2.4/c/memops/global/py_tk_util.py` | `tk_util` | Generate stub — create `tk_util.py` |
| `/ccpnmr2.4/c/memops/global/py_tk_handler.py` | `tk_handler` | Generate stub — create `tk_handler.py` |
| `/ccpnmr2.4/c/memops/global/py_mem_cache.py` | `mem_cache` | Generate stub — create `mem_cache.py` |
| `/ccpnmr2.4/c/memops/global/py_draw_handler.py` | `draw_handler` | Generate stub — create `draw_handler.py` |
| `/ccpnmr2.4/c/memops/global/py_store_handler.py` | `store_handler` | Generate stub — create `store_handler.py` |
| `/ccpnmr2.4/c/memops/global/py_gl_handler.py` | `gl_handler` | Generate stub — create `gl_handler.py` |
| `/ccpnmr2.4/c/memops/global/py_ps_handler.py` | `ps_handler` | Generate stub — create `ps_handler.py` |
| `/ccpnmr2.4/c/other/cambridge/bayes/py_bayes.py` | `bayes` | Generate stub — create `bayes.py` |
| `/ccpnmr2.4/c/other/meccano/pysrc/py_meccano.py` | `meccano` | Generate stub — create `meccano.py` |
| `/ccpnmr2.4/c/ccp/structure/py_struct_util.py` | `struct_util` | Generate stub — create `struct_util.py` |
| `/ccpnmr2.4/c/ccp/structure/py_atom.py` | `atom` | Generate stub — create `atom.py` |
| `/ccpnmr2.4/c/ccp/structure/py_bond.py` | `bond` | Generate stub — create `bond.py` |
| `/ccpnmr2.4/c/ccp/structure/py_structure.py` | `structure` | Generate stub — create `structure.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_dist_constraint.py` | `dist_constraint` | Generate stub — create `dist_constraint.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_dynamics.py` | `dynamics` | Generate stub — create `dynamics.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_atom_coord_list.py` | `atom_coord_list` | Generate stub — create `atom_coord_list.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_dist_constraint_list.py` | `dist_constraint_list` | Generate stub — create `dist_constraint_list.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_atom_coord.py` | `atom_coord` | Generate stub — create `atom_coord.py` |
| `/ccpnmr2.4/c/ccpnmr/dynamics/py_dist_force.py` | `dist_force` | Generate stub — create `dist_force.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_contour_style.py` | `contour_style` | Generate stub — create `contour_style.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_contour_levels.py` | `contour_levels` | Generate stub — create `contour_levels.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_peak.py` | `peak` | Generate stub — create `peak.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_peak_cluster.py` | `peak_cluster` | Generate stub — create `peak_cluster.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_contour_file.py` | `contour_file` | Generate stub — create `contour_file.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_peak_list.py` | `peak_list` | Generate stub — create `peak_list.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_slice_file.py` | `slice_file` | Generate stub — create `slice_file.py` |
| `/ccpnmr2.4/c/ccpnmr/analysis/py_win_peak_list.py` | `win_peak_list` | Generate stub — create `win_peak_list.py` |
| `/ccpnmr2.4/c/ccpnmr/clouds/py_dist_constraint.py` | `dist_constraint` | Generate stub — create `dist_constraint.py` (note: duplicate name)|
| `/ccpnmr2.4/c/ccpnmr/clouds/py_dynamics.py` | `dynamics` | Generate stub — create `dynamics.py` (note: duplicate name)|
| `/ccpnmr2.4/c/ccpnmr/clouds/py_atom_coord_list.py` | `atom_coord_list` | Generate stub — create `atom_coord_list.py` (note: duplicate name)|
| `/ccpnmr2.4/c/ccpnmr/clouds/py_cloud_util.py` | `cloud_util` | Generate stub — create `cloud_util.py` |
| `/ccpnmr2.4/c/ccpnmr/clouds/py_dist_constraint_list.py` | `dist_constraint_list` | Generate stub — create `dist_constraint_list.py` (note: duplicate name)|
| `/ccpnmr2.4/c/ccpnmr/clouds/py_bacus.py` | `bacus` | Generate stub — create `bacus.py` |
| `/ccpnmr2.4/c/ccpnmr/clouds/py_atom_coord.py` | `atom_coord` | Generate stub — create `atom_coord.py` (note: duplicate name)|
| `/ccpnmr2.4/c/ccpnmr/clouds/py_midge.py` | `midge` | Generate stub — create `midge.py` |
| `/ccpnmr2.4/c/ccpnmr/clouds/py_dist_force.py` | `dist_force` | Generate stub — create `dist_force.py` (note: duplicate name)|
