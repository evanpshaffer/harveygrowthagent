# Weekly Experimentation Brief

**Week of 2026-06-24 to 2026-06-30** · Performance Marketing · Google Ads, LinkedIn Ads, Meta

> Synthetic sample data. Not Harvey performance.
> **Nothing in this brief has been launched.** 3 experiments are staged as drafts and wait for a person to approve, edit or reject.

## The headline

Decision: keep shifting Google budget to Demo, or move it back to Webinar. In settled campaigns Google Webinar returns $1,953 of pipeline per dollar against $612 for Demo, yet Webinar fell from 55% to 5% of Google spend while Demo rose from 42% to 92%. `[SEG.platform_objective, MIX.objective]`

## What happened last week

- Spend fell to $17,013 across 9 campaigns, down 53% from $36,140. Conversions were 86, down 67%. `[WEEK.totals]`
- Campaigns that ended or wound down explain 99% of the spend drop. The 6 campaigns live all 14 days were nearly flat on spend. `[WEEK.spend_bridge]`
- Only 6 campaigns were still live on Jun 30 and none are scheduled past it. Weekly spend is down 91% from the March peak, so the next launches are the experiment slate. `[WEEK.program_status]`
- Qualified leads, opportunities and pipeline for this week are provisional. Qualified leads in the window are only 27% of what conversions would normally produce, so this brief judges no campaign on them. `[DQ.attribution_lag]`

## Why it happened

- In settled campaigns Webinar is 1.42x comparable campaigns and Demo is 0.46x. Demo holds 49% of settled spend and Webinar 41%. This is observational: it shows where to test, not what causes the gap. `[SEG.objective]`
- On Google, Webinar sits above Demo in settled campaigns. Google as a platform is 1.86x comparable campaigns, so the offer mix inside Google is the largest lever we can see. `[SEG.platform_objective, SEG.platform]`
- The one test that favored Demo on Google, E013, ran 5 days on a sample of 31 and used a proxy metric. It is rejected, so it cannot justify the shift. It is a reason to re-test. `[EXP.E013]`
- LinkedIn is 0.06x comparable campaigns on 31% of settled spend. 24 of 41 settled LinkedIn campaigns produced no opportunities. Last-touch attribution may under-credit LinkedIn, so this is not yet a case to cut it. `[SEG.platform, ZERO.opportunities]`

## The three experiments to run next

### 1. Google: Webinar vs Demo offer, head to head

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Google, a Webinar offer returns at least 25% more pipeline per dollar than a Demo offer for the same audience and message.

**Why this test.** Google Demo took most of the budget while settled data favors Webinar on Google. This is the biggest pipeline decision the team is making now, and the only test behind it is rejected. `[MIX.objective, SEG.platform_objective, EXP.E013]`

| | |
|---|---|
| Where | Google · Law Firm - Enterprise · US |
| Control | Demo offer, ROI theme, CR001 (Book Demo) |
| Variant | Webinar offer, ROI theme, CR001 (Book Demo) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | qualified lead rate, cost per opportunity, cost per lead, CTR |
| Budget | $1,000 per arm per day for 28 days ($56,000 in total) |
| Expected volume | Demo (current mix): about 864 qualified leads, 181 opportunities; Webinar: about 1,548 qualified leads, 441 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, 14 days after the last spend day, once attribution settles. If Webinar is at least 25% higher on pipeline per $, shift Google budget toward Webinar and stage the same comparison as a separate repeat on other platforms. If Webinar is within 25% of Demo either way, hold the mix and extend the read. If Demo is at least 25% higher, keep Demo and reopen the campaign-data discrepancy. |
| Evidence | SIG.01, SEG.platform_objective, MIX.objective |

**What we learn either way.** Whichever way it lands, it tells us whether Google budget should go back to Webinar or stay on Demo, read on a business outcome. If Webinar wins, the decision rule stages a separate repeat on other platforms.

### 2. LinkedIn: Webinar vs Content Download offer re-confirmation

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review, 2 warning(s).

**Hypothesis.** On LinkedIn, a Webinar offer returns at least 50% more pipeline per dollar than a Content Download offer (re-tests E003).

**Why this test.** LinkedIn carries 31% of settled spend at 0.06x comparable campaigns. The one test on its offer, E003, is directional and settled data disagrees with it, so the offer call is unresolved. `[SEG.platform, EXP.E003]`

| | |
|---|---|
| Where | LinkedIn · Law Firm - Enterprise · US |
| Control | Content Download offer, ROI theme, CR001 (Download Guide) |
| Variant | Webinar offer, ROI theme, CR001 (Download Guide) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | qualified lead rate, cost per opportunity, cost per lead, CTR |
| Budget | $1,000 per arm per day for 28 days ($56,000 in total) |
| Expected volume | Content Download: about 242 qualified leads, 26 opportunities; Webinar: about 135 qualified leads, 13 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, once attribution settles. Expected opportunities are low, so the bar is 50%. If Webinar is at least 50% higher on pipeline per $, treat E003 as confirmed and move LinkedIn spend toward Webinar. If within 50% either way, hold the mix and check qualified lead rate. If Content Download is at least 50% higher, treat E003 as contradicted and move spend toward Content Download. |
| Evidence | EXP.E003, SEG.platform_objective |
| Re-test of | E003 |

