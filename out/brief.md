# Weekly Experimentation Brief

**Week of 2026-06-24 to 2026-06-30** · Performance Marketing · Google Ads, LinkedIn Ads, Meta

> Synthetic sample data. Not Harvey performance.
> Replay of a recorded run for offline demos and tests. Not a live model run.
> **Nothing in this brief has been launched.** 3 experiments are staged as drafts and wait for a person to approve, edit or reject.

## The headline

Google's budget moved from Webinar to Demo over the last 8 weeks, yet in settled campaigns Google Webinar returns 3.2x the pipeline per dollar of Google Demo. No campaigns are scheduled past Jun 30, so the next launches decide whether that gets corrected. `[SIG.01, WEEK.program_status]`

## What happened last week

- Spend fell 53% week over week to $17,013 across 9 campaigns. Almost all of the drop is campaigns ending: the 6 campaigns live through both weeks were flat on spend. `[WEEK.totals, WEEK.spend_bridge, WEEK.same_store]`
- Like for like, CTR slipped from 2.18% to 1.97% and conversions went from 60 to 57. Delivery softened slightly and lead capture held. `[WEEK.same_store]`
- Qualified leads, opportunities and pipeline for the week cannot be judged yet. Inside the lag window, qualified leads are only 27% of what their conversions would normally produce. `[DQ.attribution_lag]`
- The program is winding down. 6 campaigns were still live on Jun 30, 0 are scheduled past it, and weekly spend is down 91% from the peak week. `[WEEK.program_status]`
- C119 on LinkedIn is running 24% below its own CTR baseline at 60 days old, past the point where LinkedIn creative starts to wear out. `[WEEK.campaigns, FATIGUE.curve]`

## Why it happened

- Offer is the biggest lever. In settled campaigns Webinar returns 1.42x comparable campaigns and Demo 0.46x, and the gap holds on all 3 platforms. Demo still takes 49% of spend. `[SEG.objective]`
- Google moved the wrong way. Webinar fell from 55% to 5% of Google spend while Demo rose from 42% to 92%. The only test favoring Demo, E013, ran 5 days on a sample of 31 and is rejected. `[MIX.objective, EXP.E013]`
- LinkedIn takes 31% of settled spend and returns 0.06x comparable campaigns. 24 of its 41 settled campaigns produced no opportunities. `[SEG.platform, ZERO.opportunities]`
- Meta buys leads at $10 each but only 30% qualify, against 63% on Google, so its low cost per lead overstates its value. `[FUNNEL.platform]`
- Region is not a driver. DACH looks weak on raw numbers, but like-for-like indexes run from 0.93x to 1.10x once platform and offer are held constant. `[SEG.region]`

## The three experiments to run next

### 1. Webinar vs Demo offer on Google for Law Firm Enterprise

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** For the same audience and the same ROI message, a webinar offer produces more pipeline per dollar than a demo offer.

**Why this test.** Google Webinar returns 3.2x the pipeline per dollar of Google Demo in settled campaigns, yet Demo is now 92% of Google spend. The only test behind that shift is a rejected false winner, so this is the largest budget decision resting on no valid evidence. `[SIG.01, MIX.objective, EXP.E013]`

| | |
|---|---|
| Where | Google · Law Firm - Enterprise · US |
| Control | Demo offer with the ROI message (Book Demo, CR001) |
| Variant | Webinar offer with the ROI message (Register, CR001) |
| The one thing that differs | objective |
| Primary metric | Pipeline per $ |
| Guardrail metrics | Cost per lead, CTR, Qualified lead rate |
| Budget | $600 per arm per day for 28 days ($33,600 in total) |
| Expected volume | Control: about 519 qualified leads, 109 opportunities; Variant: about 929 qualified leads, 265 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42. If Webinar's pipeline per dollar is at least 25% higher than Demo's, make Webinar the default Google offer for this audience. If the arms are within 25% of each other, keep both and repeat on a second audience. If Demo is at least 25% higher, keep the current mix. |
| Evidence | SIG.01, SEG.platform_objective, MIX.objective |
| Re-test of | E013 |

**What we learn either way.** If Webinar wins, Google's default offer switches back and the budget follows. If Demo holds up under a valid test, the team keeps the current mix with real evidence behind it.

### 2. Content Download vs Webinar offer on LinkedIn for Law Firm Enterprise

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review, 2 warning(s).

