# GitHub publication plan

This is a local release preparation; no repository, Release or DOI has been created by this task.

1. Fill `metadata/release_metadata.json`: authors, formal project name, repository URL and chosen licenses. Confirm rights to share the engineering data/model. Adopt actual license files only after these choices are made; templates are not licenses in force.
2. Use the **source ZIP** as the repository seed. Keep one top-level project directory, initialize Git there, and commit its small files. Review for files above GitHub's normal 100 MiB per-file limit. The provided workflow checks the source CSVs on pushes and pull requests.
3. Create a versioned GitHub Release after checking the source tree. Attach main.zip and the 11 checkpoint ZIPs as binary assets; source.zip is optional convenience. Each prepared checkpoint ZIP is below 2 GiB. Do not put binary model assets in ordinary Git history. The optional ZIPs are independently extractable, so reviewers can retrieve one grid or time window.
4. Attach RELEASE_ASSETS.csv and the release index with archive names, sizes and SHA-256 values. Use a version tag consistently in README, citation and metadata.
5. Fill `CITATION.cff.template`, validate it, and rename it to `CITATION.cff` only when real authors and project information exist. Never use placeholder authors or invented DOI identifiers in the published citation.
6. For a persistent scholarly archive, archive the released data through Zenodo or an appropriate repository, checking its storage limits for the roughly 15 GiB of intermediate fields. Obtain a DOI only after actual deposition. GitHub URLs and DOI links should resolve before updating a manuscript availability statement.
7. Test by downloading into a fresh directory, running the CSV verification, checking asset SHA-256 values and opening representative matching case/data pairs in the intended Fluent version. Record the installation and any numerical differences if an actual solver rerun is performed.

License templates and citation placeholders deliberately remain incomplete because the author/repository details have not been determined.
