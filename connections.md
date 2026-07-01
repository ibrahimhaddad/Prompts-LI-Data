# Prompt - Analyse LI Connections

You're a data analyst working with my exported LinkedIn connections. I'm giving you my Connections.csv from LinkedIn. If it isn't attached yet, wait for the file before doing any analysis.

Read the actual attached file rather than assuming its structure, but expect the standard LinkedIn export format: two or three preamble rows beginning with "Notes:" sit above the real header, so detect and skip them. The real columns are First Name, Last Name, URL, Email Address, Company, Position, Connected On. Some rows have a blank Company; keep those and label them "Independent / Unknown."

Do two things.

First, cluster and summarize. Group my connections by current company using the Company field. Normalize before grouping: trim whitespace, unify casing, and collapse obvious variants of the same employer (for example "Google" and "Google LLC") into one cluster, then tell me which merges you made so I can check them. Give me the top 20 clusters by connection count as a ranked table with four columns: rank, company, number of connections, and share of my total connections as a percent. Below the table, add a two or three sentence read on what the distribution says about my network, covering concentration, notable hubs, and the long tail. Grouping by inferred industry would tell a different story, but default to company clusters since that field is exact while industry has to be inferred; if the industry view looks materially more revealing, say so in one line and offer to regroup.

Second, build a force-directed network visualization as a single self-contained interactive artifact using d3 v7. Structure it as one central node for me, one hub node for each of the top 20 company clusters, and leaf nodes for the individual people inside those 20 clusters. Roll everyone outside the top 20 into a single "Other" hub so the graph stays readable and fast. If the combined top-20 population is large (more than roughly 1500 people), cap leaves at 40 per hub and note the cap in a caption, because rendering thousands of nodes in the browser gets sluggish and degrades the layout.

For design and interaction: size each hub by its connection count using a square-root scale so the largest cluster doesn't visually swallow the rest, color hubs categorically with one distinct color each, and give every leaf the color of its hub. Make my central node clearly distinct in shape or outline. On hover, show cluster name and count for a hub, or name and position for a leaf. Support dragging nodes and zooming and panning the canvas. Clicking a hub should highlight it and its leaves and dim everything else, and clicking empty space should reset. Include a ranked legend of the 20 clusters with their counts, plus a compact stats header showing total connections, the number of distinct companies after normalization, and the single largest cluster. Render it on a dark neutral canvas (deep slate, not black) with light labels and a clean sans-serif font, favoring legibility and contrast over decoration. Do not use a cream or parchment background.

Do not invent people, companies, or counts. Every number and node must come from the file. Where a field is missing or ambiguous, handle it explicitly and tell me how rather than guessing silently.

Before you finish, re-read the table and the visualization against the file: confirm the counts in the legend match the table, the percentages are consistent with my total connection count, and the normalization merges you reported are actually reflected in the clusters.

Ask me to attach the file if it isn't already here.

Think before answering (maximum reasoning)
