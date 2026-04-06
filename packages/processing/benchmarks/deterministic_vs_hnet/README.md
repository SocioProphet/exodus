# deterministic_vs_hnet

Executable benchmark skeleton for comparing the deterministic canonical chunker
against an H-Net adaptive chunk overlay.

Inputs:
- corpus manifest
- retrieval query set
- retrieval ground truth
- per-system chunk assignments or retrieval outputs

Outputs:
- benchmark run JSON
- per-system metrics JSON
- optional markdown summary