**What we learn either way.** Tells us whether LinkedIn spend should lean to Webinar or Content Download. Expected opportunities are low, so read qualified lead rate alongside pipeline. This does not test whether LinkedIn should be cut.

- Guardrail warning (sample_size): Content Download: expect about 26 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

- Guardrail warning (sample_size): Webinar: expect about 13 opportunities. A pipeline read will be noisy below 30; consider qualified-lead rate as the decision metric with pipeline as confirmation.

### 3. Meta: Customer Proof vs AI Productivity message re-confirmation

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Meta Webinar campaigns for Law Firm Enterprise, Customer Proof messaging returns at least 15% more pipeline per dollar than AI Productivity messaging (re-confirms E009).

**Why this test.** Customer Proof trails comparable campaigns yet took a growing share of recent spend. E009 logged a trusted win for it on Meta, but settled campaign data points the other way. `[SEG.theme, EXP.E009]`

| | |
|---|---|
| Where | Meta · Law Firm - Enterprise · US |
| Control | AI Productivity static, Webinar (Register, CR007) |
| Variant | Customer Proof static, Webinar (Register, CR013) |
| The one thing that differs | theme |
| Primary metric | pipeline per $ |
| Guardrail metrics | qualified lead rate, cost per opportunity, cost per lead, CTR |
| Budget | $1,000 per arm per day for 28 days ($56,000 in total) |
| Expected volume | AI Productivity: about 752 qualified leads, 172 opportunities; Customer Proof: about 752 qualified leads, 172 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, once attribution settles. If Customer Proof is at least 15% higher on pipeline per $, keep its current share of Meta spend and treat E009 as confirmed. If within 15% either way, treat E009 as unconfirmed and stop adding Customer Proof spend. If AI Productivity is at least 15% higher, move Meta budget to AI Productivity. |
| Evidence | EXP.E009, SIG.14 |
| Re-test of | E009 |

**What we learn either way.** Settles whether Customer Proof keeps its share of Meta spend or whether E009 was a one-off. Either result resolves a conflict between a trusted test and campaign data.

## Creative recommendations

- Lead with ROI messaging for Law Firm Enterprise. ROI for that audience is among the strongest pairings, and CR001 (ROI, Static, Law Firm) is the best performer against comparable campaigns at 1.45x. `[THEME.by_audience, CREATIVE.performance]`
- Refresh Meta creative after week 6 and LinkedIn creative after week 7. Google shows no decay with age, so it needs no age-based refresh. `[FATIGUE.curve]`
- Use CR021 (Workflow Automation, Video, Law Firm) as the fresh variant in the next Law Firm rotation or format test. It is active in the library and has never run. `[CREATIVE.gaps]`
- Move budget away from CR016 (Customer Proof, Static, In-House), the weakest creative at 0.40x against comparable campaigns. Do not add new Security creative yet. It exists only in Static and has no valid test. `[CREATIVE.performance, CREATIVE.gaps, EXP.E011]`

## Risks and observations

- Three-slot limit: Demo trailing and Webinar leading are the same decision as P1, so they get no separate test. A Google-versus-mix scale test was not staged. P1 covers the Google offer question first. `[SEG.objective, SEG.platform]`
- No LinkedIn holdout is staged this week. No holdout design was validated, so the team cannot yet say whether LinkedIn influences deals that last-touch attribution hides. P3 tests only the LinkedIn offer. `[ZERO.opportunities, SEG.platform]`
- Meta and LinkedIn creative rotation tests are also not staged. They are real exposure, but they rank below the offer and message decisions above. `[FATIGUE.curve]`
- All experiment reads are set after the 14-day attribution lag has cleared, because earlier pipeline numbers are provisional. Any read before then should not drive budget moves. `[DQ.attribution_lag]`
- Segment gaps here are observational. The data cannot say whether Webinar causes better pipeline, only that settled Webinar campaigns look stronger. Meta also buys cheap leads that do not qualify, so judge Meta on cost per opportunity rather than cost per lead. `[SEG.platform_objective, FUNNEL.platform]`

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
- Writing and experiment design: `claude-sonnet-5-5` (live run), 5 turns, 2 submissions of the brief.
- Claim check: every number in 21 claims was matched to the evidence it cites.
- Guardrails: 3 experiments passed every rule. The best possible verdict is 'ready for human review'.
- Held back: nothing. No claim or experiment was removed.
- Cost of this run: $0.26 and 99 seconds. 29,225 input tokens billed in full, 137,487 read from cache, 16,224 output.

### Agent steps

- Turn 1: read the creative library
- Turn 1: read SEG.platform_objective, SEG.objective, MIX.objective, EXP.E013, EXP.E009, EXP.E003, DQ.attribution_lag, SEG.platform, ZERO.opportunities, FATIGUE.curve, EXP.E014, EXP.summary
- Turn 2: 'Google: Webinar vs Demo offer, head to head' cleared for human review
- Turn 2: 'Meta: Customer Proof vs AI Productivity message re-confirmation' blocked: settled_question
- Turn 2: 'LinkedIn: Webinar vs Content Download offer re-confirmation' cleared for human review with 3 warning(s)
- Turn 3: 'Meta: Customer Proof vs AI Productivity message re-confirmation' cleared for human review
- Turn 3: 'LinkedIn: Webinar vs Content Download offer re-confirmation' cleared for human review with 2 warning(s)
- Turn 4: brief returned with 3 problem(s) on attempt 1
- Turn 5: brief accepted on attempt 2
