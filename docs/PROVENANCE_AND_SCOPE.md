# Provenance and scope

`metadata/provenance.csv` associates packaged files with source identifiers, source SHA-256 values and transformations. `metadata/SHA256SUMS.csv` records packaged-file hashes. `metadata/checkpoints.csv` lists the 240 original checkpoint members; `checkpoint_archives.csv` identifies the 11 optional ZIP assets and their hashes.

The sources are the pre-existing local Fluent models, original three-grid continuation records, dense-coarse monitoring, corrected exact-section timestep extraction, outlet sensitivity records and manuscript figure exports. Original source files were preserved. Meshes and case/data files were copied byte-for-byte. Readable residual transcripts were redacted to remove workstation paths/identifiers; data extraction and figure-source corrections are labeled in the provenance table.

## Corrections to earlier package metadata

- Three-grid continuation settings are dt=0.01 s and maximum 30 inner iterations. Earlier 0.001 s / 150-iteration descriptions do not describe these supplied continuations.
- Saved baseline pressure-outlet inputs are free-surface elevation 0.0822 m and bottom elevation -0.468 m. Earlier 0.1572/-0.393 settings are superseded for these files.
- The mesh is axis-aligned and uses an axial gravity component; longitudinal engineering bed elevations include the slope correction.
- Figure 3-3 and `exact_section_corrected.csv` supersede the earlier dt=0.01 s midpoint-depth extraction. Preserved Excel workbooks can still contain that older extraction and should not override the corrected CSV.
- Figure 3-6 is Manning-based analytical sensitivity, not CFD output from multiple roughness cases.

## Availability boundaries

No unverified CAD or mesh-generation history was invented. The baseline history begins at 33.55 s; absent early-time records were not reconstructed. A complete signed-flux/storage closure table and independent site-acceptance measurements are not included. The outlet scenarios are numerical boundary comparisons; actual downstream tailwater remains unmeasured in the supplied evidence.

Private connection JSON files, active server credentials and license configuration were excluded. Native HDF5 case/data files were not rewritten for anonymization and can retain internal historical paths; readable logs were redacted. Before public release, the authors should confirm ownership and sharing rights for the supplied model and engineering materials.

Outlet-scenario monitor rows retain external intermediate-checkpoint identifiers. Those boundary intermediate fields are not part of the 11 three-grid checkpoint assets; the three boundary final 160 s fields are included. The prepared package does not imply that every field referenced by a source monitor was bundled.
