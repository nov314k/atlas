# _Atlas_ portfolio syntax and structure

To better understand _Atlas_ portfolio syntax and structure, it is recommended to first read [Atlas rationale](atlas-rationale.md).

_Atlas_ files are plain text files with UTF-8 encoding.

_Atlas_ general syntax is loosely based on the Markdown syntax, and _Atlas_ task syntax is very much derived from the [todo.txt](http://todotxt.org/) task format.

## Portfolio

An _Atlas_ portfolio is a collection of different kinds of files:

* Life area files
* Daily tasks file.
* Auxiliary files
* Log files

Due to the nature of the problem that _Atlas_ is solving, an _Atlas_ portfolio is put together for a single person.

## Files

### Life area files

Life area files contain goals. A single file may contain goals pertaining to one life area, or they may contain goals from a number of life areas. The way that goals are grouped into files can have a small difference in the way in which tasks are prioritized, and also in the way in which new tasks are recorded.

_Atlas_ files are plain-text files and they have a **.pmd.txt** extension. Maximum line length is 120 characters.

At the beginning of each file, there is the TTL heading (`# TTL #` by default), followed by two blank lines. The meaning of this section will be explained later.

Following the TTL section, there is the INCOMING heading (`# INCOMING #` by defaule), followed by two blank lines. The meaning of this section will also be explained later.

Every file ends with a line that contains only `# THE END #`, followed by one blank line.

Note that all section headings begin with a `#` symbol. Note that 'official' or 'reserved' headings also end with a `#`.

All heading text, as well as the prefix and suffix symbols (`#` by default) are configurable via the settings file.

### Daily tasks file

Daily tasks file starts with the _TTL for_ heading (by default `# TTL for YYYY-MM-DD`), and finishes with the _DONE on_ (by default `DONE on YYYY-MM-DD`) heading. Contents of both of these headings is configurable. In between these two headings tasks are listed in the order of their priority.

### Auxiliary files

There are four auxiliary files internally used by _Atlas_:

* `daily_file`
  * This is an extract of all daily tasks
* `booked_file`
  * This is an extract of all non-periodic tasks that have a due date
* `periodic_file`
  * This is an extract of all periodic tasks
* `shlist_file`
  * This is the shopping list.

Names and locations of these files are configurable via the settings file.

## Goals

Goal definitions start with a `#` symbol, followed by a brief specification of the goal. Specification of a goal can be underlined by a row of `#` symbols. Goal specifications are written in imperative mood.

## Signposts and composite tasks

Signpost and composite task definitions start with `##` (two hashes), followed by a brief specification of the signpost or composite task. They can be underlined by a row of `#` symbols. Composite tasks and signposts are written in imperative mood.

## Tasks

_Atlas_ tasks consist of:

* Prefix character
* Task definition
* Properties
* Tags
* Parallel markers (optional).

Each one of these task properties are further specified below.

### Prefix character

Prefix character represents the state of the task and it can be one of:

* `-`
  * Open task
* `x`
  * Finished task
* `t`
  * Open task with a high priority
* `r`
  * Task marked for rescheduling (used only in daily tasks list only)
* `R`
  * Periodic task reschedulled (used in daily tasks list only)
* `|`
  * Paused task
* `\`
  * Task in development

Tasks with a `-` or a `t` prefix are collectively known as **active tasks*.

### Task definition

### Properties

The following task properties are supported:

* Duration
  * `dur:M`
  * `M` is the duration of a task in minutes (any number of minutes can be specified)
  * Duration of a task is a property that must be specified for any active task
  * For tasks where the duration is unknown, it is recommended to use `0`
  * For consistency, it is recommended to put the `dur` property immediately after the task definition
* Due date
  * `due:YYYY-MM-DD`
  * Due date of a task is an optional property
  * If a task has a due date property, it is known as a **booked task** or a **due task**
  * For consistency, it is recommended to put the `due` property immediately before the task definition, and after the task prefix
* Recurrence
  * Recurrence is used to specify that a task repeats itself in certain time intervals
  There are two types of recurrence: relative and absolute
  * Relative recurrence
    * `rec:XP`
    * `X` is the length of recurrence, and `P` is the period of recurrence
      * Period of recurrence `P` can be one of `d` (day), `m` (month), and `y` (year)
      * For example, a property of `rec:28d` means that a task is to be repeated every 28 days
    * For relative recurrence, the next due date of a task is calcualted from the day that the task is marked as done
  * Absolute recurrence
    * `rec:+XP`
    * The only difference between relative and absolute recurrence property specification is that absolute recurrence, denoted by `+` is calculated from the original task due date.

While task properties can be placed anywhere on the task line, we have recommended above certain placement suggestions, for the sake of consistency.

### Tags

Tags begin with `+` and they further classify and categorize a task. A common aim of tags is the denote to which goal, signpost, or life area the task belongs.

### Sequencing markers

Sequencing markers start with `@` and they are used to help _Atlas_ evaluate task priority.

## Blank lines, comments, text, and info lines

Blank lines in all files are ignored.

If there are no tasks listed in these sections, there must be two blank lines after the following headings: _TTL_, _INCOMING_, and _TTL for_.

Lines that start with a semicolon (`;`), followed by a space, are considered to be comment lines and they are ignored.

Lines that contain only three consecutive semicolons (`;;;`) in columns 0, 1, and 2 are considered to be the start of a multiline text section.

Lines that contain only six consecutive semicolons (`;;;;;;`) in columns 0-5 are considered to be the end of a multiline text section.

Lines that start with a greater-than symbol (`>`), followed by a space, are considered to be info lines in which _Atlas_ is providing information to the user.


