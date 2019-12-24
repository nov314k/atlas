# _Atlas_ syntax and structure

To better understand _Atlas_ syntax and structure, it is recommended to first read [Atlas rationale](atlas-rationale.md).

_Atlas_ syntax is loosely based on the markdown syntax.

## Files

Files contain goals. A single file may contain goals pertaining to one life area, or they may contain goals from a number of life areas. _Atlas_ files have a **.pmd.txt** extension. The way that goals are grouped into files can have a small difference in the way in which tasks are prioritized, and also in the way in which new tasks are recorded.

At the beginning of each file, there is a `# TTL #` heading, followed by two blank lines. The meaning of this section will be explained later.

Following the TTL section, there is an `# INCOMING #` heading, followed by two blank lines. The meaning of this section will also be explained later.

Every file ends with a line that contains only `# THE END #`, followed by one blank line.

Note that all section headings begin with a `#` symbol. Note that 'official' or 'reserved' headings also end with a `#`.

## Goals

Goal definitions start with a `#` symbol, followed by a brief specification of the goal. Specification of a goal can be underlined by a row of `#` symbols.

## Signposts and composite tasks

Signpost and composite task definitions start with `##` (two hashes), followed by a brief specification of the signpost or composite task. They can be underlined by a row of `#` symbols.

## Tasks

