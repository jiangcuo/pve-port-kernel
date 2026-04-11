# Extra Kernel Modules

Place out-of-tree kernel module source directories here. The build system will
**automatically discover and build** every module that has a `module.conf`.

## Directory Convention

```
modules/
  r8125/
    module.conf        # Required — tells build system where the Kbuild Makefile is
    src/
      Makefile         # Kbuild Makefile (obj-m := r8125.o)
      *.c *.h
  megaraid/
    module.conf
    Makefile           # Kbuild Makefile at top level
    *.c *.h
```

### module.conf

Each module directory **must** contain a `module.conf` file:

```bash
# Path to the Kbuild Makefile, relative to this module directory
# Use "." if Makefile is at the module root, "src" if in src/ subdirectory
MODSRC=src
```

The Makefile at `MODSRC` must be compatible with:
```bash
make -C /path/to/kernel M=/path/to/module/<MODSRC> modules
```

Modules without `module.conf` are **skipped**. If `MODSRC` points to a path
without a Makefile/Kbuild, the build will **error out**.

### Resulting .ko files

All `.ko` files are installed to `/lib/modules/<KVNAME>/extra/<module_name>/`
inside the main `pve-kernel-<KVNAME>` package.

## Example: Adding r8125

```bash
cd modules/
git clone https://github.com/xxx/r8125.git
echo "MODSRC=src" > r8125/module.conf
```

Then rebuild:
```bash
bash autobuild.sh aarch64
```
