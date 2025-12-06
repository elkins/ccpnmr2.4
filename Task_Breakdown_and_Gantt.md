# CCPNMR Modernization: Parallel Task Breakdown & Gantt Chart

## Executive Summary

**Current State:**
- Python 2→3 syntax: 95% complete (1,784/~1,880 files)
- C→Python conversion: 47% complete (27,206/58,354 lines)
- Test infrastructure: 800+ tests, 99.9% pass rate

**Critical Path:** Performance validation (Phase 3) blocks production rollout

**Team Capacity:** Can support 3-4 parallel workstreams without conflicts

**Timeline to Rollout:** 4-6 weeks with 3-4 developers + QA + research team

**Branch Structure:** All 18 task branches have been created and pushed to GitHub. See [Git_Branch_Strategy.md](Git_Branch_Strategy.md) for detailed branching strategy, merge workflows, and conflict prevention.

---

## Work Stream Organization

### Stream 1: Python 2→3 Completion (CRITICAL PATH - Week 1-2)
**Lead:** Python modernization specialist
**Can start:** Immediately
**Duration:** 2 weeks

### Stream 2: C→Python Zero-Risk Conversions (Weeks 1-3)
**Lead:** Scientific computing developer(s)
**Can start:** Immediately (all tasks parallel)
**Duration:** 3 weeks

### Stream 3: Performance Profiling & Optimization (CRITICAL PATH - Weeks 2-6)
**Lead:** Performance engineer
**Can start:** After Python 3 imports working (end of Week 1)
**Duration:** 4-5 weeks

### Stream 4: Scientific Validation (Weeks 1-5)
**Lead:** Research team member + QA
**Can start:** Immediately
**Duration:** 5 weeks

---

## Gantt Chart (Text Format)

```
Week 1 (Immediate Start - Highly Parallel)
===========================================================
Stream 1: Python 2→3 Completion
Task 1.1: Fix StandardError        [■■]
Task 1.2: Import Validation                [■■■]
Task 1.3: Smoke Tests                          [■■■■]

Stream 2: C→Python Zero-Risk (All Parallel)
Task 2.1: list.c                   [■■]
Task 2.2: diag_dbl.c              [■]
Task 2.3: eigenvalue.c            [■]
Task 2.4: hash_list.c                [■■]
Task 2.5: gamma.c                    [■■]

Stream 4: Validation Prep (Can Start Immediately)
Task 4.1: Prepare Datasets        [■■]

===========================================================

Week 2 (Stream 3 Starts - Critical Path Begins)
===========================================================
Stream 1: Python 2→3 Completion
Task 1.3: Smoke Tests (cont.)     [■■■]

Stream 2: C→Python Zero-Risk
Task 2.6: fit1d.c                 [■■■■]
Task 2.7: cpmg.c                      [■■■■■]

Stream 3: Performance (STARTS after 1.2 complete)
Task 3.1: Perf Infrastructure              [■■■■]

Stream 4: Validation
Task 4.2: Comparison Framework    [■■■■]

===========================================================

Week 3 (Critical Performance Work)
===========================================================
Stream 3: Performance (CRITICAL PATH)
Task 3.1: Perf Infrastructure (cont) [■■]
Task 3.2: Profile Contouring                [■■■■■■]
Task 3.4: Other Profiling                       [■■■■]

Stream 4: Validation
Task 4.2: Comparison (cont.)      [■■]
Task 4.3: Execute Validation              [■■■■]

===========================================================

Week 4 (Optimization & Validation)
===========================================================
Stream 3: Performance (CRITICAL PATH)
Task 3.2: Profile Contouring (cont) [■■■]
Task 3.3: Optimize Contouring            [■■■■■■]

Stream 4: Validation (CRITICAL PATH)
Task 4.3: Execute Validation      [■■■■]
Task 4.4: User Documentation              [■■■■]

===========================================================

Week 5-6 (Optimization Completion)
===========================================================
Stream 3: Performance (CRITICAL PATH)
Task 3.3: Optimize Contouring     [■■■■■■■■■]

Stream 4: Validation
Task 4.4: User Documentation      [■■■■]

===========================================================

Week 7+ (Staged Rollout - Success!)
===========================================================
```

