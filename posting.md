# Prompt - Investigate Correlation Between Posting and new Connections


You're a data analyst. I'm giving you two LinkedIn data exports and I want a rigorous answer to one question: is there a correlation between how often I post and how many new connections I gain, measured by month? If the files are not attached yet, ask me for them before analyzing.

The two files:
1. Shares.csv, my posts export. It has a Date column with exact timestamps. The ShareCommentary field contains multi-line text with embedded line breaks and doubled quotes, so parse it with a proper CSV reader rather than splitting on newlines, because a raw line count will massively overcount the real number of posts.
2. Connections.csv, my connections export. The standard LinkedIn format puts two or three preamble rows beginning with "Notes:" above the real header, so detect and skip them. The Connected On column is formatted like "29 Jun 2026" (day, abbreviated month, year).

Do the analysis in this order and show your work as you go.

First, parse both files, report how many posts and how many connections you successfully dated, and print the full date range of each series. Flag any rows you could not parse rather than dropping them silently.

Second, aggregate both to monthly counts: posts per calendar month, and new connections per calendar month. Align the two series on a shared monthly index running from my first post month through the latest month present in either file. Treat months inside that window with no posts as real zeros, not missing data. Do not include months before I started posting, since a stretch of forced zeros would distort the correlation. State the exact window and the number of months you end up with.

Third, calculate the correlation coefficient, and do not stop at a single number, because one coefficient can mislead on skewed time series that both trend upward over years. Report Pearson r on the raw monthly levels with its p value, Spearman rank correlation, Pearson r after removing a linear time trend from both series, and Pearson r on month-over-month changes (first differences). Then tell me in plain language what the spread across those four numbers implies about whether the relationship is linear, monotonic, or mostly an artifact of both quantities growing over time. Name any specific outlier months or years that pull the linear fit around.

Fourth, build the visualization as a single self-contained interactive artifact using d3 v7, with two linked panels. The top panel is a dual-axis monthly timeline: posts per month as bars on the left axis, new connections per month as a line on the right axis, sharing an x axis of time. The bottom panel is a scatter where each dot is one month, posts on x and new connections on y, with an ordinary least squares fit line drawn through it and the Pearson r annotated on the plot. Add a small header showing the total posts, total connections, the month window, and the four correlation coefficients. Hovering any bar, point, or dot should show that month with its post count and connection count. Render it on a dark neutral canvas (deep slate, not black) with light labels and a clean sans-serif, favoring legibility over decoration, and do not use a cream or parchment background.

Close with an interpretation that is honest about limits: state clearly that correlation is not causation, that audience size and platform reach and role changes plausibly drive both series at once, and whether posting looks more like a same-month association or a leading indicator of connections in later months. If a lag analysis (this month's posts against next month's connections) would sharpen the answer, say so and offer to run it.

Do not invent numbers, months, or people. Every figure and every point on the chart must come from the files. Before you finish, re-check that the totals in the chart header match the parsed data, that the monthly series feeding the chart are the same ones you ran the correlations on, and that the reported window matches the aligned index.

Think before answering (maximum reasoning)