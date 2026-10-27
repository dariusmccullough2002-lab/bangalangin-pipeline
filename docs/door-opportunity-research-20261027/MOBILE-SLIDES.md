# Mobile slideshow spacing — October 27, 2026

Production style commit 83a8a80d058f0656e10b64b9948c18f76d469555; Vercel dpl_5DENGiGs6Vev6TiquS9Yt5f9dEh7 READY.

Root cause: layered phone rules set a 900px minimum and align-content:space-between, sending the artwork far below the copy. Below650px slides now use a flex column, content-sized minimum,28px gap and slightly responsive headings. Graphics remain side by side on single-player compositions. Controls stay beneath the track; desktop retains grid layout.

Live review: at390px outer frame all five slides744px high with28px copy-to-art gaps, formerly900px with95–323px gaps. At320px all five788px high with28px gaps, no overflowing copy; document clientWidth305 and scrollWidth305. At1200px desktop layout remains grid, height603px. Uniform track height can leave spare room below shorter artwork, while preserving consistent slide/control positions. Build and diff check passed. A browser reload was needed to replace the previously loaded stylesheet during review.

Proof: /workspace/scratch/pipeline-mobile-slides-compact-20261027.jpg. Temporary responsive review tab closed; actual homepage left open. No data or model changes.