**Legend:**
- `[■]` = 2-4 hours of work
- `[■■]` = 4-8 hours
- `[■■■]` = 8-12 hours

---

## Task Quick Reference

**All branches created and ready!** Simply checkout the branch for your task and start working. See [Git_Branch_Strategy.md](Git_Branch_Strategy.md) for merge workflows.

### 🚀 Can Start TODAY (No Blockers):
1. **Task 1.1:** Fix StandardError (2-4h) - Branch: `fix/standarderror-exceptions`
2. **Task 2.1:** Convert list.c (2-3h) - Branch: `convert/list-to-python`
3. **Task 2.2:** Convert diag_dbl.c (1-2h) - Branch: `convert/diag-dbl-numpy`
4. **Task 2.3:** Convert eigenvalue.c (1-2h) - Branch: `convert/eigenvalue-numpy`
5. **Task 4.1:** Prepare datasets (4-6h) - Branch: `validation/prepare-datasets`

### 🟡 Can Start After Day 1 (Task 1.1 complete):
6. **Task 1.2:** Import validation (4-6h) - Branch: `validate/python3-imports`
7. **Task 2.4:** Convert hash_list.c (2-3h) - Branch: `convert/hash-list-python`
8. **Task 2.5:** Convert gamma.c (2-3h) - Branch: `convert/gamma-scipy`

### 🔴 Critical Path (Must Complete for Rollout):
- **Task 3.2:** Profile contouring (15-20h) - Week 3-4 - Branch: `perf/contour-profiling`
- **Task 3.3:** Optimize contouring (15-25h) - Week 4-6 - Branch: `perf/contour-optimization`
- **Task 4.3:** Scientific validation (12-16h) - Week 3-4 - Branch: `validation/scientific-results`

---

## Detailed Task List

## STREAM 1: Python 2→3 Completion

### Task 1.1: Fix Remaining StandardError Issues
- **Effort:** S (2-4 hours)
- **Priority:** P0 (Critical)
- **Branch:** `fix/standarderror-exceptions`
- **Blocking:** None
- **Blocks:** Tasks 1.2, 1.3, Stream 3 start

**What to do:**
1. Search for remaining StandardError usage
2. Replace `StandardError` → `Exception`
3. Test imports for affected files
4. Run smoke test on modified files

**Done when:**
- ✅ Zero StandardError references in code (excluding comments)
- ✅ All modified files import successfully
- ✅ `python3 -c "import ccpnmr.analysis"` works

---

### Task 1.2: Comprehensive Import Validation
- **Effort:** S (4-6 hours)
- **Priority:** P0 (Critical)
- **Branch:** `validate/python3-imports`
- **Blocking:** Task 1.1
- **Blocks:** Tasks 1.3, all of Stream 3

**What to do:**
1. Create import validation script for all core modules
2. Run against memops.*, ccp.*, ccpnmr.*
3. Document failures and fix trivial issues
4. Generate import validation report

**Done when:**
- ✅ 100% of core library modules import successfully
- ✅ Import validation report generated
- ✅ GUI modules excluded (documented as out of scope)

---

### Task 1.3: Core Library Smoke Tests
- **Effort:** M (8-12 hours)
- **Priority:** P0 (Critical)
- **Branch:** `test/python3-smoke-tests`
- **Blocking:** Task 1.2
- **Blocks:** Production rollout

**What to do:**
1. Create smoke test suite for core workflows
2. Run tests: spectrum reading, peak picking, contouring, fitting
3. Document any issues
4. Fix critical failures

**Done when:**
- ✅ Smoke tests execute without errors
- ✅ Pass rate ≥95%
- ✅ Core NMR workflows demonstrably functional

---

## STREAM 2: C→Python Zero-Risk Conversions

**All these tasks can run in parallel by different developers!**

### Task 2.1: Convert list.c → Python list wrapper
- **Effort:** S (2-3 hours)
- **Priority:** P1 (High)
- **Branch:** `convert/list-to-python`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze list.c API (200 lines)
2. Create python_impl/list.py wrapping Python list
3. Create tests (test_list.py)
4. Performance benchmark vs C

