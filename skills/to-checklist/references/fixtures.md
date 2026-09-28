# Building a Test Fixture

## 1. Start from what exists

Ask whether the user already has a test document for this project. It may have been renamed or moved. If they do, reuse it and extend it until it covers every Check.

## 2. Build it inside the application

Build the fixture live in the running application, through its bridge or scripting (an MCP server, a script console, the application's API). Ask the user to open a fresh document first.

Writing the file format yourself is the fallback, because the application may reject the version: a `.3dm` written that way came out as format version 7, while MoI 3D reads only version 5 or lower. When a file is the only way, write the version the application reads, and have the user open it once before you hand over the Checklist.

If you can neither drive the application nor write a file it opens, put numbered build instructions into the Checklist's `setup.steps`.

## 3. Name and lay out every element

- Give each case its own named group, layer or page, named for the case it represents, e.g. `G1 cube frame`, `G4 tight pair`. When an element serves only one Check, prefix its name with that Check's ID, e.g. `CHK03_fillet_edge`.
- Space the cases apart, or label them with text in the document, so the user finds each one without searching.
- Several fixtures are fine, e.g. a source file and a target file. Name each one in Setup, and let each Check's `use` say which fixture and which element it needs.

## 4. Describe it in Setup

Fill `setup.fixtures` in the Checklist DATA:

- one row per group: what to select, how many objects it holds, and what it is, in plain words;
- `notes`: the units, the default parameter values the Checks assume, and the object count before any run, so objects a run leaves behind show up;
- how to select a group, e.g. "click its name in the Objects panel; hold Ctrl to add a second group".

## 5. Prove the fixture triggers each case

You may be able to run the project's own logic on the fixture's content outside the application, e.g. the planner module that the plugin calls. If so, write a small script that asserts each group produces its intended case: "G1 must build clean", "G4 must fail its joint", "the lattice must survive with three frames dropped". Run it before handing over the Checklist, and keep it next to the fixture as `check-fixture-covers-cases.<ext>`.
