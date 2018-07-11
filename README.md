# Benchmark Harness
Harness to run benchmarks with options for different machines and different compilers

## Usage

The benchmark controller receives all parameters via command line options, which define:
 * The name of the benchmark
 * The type of machine to run on
 * The compiler to be used
 * Environment (compiler flags, paths, etc)

This is a modular harness, so in order to run a benchmark, you need to add a module that knows that benchmark. It won't be able to recognise random benchmarks, know how to build and run it, so all of that has to be encoded as modules in the structure.

Benchmarks modules need to know how to fetch it (git clone, wget, etc), build (using the compiler + special flags) and run (and how many times to run, etc).

Machine modules are mostly structures with extra values for required compiler flags, pre/post benchmark logic and specific knowledge (for example modules to load, /sys and /proc handling, etc. as well as uArch options, for example --mtune).

Compiler modules need to either get a tarball and unpack it or use the system compiler. It also needs to know how to identify the compiler (ex. gcc vs clang) and if there are any special flags that need to be used.

The controller will then get the benchmark and compiler, build the sources, run as many times and as many combination of flags  as necessary and bundle the results into a directory, which will then be copied into a safe place (TBD).

## Extending

To extend functionality, either add new benchmark/machine/compiler modules or improve the relationship between them, so that the right decisions fall out in the right places.

As we move this script to production, we'll require more and more testing before changes can be merged in. Once that happens, we'll have a few 'stable' branches, with what's in production at different sites, master as the "new version" and diverse branches for testing new features.

We encourage automation jobs to be able to select the branch it's using, so that you can run tests without breaking anyone's production (including yours).