**Done when:**
- ✅ list.py implements full list.c API
- ✅ 20+ tests, 100% passing
- ✅ Performance ≥100% of C speed (Python list is faster)

**Files to create:**
- `ccpnmr2.4/python/memops/c/python_impl/list.py`
- `ccpnmr2.4/python/memops/c/python_impl/test_list.py`

---

### Task 2.2: Convert diag_dbl.c → NumPy wrapper
- **Effort:** S (1-2 hours)
- **Priority:** P1 (High)
- **Branch:** `convert/diag-dbl-numpy`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze diag_dbl.c (matrix diagonalization, 205 lines)
2. Create NumPy wrapper using `np.linalg.eig`
3. Create tests comparing with C results
4. Performance benchmark (expect 10-100x speedup)

**Done when:**
- ✅ diag_dbl.py wraps NumPy successfully
- ✅ 15+ tests, 100% passing
- ✅ Numerical accuracy: rtol < 1e-10
- ✅ Performance: 10-100x faster than C

---

### Task 2.3: Convert eigenvalue.c → NumPy wrapper
- **Effort:** S (1-2 hours)
- **Priority:** P1 (High)
- **Branch:** `convert/eigenvalue-numpy`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze eigenvalue.c (217 lines)
2. Create NumPy wrapper using `np.linalg.eigh` (for symmetric matrices)
3. Create tests vs C implementation
4. Performance benchmark

**Done when:**
- ✅ eigenvalue.py functional
- ✅ 15+ tests, 100% passing
- ✅ Numerical accuracy: rtol < 1e-10
- ✅ Performance: 10-100x faster than C

---

### Task 2.4: Convert hash_list.c → dict+list hybrid
- **Effort:** S (2-3 hours)
- **Priority:** P1 (High)
- **Branch:** `convert/hash-list-python`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze hash_list.c (ordered hash table, ~150 lines)
2. Implement using Python dict + list for ordering
3. Create tests for insert/lookup/delete/ordering
4. Performance benchmark

**Done when:**
- ✅ hash_list.py implements full API
- ✅ 20+ tests, 100% passing
- ✅ Performance ≥100% of C speed
- ✅ Ordering preserved correctly

---

### Task 2.5: Convert gamma.c → SciPy wrapper
- **Effort:** S (2-3 hours)
- **Priority:** P2 (Medium)
- **Branch:** `convert/gamma-scipy`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze gamma.c (141 lines: gamma, gammainc, gammaln)
2. Create SciPy wrapper using `scipy.special`
3. Create tests vs C results
4. Performance verification

**Done when:**
- ✅ gamma.py wraps SciPy successfully
- ✅ 10+ tests, 100% passing
- ✅ Numerical accuracy matches C

---

### Task 2.6: Convert fit1d.c → SciPy optimization
- **Effort:** M (4-6 hours)
- **Priority:** P2 (Medium)
- **Branch:** `convert/fit1d-scipy`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze fit1d.c (1D function minimization, 142 lines)
2. Wrap `scipy.optimize.minimize_scalar`
3. Create tests on known functions
4. Performance benchmark

**Done when:**
- ✅ fit1d.py functional
- ✅ 15+ tests, 100% passing
- ✅ Optimization converges correctly

---

### Task 2.7: Convert cpmg.c → SciPy curve fitting
- **Effort:** M (6-8 hours)
- **Priority:** P2 (Medium)
- **Branch:** `convert/cpmg-scipy`
- **Blocking:** None
- **Blocks:** None

**What to do:**
1. Analyze cpmg.c (CPMG relaxation dispersion, 209 lines)
2. Implement CPMG equations in Python
3. Use `scipy.optimize.curve_fit`
4. Create tests with known datasets

**Done when:**
- ✅ cpmg.py functional
- ✅ 20+ tests, 100% passing
- ✅ Fits converge correctly on CPMG data

---

## STREAM 3: Performance Profiling & Optimization (CRITICAL PATH)