**Hypothesis.** On LinkedIn, a content download offer produces opportunities at a lower cost than a webinar offer for the same audience and message.

**Why this test.** LinkedIn Demo returns $5 of pipeline per dollar and cannot be tested within the budget ceiling, so the affordable question is which other offer LinkedIn should run. E003 favored Webinar, but in settled LinkedIn campaigns Webinar returns 0.60x the pipeline per dollar of Content Download. `[SEG.platform_objective, EXP.E003]`

| | |
|---|---|
| Where | LinkedIn · Law Firm - Enterprise · US |
| Control | Webinar offer with the ROI message (Register, CR002) |
| Variant | Content download offer with the ROI message (Download Guide, CR002) |
| The one thing that differs | objective |
| Primary metric | Cost per opportunity |
| Guardrail metrics | Cost per lead, Qualified lead rate, CTR |
| Budget | $750 per arm per day for 35 days ($52,500 in total) |
| Expected volume | Control: about 127 qualified leads, 12 opportunities; Variant: about 227 qualified leads, 25 opportunities |
| Earliest valid read | Day 49 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 49. If Content Download's cost per opportunity is at least 30% lower than Webinar's, make it the default LinkedIn offer and confirm on pipeline at day 90. If neither arm gets within reach of Meta's cost per opportunity in settled campaigns, recommend moving LinkedIn budget to Google and Meta. |
| Evidence | SEG.platform_objective, SEG.platform, EXP.E003 |
| Re-test of | E003 |

**What we learn either way.** It tells the team which offer gives LinkedIn its best chance before any decision to cut the channel, and it settles a directional result that campaign data disagrees with.

- Guardrail warning (sample_size): Control: expect about 12 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

- Guardrail warning (sample_size): Variant: expect about 25 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

### 3. Role-targeted vs current targeting on Meta for Law Firm Enterprise

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Meta, targeting legal roles directly produces opportunities at a lower cost than the current audience, even though each lead costs more.

**Why this test.** Meta has the lowest cost per lead at $10 but only 30% of its leads qualify, against 63% on Google. E007 found that broad targeting produced lower-quality leads, but it ran 18 days on a sample of 160 and is only directional. `[FUNNEL.platform, EXP.E007]`

| | |
|---|---|
| Where | Meta · Law Firm - Enterprise · US |
| Control | Webinar offer with the ROI message, shown to the audience as targeted today (Register, CR002, Current legal-interest audience, as configured today (channel owner to confirm)) |
| Variant | Webinar offer with the ROI message, shown to a role-targeted audience (Register, CR002, Role-targeted: general counsel, legal operations leaders and law firm partners) |
| The one thing that differs | targeting |
| Primary metric | Cost per opportunity |
| Guardrail metrics | Cost per lead, Qualified lead rate, CTR |
| Budget | $500 per arm per day for 28 days ($28,000 in total) |
| Expected volume | Control: about 376 qualified leads, 86 opportunities; Variant: about 376 qualified leads, 86 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42. If the role-targeted arm's cost per opportunity is at least 20% lower, make role targeting the Meta default even if cost per lead rises. If it is within 20%, keep current targeting. A higher cost per lead alone is not a reason to stop. |
| Evidence | FUNNEL.platform, EXP.E007, SEG.platform |
| Re-test of | E007 |

**What we learn either way.** It shows whether Meta's lead-quality gap is a targeting problem the team can fix, or a property of the channel that should cap how much budget it gets.

## Creative recommendations

- Make ROI the default message. It returns 1.29x comparable campaigns, is above benchmark in 6 of 6 platform and offer cells, and two trusted tests agree. `[SEG.theme, EXP.E001, EXP.E014]`
- Refresh paid-social creative on a schedule. Meta CTR holds for 6 weeks and LinkedIn for 7 before it decays. CR021, the one active creative that has never run, is available as a fresh variant for Law Firm audiences. `[FATIGUE.curve, CREATIVE.gaps]`
- Pull back on Customer Proof until it is re-tested. It returns 0.75x comparable campaigns, yet it took 24% of spend in the last 8 weeks. `[SIG.11, EXP.E009]`
- Keep Security at exploration level. It returns 0.65x comparable campaigns, exists only in Static, and has no valid test behind it. Do not commission new formats until a small test says it is worth it. `[SEG.theme, CREATIVE.gaps, EXP.E011]`
- Build on product UI rather than stock photography, and use a customer logo wall rather than a quote card for enterprise audiences. Both come from trusted tests. `[EXP.E005, EXP.E016]`

