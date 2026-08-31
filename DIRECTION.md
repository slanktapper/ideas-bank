# ideas-bank — direction

A bank of independent ideas, tools, and experiments, developed with Claude Code.

Each idea gets a folder named with its **short name**. Folders are self-contained —
their own stack, their own tooling, their own `direction.md`. They do not share code
or data unless a deliberate decision was made to connect them.

The root holds direction `.md` files and project folders. Nothing else.

See `CLAUDE.md` for the working rules, and `available-tools.md` for the physical and
fabrication capability any project can draw on — there is a 3D printer and a blade
cutter, so not every idea here has to be software.

## Project registry

The short name is the folder name and how projects are referred to in conversation.
The filesystem is the source of truth for which projects exist; this table adds the
one-line description. Add a row when you create a project.

| Short name | Description | Status |
| --- | --- | --- |
| 3dresearch | Research into 3D printers — machines, technologies, materials, costs | working |
| gridfinity-negatives | Scan or photograph a tool, get a Gridfinity bin with its shape cut into it | prototype |

Status values: `idea`, `prototype`, `working`, `parked`, `retired`.