### Task 3.1: Establish Performance Testing Infrastructure
- **Effort:** M (8-12 hours)
- **Priority:** P0 (Critical - blocks rollout)
- **Branch:** `perf/testing-infrastructure`
- **Blocking:** Task 1.2 (Python 3 imports must work)
- **Blocks:** Tasks 3.2, 3.3, 3.4

**What to do:**
1. Identify critical performance workflows
   - 3D/4D spectrum contouring
   - Large spectrum file reading
   - Peak detection on dense spectra
2. Create benchmark suite
3. Profile C implementation (baseline)
4. Profile Python 3 implementation (current state)
5. Document performance targets (90% of C minimum)

**Done when:**
- ✅ Benchmark suite runs automatically
- ✅ C baseline performance documented
- ✅ Python 3 baseline measured
- ✅ Performance targets defined

---

### Task 3.2: Profile Contouring Performance on Large Datasets
- **Effort:** L (15-20 hours)
- **Priority:** P0 (Critical - user concern)
- **Branch:** `perf/contour-profiling`
- **Blocking:** Task 3.1
- **Blocks:** Task 3.3, Production rollout

**What to do:**
1. Profile contouring on production 3D/4D spectra
2. Identify bottlenecks (memory, algorithm, I/O)
3. Compare Python vs C performance
4. Measure memory usage
5. Test different dataset sizes
6. Create profiling visualization

**Done when:**
- ✅ Contouring performance measured for 3D/4D
- ✅ Bottlenecks identified and documented
- ✅ Performance gap quantified (Python vs C)
- ✅ Report delivered to research team

**Tools:**
```bash
python -m cProfile -o contour.prof contour_test.py
python -m memory_profiler contour_test.py
```

---

### Task 3.3: Optimize Contouring with Numba ⚠️ CRITICAL
- **Effort:** L (15-25 hours)
- **Priority:** P0 (Critical - blocks rollout)
- **Branch:** `perf/contour-optimization`
- **Blocking:** Task 3.2
- **Blocks:** Production rollout

**What to do:**
1. Apply Numba JIT to contouring hotspots
2. Optimize memory access patterns
3. Implement chunking/progressive rendering if needed
4. Re-profile after optimization
5. Verify numerical accuracy maintained
6. Get research team sign-off

**Done when:**
- ✅ Contouring ≥90% of C speed OR research team approves
- ✅ Numerical accuracy maintained (rtol < 1e-6)
- ✅ Memory usage acceptable
- ✅ Research team written approval

**Example Numba optimization:**
```python
import numba

@numba.jit(nopython=True, parallel=True)
def contour_march(data, level):
    # Marching squares/cubes algorithm
    ...
```

**Decision Point:** If targets not met:
1. More optimization (extend timeline)
2. Hybrid approach (keep C for contouring)
3. Progressive rendering (different UX)

---

### Task 3.4: Profile and Optimize Other Critical Paths
- **Effort:** M (10-15 hours)
- **Priority:** P1 (High)
- **Branch:** `perf/general-optimization`
- **Blocking:** Task 3.1
- **Blocks:** None (nice-to-have)

**What to do:**
1. Profile file I/O (Varian, Bruker readers)
2. Profile peak detection algorithms
3. Profile fitting operations
4. Apply targeted optimizations

**Done when:**
- ✅ All critical workflows profiled
- ✅ No performance regressions introduced

---

## STREAM 4: Scientific Validation

### Task 4.1: Prepare Validation Test Datasets
- **Effort:** S (4-6 hours)
- **Priority:** P1 (High)
- **Branch:** `validation/prepare-datasets`
- **Blocking:** None
- **Blocks:** Tasks 4.2, 4.3

**What to do:**
1. Gather 3-5 production NMR datasets
   - Various experiment types (2D, 3D, 4D)
   - Different formats (Varian, Bruker, NMRPipe)
   - Range of sizes (small, medium, large)
2. Document dataset characteristics
3. Create baseline results (Python 2/C version)
4. Store in test data repository

**Done when:**
- ✅ ≥3 production datasets available
- ✅ Dataset characteristics documented
- ✅ Baseline results generated

---

