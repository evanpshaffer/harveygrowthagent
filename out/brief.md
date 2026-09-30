# Weekly Experimentation Brief

**Week of 2026-06-24 to 2026-06-30** · Performance Marketing · Google Ads, LinkedIn Ads, Meta

> Synthetic sample data. Not Harvey performance.
> **Nothing in this brief has been launched.** 3 experiments are staged as drafts and wait for a person to approve, edit or reject.

## The headline

Google budget moved from Webinar to Demo, and Demo now takes 92% of Google spend. In settled campaigns Google Demo returns $612 of pipeline per dollar against $1,953 for Webinar, so the team needs a clean head-to-head before spending more on Demo. `[MIX.objective, SEG.platform_objective]`

## What happened last week

- Nine campaigns spent $17,013 in the week of Jun 24 to Jun 30, down 53% from $36,140 the week before. They produced 86 conversions, down 67%. `[WEEK.totals]`
- Almost all of the spend drop came from campaigns that ended or wound down, not from changes inside live campaigns. The 6 campaigns live both weeks held spend within 1%, while CTR slipped from 2.18% to 1.97%. `[WEEK.spend_bridge, WEEK.same_store]`
- The program is winding down: 6 campaigns were live on Jun 30 and none are scheduled past it. Weekly spend is down 91% from the March peak. `[WEEK.program_status]`
- Lead capture is current, but qualified leads, opportunities and pipeline for this week are provisional. Qualified leads in the window are only 27% of what conversions would normally produce, so this week gives no read on outcomes. `[DQ.attribution_lag]`

## Why it happened

- The offer mix on Google flipped. Webinar fell from 55% to 5% of Google spend and Demo rose from 42% to 92% over the last 8 weeks versus earlier. `[MIX.objective]`
- In settled campaigns, Google Webinar returns $1,953 of pipeline per dollar and Google Demo returns $612. That is observational, so it tells us where to test, not what causes the gap. `[SEG.platform_objective]`
- The one logged test favoring Demo on Google, E013, is not a valid read. It ran 5 days against a 14-day minimum on a sample of 31, and it used a proxy metric. It should not back the shift. `[EXP.E013]`
- Across platforms, Demo returns 0.46x the pipeline of comparable campaigns while taking 49% of settled spend. Webinar returns 1.42x on 41%. `[SEG.objective]`
- LinkedIn is the weakest platform in settled campaigns. It costs $3,555 per opportunity, against $71 on Google and $164 on Meta. `[FUNNEL.platform]`

## The three experiments to run next

### 1. Google Webinar vs Demo head-to-head

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** In settled campaigns Google Webinar returns more pipeline per dollar than Google Demo; a randomized split will show whether the offer drives it.

**Why this test.** Google moved most of its budget to Demo while settled Google Webinar returns $1,953 of pipeline per dollar against $612 for Demo. No valid test supports the move, so this is the largest decision the team is making now. `[SEG.platform_objective, MIX.objective, EXP.E013]`

