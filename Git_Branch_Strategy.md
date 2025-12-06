# Git Branch Strategy for CCPNMR Modernization

## Overview

This document defines the branch structure, naming conventions, and merge strategy for the CCPNMR modernization project. It aligns with the task breakdown in [Task_Breakdown_and_Gantt.md](Task_Breakdown_and_Gantt.md).

## Branch Structure

```
analysis-phase (main development branch)
│
├── Stream 1: Python 2→3 Completion
│   ├── fix/standarderror-exceptions
│   ├── validate/python3-imports
│   └── test/python3-smoke-tests
│
├── Stream 2: C→Python Conversions (All Independent)
│   ├── convert/list-to-python
│   ├── convert/diag-dbl-numpy
│   ├── convert/eigenvalue-numpy
│   ├── convert/hash-list-python
│   ├── convert/gamma-scipy
│   ├── convert/fit1d-scipy
│   └── convert/cpmg-scipy
│
├── Stream 3: Performance (Sequential within stream)
│   ├── perf/testing-infrastructure
│   ├── perf/contour-profiling
│   ├── perf/contour-optimization
│   └── perf/general-optimization
│
└── Stream 4: Validation
    ├── validation/prepare-datasets
    ├── validation/comparison-framework
    ├── validation/scientific-results
    └── docs/user-guide-python3
```

---

## Branch Naming Convention

### Format
```
<type>/<scope>-<description>
```

