# Weekly Experimentation Brief

**Week of 2026-06-24 to 2026-06-30** · Performance Marketing · Google Ads, LinkedIn Ads, Meta

> Synthetic sample data. Not Harvey performance.
> **Nothing in this brief has been launched.** 3 experiments are staged as drafts and wait for a person to approve, edit or reject.

## The headline

The team must decide whether Google keeps putting almost all its budget into Demo. In settled campaigns Google Webinar returns $1,953 of pipeline per dollar against $612 for Google Demo, and Demo now takes 92% of Google spend. `[SEG.platform_objective, MIX.objective]`

## What happened last week

- Spend fell to $17,013 across 9 campaigns, down 53% from $36,140 the week before. Clicks fell 64% and conversions fell 67% to 86. `[WEEK.totals]`
- The drop is campaigns ending, not campaigns weakening. 8 wound-down campaigns explain 99% of the spend change, and no campaign launched. `[WEEK.spend_bridge]`
- For the 6 campaigns live both weeks, spend was down 1% and CTR slipped from 2.18% to 1.97%. Conversions went from 60 to 57. `[WEEK.same_store]`
- No campaigns are scheduled past Jun 30, and weekly spend is 91% below the peak week of Mar 04 ($194,291). The next launches are the chance to build tests into live spend. `[WEEK.program_status]`
- Lead capture for the week is current. Qualified leads, opportunities and pipeline are provisional, because qualified leads run at only 27% of their normal rate inside the lag window. `[DQ.attribution_lag]`

## Why it happened

- In settled campaigns, Google Webinar out-earns Google Demo on pipeline per dollar. Google moved from 55% Webinar and 42% Demo to 5% Webinar and 92% Demo over the last 8 weeks. This is observational: it shows where to test, not what causes the gap. `[SEG.platform_objective, MIX.objective]`
- Demo is below benchmark in all 3 platform cells with enough spend, and takes 49% of settled spend. Webinar is above benchmark in all 3 cells on 41% of spend. `[SEG.objective]`
- The one test that favored Demo on Google (E013) is rejected. It ran 5 days with a sample of 31 and used a proxy metric, so it cannot support the budget move. It is the reason to re-test. `[EXP.E013]`
- LinkedIn returns $25 of pipeline per dollar against $1,307 on Google, on a similar share of spend. 24 of 41 settled LinkedIn campaigns produced no opportunities. Last-touch attribution may under-credit LinkedIn on enterprise deals, so this is not yet proof it should be cut. `[SEG.platform, ZERO.opportunities]`
- Two trusted tests (E001, E014) found ROI messaging ahead of AI Productivity, and settled campaigns agree. That question is answered, so this week's theme test goes elsewhere. `[EXP.E001, EXP.E014]`

## The three experiments to run next

### 1. Google: Webinar vs Demo offer head-to-head

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** Webinar will return at least 50% more pipeline per dollar than Demo on Google for Law Firm - Enterprise.

**Why this test.** Google moved nearly all its budget to Demo while settled data shows Webinar returning more per dollar. The only test behind the move (E013) is rejected, so this is a clean re-test on a business outcome at full length. `[SEG.platform_objective, MIX.objective, EXP.E013]`

