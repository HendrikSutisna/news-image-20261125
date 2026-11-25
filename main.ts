// News-image entry (Node 22, standard library only): the image lives beside
// this file as entry.png, and the program copies it to the output path the
// grader provides. Deterministic: the same bytes out on every run.
import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'),
);