## Risks and observations

- The daily and summary tables disagree on outcomes: the daily table carries only 16% of conversions and 3.5% of pipeline. Every efficiency figure here assumes the summary is the reconciled record, which the data owner should confirm. `[DQ.reconciliation]`
- LinkedIn Demo could not be tested within the budget ceiling. It is 23% of settled spend at $5 of pipeline per dollar, so the team faces a decision without a test: pause it, or approve a larger test budget. `[SEG.platform_objective]`
- Do not read LinkedIn's numbers as proof the channel has no value. Platform attribution can under-credit channels that influence enterprise deals, which is why the recommendation is to test before cutting. `[ZERO.opportunities]`
- Three learnings the team may be relying on point the other way in settled campaign data: E003, E004 and E009. None is overturned, but each deserves a confirmation test before it shapes a plan. `[EXP.summary]`
- Campaign-to-experiment links are unreliable. 42 of 60 linked campaigns point to an experiment on a different platform, so no result in this brief was attributed through those links. `[DQ.experiment_links]`

## What the data cannot tell us yet

- **Recent downstream data is incomplete.** Everything from Jun 17 to Jun 30 is inside the attribution lag window (source flag). Measured against each campaign's own prior 28 days, conversions in the window are 96% of what their clicks would normally produce, but qualified leads are only 27% of what their conversions would normally produce (10 of 10 comparable campaigns are below their own baseline). Lead capture is current; qualification and everything after it is not. 14 campaigns carry the immature flag in the summary. `[DQ.attribution_lag]`
- **Daily and summary files disagree on outcomes.** Spend, impressions and clicks reconcile exactly between the daily and summary tables, but the daily table carries only 16% of conversions, 13% of qualified leads, 4% of opportunities and 3.5% of pipeline. `[DQ.reconciliation]`
- **Some campaigns have no daily outcome data at all.** 20 campaigns show zero conversions in the daily table while the summary credits them with 2,403 (20 on LinkedIn), and 73 campaigns with opportunities in the summary show none in the daily table. `[DQ.daily_outcome_gaps]`

## Assumptions

- **A1.** The campaign summary is the CRM-reconciled record of lifetime outcomes. The daily table is a partial, same-day view of outcomes.
- **A2.** 'Last week' is the 7 days ending on the latest date in the data, compared with the 7 days before.
- **A3.** Anything the source flags as immature is excluded from performance judgments and efficiency benchmarks.
- **A4.** Pipeline per dollar is the primary success metric, supported by cost per opportunity and ARR per dollar. CTR, CPC and cost per lead are diagnostics only.
- **A5.** In the experiment log the first-named arm is the variant, so 'Win' on 'A vs B' means A beat B.
- **A6.** Absolute dollar magnitudes are synthetic. Ratios between segments are the signal.
- **A7.** An experiment needs at least 14 days and a sample of 100 to count as a read; a new test needs at least 28 days.
- **A8.** No proposed test may exceed the highest daily budget the team has already run, or a fixed total budget ceiling.

## How this brief was produced and checked

- Facts: computed by the analysis engine from the `sample_csv` source. 69 evidence items.
- Writing and experiment design: `scripted-fixture` (replay run), 4 turns, 1 submission of the brief.
- Claim check: every number in 24 claims was matched to the evidence it cites.
- Guardrails: 3 experiments passed every rule. The best possible verdict is 'ready for human review'.
- Held back: nothing. No claim or experiment was removed.
- This is a replay of a recorded run, used for offline demos and tests. Run with an API key for a live brief.

### Agent steps

- Turn 1: read SEG.platform_objective, SEG.objective, MIX.objective, SEG.platform, FUNNEL.platform, WEEK.campaigns, FATIGUE.curve, EXP.E003, EXP.E007, EXP.E013
- Turn 1: read the creative library
- Turn 2: 'Webinar vs Demo offer on Google for Law Firm Enterprise' cleared for human review
- Turn 2: 'Content Download vs Demo offer on LinkedIn for Law Firm Enterprise' blocked: decision_rule; sample_size
- Turn 2: 'Role-targeted vs current targeting on Meta for Law Firm Enterprise' cleared for human review
- Turn 3: 'Content Download vs Webinar offer on LinkedIn for Law Firm Enterprise' cleared for human review with 2 warning(s)
- Turn 4: brief accepted on attempt 1