| | |
|---|---|
| Where | Google · Law Firm - Enterprise · US |
| Control | Demo offer, ROI theme, Static creative (Book Demo, CR001) |
| Variant | Webinar offer, ROI theme, same Static creative (Register, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, CTR |
| Budget | $200 per arm per day for 28 days ($11,200 in total) |
| Expected volume | Demo: about 173 qualified leads, 36 opportunities; Webinar: about 310 qualified leads, 88 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If Webinar is at least 50% higher on pipeline per dollar, shift Google budget back toward Webinar and repeat the test on Meta; if within 50% either way, keep the current mix; if Demo is at least 50% higher, keep Demo. |
| Evidence | SEG.platform_objective, MIX.objective |
| Re-test of | E013 |

**What we learn either way.** Either way, the team learns whether Google budget should go back toward Webinar. If Webinar wins, the team repeats the test on Meta before moving more spend. If Demo wins, the current mix stays on firmer ground than E013 gave it.

### 2. LinkedIn: Webinar vs Content Download

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review, 2 warning(s).

**Hypothesis.** Content Download will return at least 50% more pipeline per dollar than Webinar on LinkedIn for Law Firm - Enterprise.

**Why this test.** LinkedIn trails comparable campaigns, and the team's LinkedIn offer test (E003) points the opposite way from settled campaign data. A LinkedIn Demo arm was blocked by the validator on sample size, so this tests the two offers LinkedIn can support. `[EXP.E003, SEG.platform_objective]`

| | |
|---|---|
| Where | LinkedIn · Law Firm - Enterprise · US |
| Control | Webinar offer, ROI theme, Static creative (Register, CR001) |
| Variant | Content Download offer, ROI theme, same Static creative (Download Guide, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, CTR |
| Budget | $900 per arm per day for 28 days ($50,400 in total) |
| Expected volume | Webinar: about 122 qualified leads, 11 opportunities; Content Download: about 218 qualified leads, 24 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If Content Download is at least 50% higher on pipeline per dollar, move LinkedIn Webinar budget to Content Download; if Webinar is at least 50% higher, keep Webinar and treat E003 as confirmed; otherwise hold the current mix and use qualified lead rate as a tiebreak. |
| Evidence | SEG.platform_objective, EXP.E003 |
| Re-test of | E003 |

**What we learn either way.** The team learns which of the two testable LinkedIn offers deserves the LinkedIn budget, and whether E003 holds up on a valid read. If neither offer clears the bar, that supports a wider LinkedIn review.

- Guardrail warning (sample_size): Webinar: expect about 11 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

- Guardrail warning (sample_size): Content Download: expect about 24 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

### 3. Google Demo: ROI vs Customer Proof

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** ROI will return at least 25% more pipeline per dollar than Customer Proof on Google Demo for In-House - Enterprise.

**Why this test.** Customer Proof now takes 24% of the last 8 weeks' spend while trailing comparable campaigns, and ROI is above benchmark in all 6 cells with enough spend. E009 favored Customer Proof on Meta but settled data disagrees, so the team needs a clean read on Google Demo, where most live campaigns run. `[SEG.theme, EXP.E009]`

| | |
|---|---|
| Where | Google · In-House - Enterprise · US |
| Control | Customer Proof theme, Static creative, Demo offer (Book Demo, CR016) |
| Variant | ROI theme, Static creative, Demo offer (Book Demo, CR004) |
| The one thing that differs | theme |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, CTR |
| Budget | $200 per arm per day for 28 days ($11,200 in total) |
| Expected volume | Customer Proof: about 173 qualified leads, 36 opportunities; ROI: about 173 qualified leads, 36 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42 after attribution settles. If ROI is at least 25% higher on pipeline per dollar, move Customer Proof budget to ROI; if within 25% either way, keep the current mix; if Customer Proof is at least 25% higher, treat E009 as confirmed and keep it. |
| Evidence | SEG.theme, EXP.E009 |

**What we learn either way.** The team learns whether to keep funding Customer Proof creative or move that budget to ROI. If Customer Proof holds up, E009 gains support.

## Creative recommendations

- Lead with ROI messaging for Enterprise audiences. ROI is the strongest pairing for In-House - Enterprise (1.58x) and Law Firm - Enterprise (1.52x) against comparable campaigns. `[THEME.by_audience]`
- Static ROI for Law Firm (CR001) is the best performing creative at 1.45x against comparable campaigns. Use it as the shared creative in the offer tests. `[CREATIVE.performance]`
- Hold new Customer Proof creative work until experiment 3 reads. CR016 is the weakest creative at 0.40x, and Customer Proof for In-House - Mid-Market is among the weakest pairings at 0.64x. `[CREATIVE.performance, THEME.by_audience]`
- Plan refreshes by platform. Meta creative holds for 6 weeks before CTR slips, and LinkedIn holds for 7 weeks. Google shows no decay with age. `[FATIGUE.curve]`
- CR021 (Workflow Automation, Video, Law Firm) has never run, so it is the ready fresh variant for a Law Firm rotation or format test. Security exists only in Static, so wait for a valid Security read before building Carousel or Video. `[CREATIVE.gaps]`

## Risks and observations

- The week's qualified leads, opportunities and pipeline are provisional. 14 campaigns carry the immature flag, so do not judge this week on downstream results yet. `[DQ.attribution_lag]`
- The LinkedIn holdout (SIG.07) and a LinkedIn Demo offer test get no experiment this week. The validator blocked the LinkedIn Demo arm on sample size. A holdout does not fit a one-variable design. Last-touch attribution may be hiding LinkedIn's influence on enterprise deals. `[ZERO.opportunities, SEG.platform_objective]`
- Meta and LinkedIn creative fatigue and Meta's low lead quality (only 30% of Meta leads qualify, against 63% on Google) get no test this week. Both are real exposure, but they rank below the offer and theme decisions. `[FATIGUE.curve, FUNNEL.platform]`
- The experiment log needs care. Settled campaign data disagrees with E003, E004 and E009, so none of them should drive budget until re-confirmed. E012 and E013 are overturned. `[EXP.summary]`
- With no campaigns scheduled past Jun 30, these tests need approval and a launch slot. Nothing has been launched. Until they read on day 42, there is no valid evidence on Webinar versus Demo in Google. `[WEEK.program_status]`

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
- Writing and experiment design: `claude-sonnet-5-5` (live run), 5 turns, 1 submission of the brief.
- Claim check: every number in 24 claims was matched to the evidence it cites.
- Guardrails: 3 experiments passed every rule. The best possible verdict is 'ready for human review'.
- Held back: nothing. No claim or experiment was removed.
- Cost of this run: $0.26 and 98 seconds. 39,501 input tokens billed in full, 117,608 read from cache, 14,224 output.

### Agent steps

- Turn 1: read the creative library
- Turn 1: read SEG.platform_objective, SEG.objective, MIX.objective, EXP.E013, DQ.attribution_lag, ZERO.opportunities, FATIGUE.curve, EXP.E003, SEG.platform
- Turn 2: 'Google: Webinar vs Demo offer head-to-head' cleared for human review
- Turn 2: 'LinkedIn: Demo vs Content Download' blocked: sample_size
- Turn 2: 'Google Demo: ROI vs Customer Proof' cleared for human review
- Turn 3: 'LinkedIn: Webinar vs Content Download' blocked: sample_size
- Turn 4: 'LinkedIn: Webinar vs Content Download' cleared for human review with 2 warning(s)
- Turn 4: 'Google: Webinar vs Demo offer head-to-head' cleared for human review
- Turn 4: 'Google Demo: ROI vs Customer Proof' cleared for human review
- Turn 5: brief accepted on attempt 1