### Task 4.2: Side-by-Side Validation Script
- **Effort:** M (8-12 hours)
- **Priority:** P1 (High)
- **Branch:** `validation/comparison-framework`
- **Blocking:** Task 4.1
- **Blocks:** Task 4.3

**What to do:**
1. Create comparison framework
   - Run analysis in Python 2 and Python 3
   - Compare outputs numerically
   - Generate diff reports
2. Define acceptable tolerances
3. Create visualization of differences

**Done when:**
- ✅ Comparison framework functional
- ✅ Tolerance thresholds defined
- ✅ Diff reporting clear

---

### Task 4.3: Execute Scientific Validation
- **Effort:** M (12-16 hours, includes research team)
- **Priority:** P0 (Critical - blocks rollout)
- **Branch:** `validation/scientific-results`
- **Blocking:** Tasks 4.2, 1.3
- **Blocks:** Production rollout

**What to do:**
1. Run validation on all test datasets
2. Analyze differences
3. Investigate discrepancies
4. Fix any bugs found
5. Get research team sign-off

**Done when:**
- ✅ All datasets process successfully
- ✅ Differences documented and explained
- ✅ Research team written approval
- ✅ Validation report published

---

### Task 4.4: Create User Documentation
- **Effort:** M (10-15 hours)
- **Priority:** P1 (High)
- **Branch:** `docs/user-guide-python3`
- **Blocking:** Task 4.3
- **Blocks:** Production rollout

**What to do:**
1. Write user guide for Python 3 version
   - Installation instructions
   - What's changed from Python 2
   - Known limitations
   - Troubleshooting
2. Create migration guide
3. FAQ document

**Done when:**
- ✅ Comprehensive user documentation
- ✅ Installation tested on clean system
- ✅ Research team reviews and approves

---

## Dependency Graph

```
START
  │
  ├─→ Task 1.1: Fix StandardError (S) ──→ Task 1.2: Import Validation (S)
  │                                          │
  │                                          ├─→ Task 1.3: Smoke Tests (M)
  │                                          │
  │                                          └─→ Task 3.1: Perf Infrastructure (M)
  │                                               │
  │                                               ├─→ Task 3.2: Profile Contouring (L) **CRITICAL**
  │                                               │     │
  │                                               │     └─→ Task 3.3: Optimize Contouring (L) **CRITICAL**
  │                                               │           │
  │                                               │           └─→ ROLLOUT
  │                                               │
  │                                               └─→ Task 3.4: Other Profiling (M)
  │
  ├─→ Task 2.1: list.c (S) ─────────────────→ (Independent)
  ├─→ Task 2.2: diag_dbl.c (S) ─────────────→ (Independent)
  ├─→ Task 2.3: eigenvalue.c (S) ───────────→ (Independent)
  ├─→ Task 2.4: hash_list.c (S) ────────────→ (Independent)
  ├─→ Task 2.5: gamma.c (S) ────────────────→ (Independent)
  ├─→ Task 2.6: fit1d.c (M) ────────────────→ (Independent)
  └─→ Task 2.7: cpmg.c (M) ─────────────────→ (Independent)

  └─→ Task 4.1: Prepare Datasets (S) ──→ Task 4.2: Comparison Framework (M)
                                           │
                                           └─→ Task 4.3: Execute Validation (M) **CRITICAL**
                                                 │
                                                 └─→ Task 4.4: Documentation (M) ──→ ROLLOUT
```

**Critical Path:** 1.1 → 1.2 → 3.1 → 3.2 → 3.3 → ROLLOUT (≈4-5 weeks)

---

## Branch Naming Strategy

### Convention
```
<type>/<scope>-<description>

Types:
- fix/       - Bug fixes, Python 2→3 syntax
- convert/   - C→Python conversions
- perf/      - Performance work
- validation/- Scientific validation
- test/      - Test infrastructure
- docs/      - Documentation
```

### All Branches for This Project
```
fix/standarderror-exceptions
validate/python3-imports
test/python3-smoke-tests
convert/list-to-python
convert/diag-dbl-numpy
convert/eigenvalue-numpy
convert/hash-list-python
convert/gamma-scipy
convert/fit1d-scipy
convert/cpmg-scipy
perf/testing-infrastructure
perf/contour-profiling
perf/contour-optimization
perf/general-optimization
validation/prepare-datasets
validation/comparison-framework
validation/scientific-results
docs/user-guide-python3
```