| | |
|---|---|
| Where | Google · Law Firm - Enterprise · US |
| Control | Demo offer, ROI theme, Law Firm creative (Book Demo, CR001) |
| Variant | Webinar offer, ROI theme, same creative (Register, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, click-through rate, qualified lead rate |
| Budget | $250 per arm per day for 28 days ($14,000 in total) |
| Expected volume | Demo (current mix): about 216 qualified leads, 45 opportunities; Webinar: about 387 qualified leads, 110 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If Webinar is at least 25% higher on pipeline per $ than Demo, shift Google budget toward Webinar and repeat the split on Meta before any wider move; if within 25% either way, hold the mix and extend the read; if Demo is at least 25% higher, keep Demo. |
| Evidence | SIG.01, SEG.platform_objective, MIX.objective |

**What we learn either way.** Whichever way it lands, it tells the team whether to rebuild Google Webinar spend or keep Demo. It also says whether the split is worth repeating on Meta and LinkedIn.

### 2. LinkedIn Webinar vs Content Download (confirmation of E003)

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review, 2 warning(s).

**Hypothesis.** E003 logged Webinar as a win on LinkedIn but settled campaigns disagree; re-test on an outcome metric.

**Why this test.** LinkedIn holds a large share of spend but returns far less than comparable campaigns, so its offer mix matters. The E003 Webinar win is directional only, and settled LinkedIn data shows Webinar at 0.60x Content Download, so the team needs a clean read. `[EXP.E003, SEG.platform_objective]`

| | |
|---|---|
| Where | LinkedIn · Law Firm - Enterprise · US |
| Control | Content Download offer, ROI theme (Download Guide, CR001) |
| Variant | Webinar offer, ROI theme (Register, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, click-through rate, qualified lead rate |
| Budget | $1,000 per arm per day for 28 days ($56,000 in total) |
| Expected volume | Content Download: about 242 qualified leads, 26 opportunities; Webinar: about 135 qualified leads, 13 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If Webinar is at least 25% higher on pipeline per $, favor Webinar on LinkedIn; if within 25%, hold the LinkedIn mix; if Content Download is at least 25% higher, favor Content Download. Treat the read as provisional if either arm has fewer than 30 opportunities, and use qualified lead rate as the tiebreaker. |
| Evidence | EXP.E003, SEG.platform_objective |
| Re-test of | E003 |

**What we learn either way.** It shows which LinkedIn offer deserves the remaining LinkedIn budget. It also shows whether the E003 win holds on an outcome metric.

- Guardrail warning (sample_size): Content Download: expect about 26 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

- Guardrail warning (sample_size): Webinar: expect about 13 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

### 3. Customer Proof vs AI Productivity on Meta Webinar (re-test of E009)

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** E009 logged Customer Proof as a win, but settled Meta campaigns point the other way; a clean re-test settles which message keeps its budget.

**Why this test.** E009 logged Customer Proof as a trusted win on Meta, but settled Meta campaigns show it at 0.81x AI Productivity. The team needs to know which message keeps its budget. `[EXP.E009, SEG.theme]`

| | |
|---|---|
| Where | Meta · Law Firm - Enterprise · US |
| Control | Webinar offer, AI Productivity theme (Register, CR007) |
| Variant | Webinar offer, Customer Proof theme (Register, CR013) |
| The one thing that differs | theme |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, click-through rate, qualified lead rate |
| Budget | $250 per arm per day for 28 days ($14,000 in total) |
| Expected volume | AI Productivity: about 188 qualified leads, 43 opportunities; Customer Proof: about 188 qualified leads, 43 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If Customer Proof is at least 15% higher on pipeline per $, keep it in the mix; if within 15% either way, stop scaling it and hold spend flat; if it is at least 15% lower, cut Customer Proof spend on Meta. |
| Evidence | EXP.E009, SEG.theme |
| Re-test of | E009 |

**What we learn either way.** It settles whether Customer Proof earns budget on Meta or only looked good in one test. It also shows which logged learnings the team can plan around.

## Creative recommendations

- Lead Law Firm - Enterprise work with the ROI message. In settled campaigns the ROI Static Law Firm creative is the best performer against comparable campaigns at 1.45x, and ROI for Law Firm - Enterprise is among the strongest pairings at 1.52x. `[CREATIVE.performance, THEME.by_audience]`
- Do not add creative spend behind Customer Proof for Mid-Market audiences until experiment 3 reads. Customer Proof for In-House - Mid-Market is among the weakest pairings at 0.64x, and the Customer Proof Static In-House creative is the weakest creative at 0.40x. `[THEME.by_audience, CREATIVE.performance]`
- Plan creative refresh by platform. Meta CTR holds for 6 weeks and is at 79% of launch level by week 9. LinkedIn holds for 7 weeks and is at 71% by week 10. Google shows no decay with age. `[FATIGUE.curve]`
- CR021 (Workflow Automation, Video, Law Firm) has never run. Keep it ready as the fresh Video option for Law Firm audiences when the next launches are planned. `[CREATIVE.gaps]`
- Security exists only in Static, with no Carousel or Video for either audience. Hold off on new Security formats until Security has a properly powered read. `[CREATIVE.gaps, SEG.theme]`

## Risks and observations

- Three strong signals get no test this week: a LinkedIn holdout, a Meta and LinkedIn creative rotation, and the Security read. The LinkedIn holdout matters because 24 of 41 settled LinkedIn campaigns produced no opportunities on $385,683 of spend, and last-touch attribution can hide influence on enterprise deals. Do not cut LinkedIn on this data alone. `[ZERO.opportunities, FATIGUE.curve, SEG.theme]`
- Meta has $190,139 of spend behind creative past the point where CTR starts to fall. That is about 17% of Meta spend. It is untested this week, so treat it as a fast follow-up. `[FATIGUE.curve]`
- The LinkedIn test in experiment 2 may read noisily because opportunity counts per arm will be low. The decision rule falls back on qualified lead rate if counts stay thin. `[EXP.E003, SEG.platform_objective]`
- Last week's qualified leads, opportunities and pipeline are provisional, and 14 campaigns carry the immature flag. They are excluded from every benchmark used here. `[DQ.attribution_lag]`
- Only 6 campaigns were live on Jun 30 and none are scheduled past it. The three tests need new campaigns approved and launched, and none can read until attribution settles. `[WEEK.program_status]`

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
- Writing and experiment design: `claude-sonnet-5-5` (live run), 6 turns, 3 submissions of the brief.
- Claim check: every number in 23 claims was matched to the evidence it cites.
- Guardrails: 3 experiments passed every rule. The best possible verdict is 'ready for human review'.
- Held back: nothing. No claim or experiment was removed.
- Cost of this run: $0.37 and 121 seconds. 50,693 input tokens billed in full, 170,740 read from cache, 21,245 output.

### Agent steps

- Turn 1: read the creative library
- Turn 1: read SEG.platform_objective, MIX.objective, EXP.E013, EXP.E009, EXP.E003, DQ.attribution_lag, SEG.theme, FATIGUE.curve, ZERO.opportunities, SEG.platform, SEG.objective
- Turn 2: 'Google Webinar vs Demo head-to-head' cleared for human review
- Turn 2: 'Customer Proof vs AI Productivity on Meta Webinar' blocked: settled_question
- Turn 2: 'LinkedIn Webinar vs Content Download' cleared for human review with 3 warning(s)
- Turn 3: 'Customer Proof vs AI Productivity on Meta Webinar (re-test of E009)' cleared for human review
- Turn 3: 'LinkedIn Webinar vs Content Download (confirmation of E003)' cleared for human review with 2 warning(s)
- Turn 4: brief returned with 1 problem(s) on attempt 1
- Turn 5: brief returned with 1 problem(s) on attempt 2
- Turn 6: brief accepted on attempt 3