### Types
- **fix/** - Bug fixes, syntax corrections (e.g., StandardError → Exception)
- **convert/** - C module to Python conversions
- **perf/** - Performance profiling and optimization
- **validation/** - Scientific validation work
- **test/** - Test infrastructure and test suites
- **docs/** - Documentation

### Scope
- Brief descriptor of what's being changed (e.g., `standarderror`, `list-to-python`, `contour-profiling`)

### Description
- Optional additional context, kebab-case

### Examples
```
fix/standarderror-exceptions          # Task 1.1
validate/python3-imports              # Task 1.2
convert/list-to-python                # Task 2.1
perf/contour-optimization             # Task 3.3
validation/scientific-results         # Task 4.3
```

---

## Merge Strategy

### Sequential Merges (Dependencies)

**Stream 1: Python 2→3 Completion**
```
analysis-phase
    ↑
    └── fix/standarderror-exceptions (Task 1.1)
            ↑
            └── validate/python3-imports (Task 1.2)
                    ↑
                    └── test/python3-smoke-tests (Task 1.3)
```

**Merge Order:**
1. `fix/standarderror-exceptions` → `analysis-phase`
2. `validate/python3-imports` → `analysis-phase`
3. `test/python3-smoke-tests` → `analysis-phase`

**Why Sequential:** Each task depends on the previous completing successfully.

---

**Stream 3: Performance (Critical Path)**
```
analysis-phase
    ↑
    └── perf/testing-infrastructure (Task 3.1)
            ↑
            ├── perf/contour-profiling (Task 3.2)
            │       ↑
            │       └── perf/contour-optimization (Task 3.3)
            │
            └── perf/general-optimization (Task 3.4) [Can be parallel with 3.2]
```

**Merge Order:**
1. `perf/testing-infrastructure` → `analysis-phase`
2. `perf/contour-profiling` → `analysis-phase`
3. `perf/contour-optimization` → `analysis-phase`
4. `perf/general-optimization` → `analysis-phase` (can merge anytime after 3.1)

**Why Sequential:** Each performance task builds on infrastructure from previous.

---

### Independent Merges (No Dependencies)

**Stream 2: C→Python Conversions**

All these branches are **completely independent** and can be merged in any order:

```
analysis-phase
    ↑
    ├── convert/list-to-python           (Task 2.1) - Can merge anytime
    ├── convert/diag-dbl-numpy           (Task 2.2) - Can merge anytime
    ├── convert/eigenvalue-numpy         (Task 2.3) - Can merge anytime
    ├── convert/hash-list-python         (Task 2.4) - Can merge anytime
    ├── convert/gamma-scipy              (Task 2.5) - Can merge anytime
    ├── convert/fit1d-scipy              (Task 2.6) - Can merge anytime
    └── convert/cpmg-scipy               (Task 2.7) - Can merge anytime
```

**Why Independent:**
- Each converts a different C module
- Files modified are isolated (`ccpnmr2.4/python/memops/c/python_impl/<module>.py`)
- No conflicts expected between these branches
- Can be developed by different people simultaneously

**Merge Strategy:** First ready, first merged. No waiting required.

---

**Stream 4: Validation (Mostly Sequential)**

```
analysis-phase
    ↑
    └── validation/prepare-datasets (Task 4.1)
            ↑
            └── validation/comparison-framework (Task 4.2)
                    ↑
                    ├── validation/scientific-results (Task 4.3)
                    │       ↑
                    │       └── docs/user-guide-python3 (Task 4.4)
```

**Merge Order:**
1. `validation/prepare-datasets` → `analysis-phase`
2. `validation/comparison-framework` → `analysis-phase`
3. `validation/scientific-results` → `analysis-phase`
4. `docs/user-guide-python3` → `analysis-phase`

**Why Sequential:** Each validation task needs outputs from previous task.

---

## Branch Creation Commands

### Create All Stream 1 Branches
```bash
git checkout analysis-phase
git pull origin analysis-phase

# Task 1.1
git checkout -b fix/standarderror-exceptions
git push -u origin fix/standarderror-exceptions

# Task 1.2 (create from main, but don't start work until 1.1 merged)
git checkout analysis-phase
git checkout -b validate/python3-imports
git push -u origin validate/python3-imports

# Task 1.3
git checkout analysis-phase
git checkout -b test/python3-smoke-tests
git push -u origin test/python3-smoke-tests
```

### Create All Stream 2 Branches (Can all be created now)
```bash
git checkout analysis-phase

for module in list-to-python diag-dbl-numpy eigenvalue-numpy hash-list-python gamma-scipy fit1d-scipy cpmg-scipy; do
    git checkout -b convert/$module
    git push -u origin convert/$module
    git checkout analysis-phase
done
```

### Create All Stream 3 Branches
```bash
git checkout analysis-phase

for task in testing-infrastructure contour-profiling contour-optimization general-optimization; do
    git checkout -b perf/$task
    git push -u origin perf/$task
    git checkout analysis-phase
done
```

### Create All Stream 4 Branches
```bash
git checkout analysis-phase

git checkout -b validation/prepare-datasets
git push -u origin validation/prepare-datasets
git checkout analysis-phase

git checkout -b validation/comparison-framework
git push -u origin validation/comparison-framework
git checkout analysis-phase

git checkout -b validation/scientific-results
git push -u origin validation/scientific-results
git checkout analysis-phase

git checkout -b docs/user-guide-python3
git push -u origin docs/user-guide-python3
git checkout analysis-phase
```

---

## Merge Workflow

### Standard Merge Process

1. **Complete work on feature branch**
   ```bash
   git checkout fix/standarderror-exceptions
   # ... make changes ...
   git add .
   git commit -m "Fix StandardError → Exception in workflow modules"
   git push origin fix/standarderror-exceptions
   ```

2. **Update feature branch with latest main** (if needed)
   ```bash
   git checkout analysis-phase
   git pull origin analysis-phase
   git checkout fix/standarderror-exceptions
   git merge analysis-phase
   # Resolve any conflicts
   git push origin fix/standarderror-exceptions
   ```

3. **Merge to main branch**
   ```bash
   git checkout analysis-phase
   git pull origin analysis-phase
   git merge --no-ff fix/standarderror-exceptions
   git push origin analysis-phase
   ```

4. **Delete merged branch** (optional, keeps repo clean)
   ```bash
   git branch -d fix/standarderror-exceptions
   git push origin --delete fix/standarderror-exceptions
   ```

### Using --no-ff (No Fast-Forward)

**Why use --no-ff?**
- Preserves branch history and task structure
- Makes it clear which commits belonged to which task
- Easier to understand project history
- Allows reverting entire tasks if needed

**Example:**
```bash
# Without --no-ff (fast-forward, linear history):
* abc123 - Fix StandardError in Util.py
* def456 - Fix StandardError in Fc.py

# With --no-ff (preserved branch structure):
*   ghi789 - Merge branch 'fix/standarderror-exceptions'
|\
| * abc123 - Fix StandardError in Util.py
| * def456 - Fix StandardError in Fc.py
|/
```

---

## Conflict Prevention

### File Ownership by Stream

**Stream 1 (Python 2→3):**
- Touches: ALL Python files (syntax fixes)
- Conflict Risk: HIGH if others modify same files
- **Strategy:** Complete Stream 1 tasks FIRST before heavy development in other streams

**Stream 2 (C→Python):**
- Touches: `ccpnmr2.4/python/memops/c/python_impl/<module>.py` (new files)
- Conflict Risk: ZERO between Stream 2 branches
- Conflict Risk with Stream 1: LOW (different files)
- **Strategy:** Can work in parallel with all streams

**Stream 3 (Performance):**
- Touches: `benchmarks/`, profiling scripts, Numba decorators in existing modules
- Conflict Risk: MEDIUM if modifying same performance-critical modules
- **Strategy:** Sequential within stream, coordinate with Stream 2 if both touch same module

**Stream 4 (Validation):**
- Touches: `tests/validation/`, `docs/`, test data
- Conflict Risk: ZERO with other streams
- **Strategy:** Can work completely in parallel

### Conflict Resolution Priority

If conflicts occur, priority order:
1. **Stream 1** (Python 2→3) - Foundational, must complete first
2. **Stream 3** (Performance) - Critical path for rollout
3. **Stream 4** (Validation) - Required for rollout
4. **Stream 2** (C→Python) - Nice to have, not blocking

---

## Multi-Developer Workflow

### Scenario 1: Solo Developer
```bash
Week 1:
- Work on fix/standarderror-exceptions (Task 1.1)
- Merge to analysis-phase
- Work on validate/python3-imports (Task 1.2)
- Merge to analysis-phase

Week 2:
- Work on test/python3-smoke-tests (Task 1.3)
- Start convert/list-to-python (Task 2.1) in parallel
- Start validation/prepare-datasets (Task 4.1) in parallel
```

### Scenario 2: Team of 3 Developers

**Developer A (Stream 1 - Critical Path):**
```bash
Week 1:
git checkout fix/standarderror-exceptions
# Complete Task 1.1, merge
git checkout validate/python3-imports
# Complete Task 1.2, merge

Week 2:
git checkout test/python3-smoke-tests
# Complete Task 1.3, merge
```

**Developer B (Stream 2 - Conversions):**
```bash
Week 1:
git checkout convert/list-to-python
# Complete Task 2.1, merge
git checkout convert/diag-dbl-numpy
# Complete Task 2.2, merge
git checkout convert/eigenvalue-numpy
# Complete Task 2.3, merge

Week 2-3:
# Continue with Tasks 2.4-2.7
```

**Developer C (Stream 3 & 4 - Performance & Validation):**
```bash
Week 1:
git checkout validation/prepare-datasets
# Complete Task 4.1, merge

Week 2 (after Dev A finishes Task 1.2):
git checkout perf/testing-infrastructure
# Complete Task 3.1, merge

Week 3-4:
git checkout perf/contour-profiling
# Complete Task 3.2, merge
git checkout perf/contour-optimization
# Complete Task 3.3 (CRITICAL)
```

### Scenario 3: Team with Remote Contributors

**Main developer (on-site):** Handles critical path (Streams 1 & 3)
**Remote contributor(s):** Handle independent tasks (Stream 2)

```bash
# Remote contributor workflow:
git clone https://github.com/elkins/ccpnmr2.4.git
cd ccpnmr2.4
git checkout analysis-phase
git checkout -b convert/hash-list-python

# ... work on conversion ...

git add .
git commit -m "Convert hash_list.c to Python dict+list hybrid"
git push origin convert/hash-list-python

# Create pull request on GitHub
# Main developer reviews and merges
```

---

## Pull Request vs Direct Merge

### When to Use Pull Requests

**Use PRs for:**
- Remote contributors (code review required)
- Large/risky changes (second pair of eyes)
- Stream 3 tasks (performance critical, need validation)
- Stream 4 Task 4.3 (scientific validation, research team approval)

**Example PR template:**
```markdown
## Task: 3.3 - Optimize Contouring with Numba

### Changes
- Applied @numba.jit to marching cubes algorithm
- Optimized memory access patterns in contour generation
- Added chunking for large datasets

### Performance Results
- 3D contouring: 95% of C speed (target: 90%)
- 4D contouring: 88% of C speed (target: 90%)
- Memory usage: 1.2x C implementation (acceptable)

### Testing
- All tests pass: pytest tests/ --performance
- Numerical accuracy verified: rtol < 1e-6
- Smoke tests pass on production datasets

### Approval Needed
- [ ] Research team confirms performance acceptable
- [ ] Code review complete
```

### When to Direct Merge

**Direct merge for:**
- Stream 1 tasks (straightforward syntax fixes)
- Stream 2 tasks (well-defined conversions with tests)
- Solo developer (no review needed)
- Small, obvious fixes

---

## Branch Cleanup Strategy

### After Successful Merge

**Option 1: Delete immediately** (keeps repo clean)
```bash
git branch -d fix/standarderror-exceptions
git push origin --delete fix/standarderror-exceptions
```

**Option 2: Keep until project complete** (preserves history)
- Useful for understanding what was done
- Can recreate timeline from branch structure
- Delete all at once after MVM complete

**Recommendation:** Delete Stream 2 branches immediately (many small branches), keep Stream 1/3/4 until rollout complete.

---

## Emergency Scenarios

### Scenario 1: Need to Revert a Task

If Task 3.3 (contour optimization) causes problems:

```bash
git checkout analysis-phase
git log --oneline --graph

# Find the merge commit
*   ghi789 - Merge branch 'perf/contour-optimization'

# Revert the entire merge
git revert -m 1 ghi789
git push origin analysis-phase
```

### Scenario 2: Hotfix Needed During Development

Critical bug found while branches are in progress:

```bash
git checkout analysis-phase
git checkout -b hotfix/critical-bug-description
# ... fix the bug ...
git commit -m "Hotfix: Fix critical bug in ..."
git checkout analysis-phase
git merge hotfix/critical-bug-description
git push origin analysis-phase

# Update all active branches
for branch in fix/standarderror-exceptions convert/list-to-python; do
    git checkout $branch
    git merge analysis-phase
    git push origin $branch
done
```

### Scenario 3: Two Developers Modify Same File

Developer A and Developer B both modify `contour.py`:

```bash
# Developer B's branch
git checkout perf/contour-optimization
git merge analysis-phase
# CONFLICT in ccpnmr2.4/python/ccpnmr/analysis/contour.py

# Resolve manually
git add ccpnmr2.4/python/ccpnmr/analysis/contour.py
git commit -m "Merge analysis-phase and resolve conflicts"
git push origin perf/contour-optimization
```

---

## Branch Status Tracking

### View All Branches
```bash
# Local branches
git branch

# Remote branches
git branch -r

# All branches with last commit
git branch -a -v
```

### Check Branch Status Against Main
```bash
# Commits in branch not in analysis-phase
git checkout convert/list-to-python
git log analysis-phase..HEAD --oneline

# Commits in analysis-phase not in branch
git log HEAD..analysis-phase --oneline
```

### Visual Branch Graph
```bash
# See entire branch structure
git log --oneline --graph --all --decorate

# Filter to specific stream
git log --oneline --graph --all --decorate --branches="convert/*"
```

---

## Integration with Task Tracking

### Branch → Task Mapping

| Branch | Task | Priority | Status |
|--------|------|----------|--------|
| `fix/standarderror-exceptions` | Task 1.1 | P0 | ✅ Complete |
| `validate/python3-imports` | Task 1.2 | P0 | 🔄 In Progress |
| `test/python3-smoke-tests` | Task 1.3 | P0 | ⏸️ Blocked by 1.2 |
| `convert/list-to-python` | Task 2.1 | P1 | 🔄 In Progress |
| `convert/diag-dbl-numpy` | Task 2.2 | P1 | ⏳ Not Started |
| `perf/testing-infrastructure` | Task 3.1 | P0 | ⏸️ Blocked by 1.2 |
| ... | ... | ... | ... |

### Update Status Script

Create `scripts/branch-status.sh`:
```bash
#!/bin/bash
# Show status of all task branches

echo "Stream 1: Python 2→3 Completion"
for branch in fix/standarderror-exceptions validate/python3-imports test/python3-smoke-tests; do
    if git show-ref --verify --quiet refs/heads/$branch; then
        status="🔄 Active"
    elif git show-ref --verify --quiet refs/remotes/origin/$branch; then
        status="☁️ Remote"
    else
        status="✅ Merged/Deleted"
    fi
    echo "  $branch: $status"
done

echo ""
echo "Stream 2: C→Python Conversions"
# ... similar for other streams
```

---

## Best Practices Summary

### DO:
✅ Use `--no-ff` for merges (preserves history)
✅ Keep branches focused on single task
✅ Merge Stream 1 branches sequentially
✅ Merge Stream 2 branches as soon as ready (no waiting)
✅ Update branch from main before merging
✅ Write clear commit messages
✅ Delete branches after merge (Stream 2 especially)
✅ Use PRs for critical path (Stream 3) and validation sign-offs

### DON'T:
❌ Create branches not in the plan (stay organized)
❌ Mix multiple tasks in one branch
❌ Force-push to shared branches
❌ Merge Stream 3 branches out of order
❌ Forget to pull latest main before creating branch
❌ Skip testing before merging
❌ Leave stale branches around indefinitely

---

## Quick Reference

### Create Branch for Task
```bash
git checkout analysis-phase
git pull origin analysis-phase
git checkout -b <type>/<scope>-<description>
git push -u origin <type>/<scope>-<description>
```

### Merge Branch to Main
```bash
git checkout analysis-phase
git pull origin analysis-phase
git merge --no-ff <branch-name>
git push origin analysis-phase
```

### Delete Merged Branch
```bash
git branch -d <branch-name>
git push origin --delete <branch-name>
```

### Update Branch from Main
```bash
git checkout <branch-name>
git merge analysis-phase
git push origin <branch-name>
```

---

**Document Status:** Ready for implementation
**Last Updated:** December 2025
**Next Review:** After first week of task execution