### Merge Strategy
- Merge to `analysis-phase` branch
- Stream 1: Sequential merges (order matters)
- Stream 2: Independent merges (no conflicts)
- Stream 3: Sequential within stream
- Stream 4: Merge as ready

---

## Resource Allocation

### Minimum Team (Sequential):
- **1-2 developers:** 8-10 weeks
- **Plus:** QA + research team for validation

### Optimal Team (Parallel):
- **Dev A:** Stream 1 (Week 1-2)
- **Dev B:** Stream 2 tasks 2.1-2.4 (Week 1-2)
- **Dev C:** Stream 2 tasks 2.5-2.7 (Week 1-3)
- **Dev D:** Stream 3 (Week 2-6) **Performance specialist**
- **QA:** Stream 4 (Week 1-5)
- **Research team:** Validation sign-off (Week 4-5)

**Timeline with optimal team:** 4-6 weeks to rollout

---

## Risk Heat Map

```
                    LOW RISK          MEDIUM RISK         HIGH RISK
                    --------          -----------         ---------
HIGH IMPACT    │ Task 2.1-2.3     │ Task 3.3 (CRITICAL)│            │
(Blocks        │ Task 1.1, 1.2    │ Task 4.3           │            │
Rollout)       │                  │                    │            │
───────────────┼──────────────────┼────────────────────┼────────────┤
MEDIUM IMPACT  │ Task 2.4-2.7     │ Task 3.2, 3.4      │            │
(Improves      │ Task 1.3         │ Task 4.2, 4.4      │            │
Quality)       │                  │                    │            │
```

**Watch Task 3.3:** Contouring optimization is the biggest risk. If it fails, project has fallback options (hybrid C/Python, extended timeline).

---

## Success Metrics by Phase

### Week 2 Success:
- ✅ All Python 3 imports working
- ✅ ≥3 C modules converted
- ✅ Validation datasets ready

### Week 4 Success:
- ✅ Smoke tests passing
- ✅ Performance baseline established
- ✅ Contouring profiled

### Week 6 Success (Rollout Ready):
- ✅ Contouring ≥90% speed OR research approval
- ✅ Scientific validation complete
- ✅ User documentation published

---

## Emergency Scenarios

### Scenario 1: Contouring Performance Unacceptable
**Trigger:** Python <70% of C speed
**Response:**
1. Research team consultation
2. Options:
   - Extended optimization (Task 3.3)
   - Hybrid approach (keep C)
   - Progressive rendering
3. Timeline: +2-4 weeks

### Scenario 2: Scientific Validation Fails
**Trigger:** Unacceptable discrepancies in results
**Response:**
1. Halt rollout
2. Bug fixes
3. Re-validation
4. Timeline: +1-3 weeks

---

## How to Get Started

### If You're Working Alone:
1. **Week 1:** Task 1.1 → 1.2 → Start 1.3
2. **Week 2:** Finish 1.3, Start 3.1
3. **Week 3:** Tasks 3.2, 4.1, 4.2
4. **Week 4-6:** Tasks 3.3 (critical!), 4.3, 4.4
5. **Pick up Stream 2 tasks whenever you have spare time (independent)**

### If You Have a Team:
1. **Assign streams** to different developers
2. **Daily standups:** What merged? Any blockers?
3. **Watch critical path:** Tasks 3.2 and 3.3 cannot slip
4. **Stream 2 tasks** are great for junior devs (clear scope, no blockers)

### First 5 Tasks to Tackle:
1. Task 1.1 (2-4h) - Enables everything
2. Task 4.1 (4-6h) - Can start immediately, unblocks validation
3. Task 2.1 (2-3h) - Easy win, establishes pattern
4. Task 2.2 (1-2h) - Easy win
5. Task 1.2 (4-6h) - Unblocks critical path

---

**Document Status:** Ready for team coordination
**Last Updated:** December 2025
**Next Review:** After Week 2 (adjust based on progress)
