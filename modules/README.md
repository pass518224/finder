Module System
====

Module system provide extended function for Finder.

Finder export some hook functions helping for developer of module to inspect the solving of finder.

Usage
----

### load the module

Load the module with function `add()`

    import lib.Module as Module
    Module.getModule().add("TimeSlicer")

### Entry function -- module_init

Module system start with function `module_init()`.

The system call this function, and expect to receive a dict with function pointer.
The dict must only contain the hook function names.
The value of dict are function pointer implemented by the module.

    def module_init():

        descriptor = {
            "SOLVING_START" : solve_start,
            "SOLVING_SUCCESS" : solve_success,
            "SOLVING_FAIL" : solve_fail,
            "FINDER_END" : end,
        }
        return descriptor

### function pointer

The implemented function pointers must satisfy the required arguments.

Current modules
----

### Statistic

The module is used to count the solving rate of Finder.
At the `end()` function will write the result to the file

### TimeSlicer

This module statistic the total amount of type of ICC with time quantum.
The config of this module is at `TimeSlicer.ini`.

