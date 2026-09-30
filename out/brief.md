# Weekly Experimentation Brief

**Week of 2026-06-24 to 2026-06-30** · Performance Marketing · Google Ads, LinkedIn Ads, Meta

> Synthetic sample data. Not Harvey performance.
> **Nothing in this brief has been launched.** 3 experiments are staged as drafts and wait for a person to approve, edit or reject.

## The headline

Spend fell to $17,013 as the program wound down, and Google budget has shifted to Demo even though settled campaigns return more pipeline per dollar from Webinar. Staged tests will settle which offer to fund before the next launches. `[WEEK.totals, MIX.objective, SEG.platform_objective]`

## What happened last week

- In the week of Jun 24 to Jun 30, 9 campaigns spent $17,013 (-53% vs the prior week's $36,140 across 14 campaigns). They produced 11,713 clicks (-64%) and 86 conversions (-67%). `[WEEK.totals]`
- 8 campaigns that ended or wound down account for -$19,000 of the spend drop (99%). 0 campaigns launched. `[WEEK.spend_bridge]`
- 6 campaigns were still live on Jun 30 and 0 are scheduled to run past it. Weekly spend is down 91% from the peak week of Mar 04. `[WEEK.program_status]`
- The week shows 10 qualified leads and 1 opportunity, but both are provisional. Qualified leads are only 27% of what conversions would normally produce, so we are not judging the week on pipeline. `[WEEK.totals, DQ.attribution_lag]`

## Why it happened

- Google Webinar went from 55% to 5% of platform spend. Google Demo went from 42% to 92% (last 8 weeks versus everything earlier). `[MIX.objective]`
- In settled campaigns, Google Webinar returns $1,953 of pipeline per dollar and Google Demo returns $612. This is observational, so it tells us where to test, not what causes the gap. `[SEG.platform_objective]`
- Across platforms, Demo returns 0.46x the pipeline of comparable campaigns on 49% of spend. Webinar returns 1.42x on 41% of spend. `[SEG.objective]`
- E013 is logged as a Demo win on Google, but it ran 5 days on a sample of 31 with a proxy metric. It is not a valid read, so it cannot justify the Demo shift. It is the reason to re-test. `[EXP.E013]`
- LinkedIn returns $25 of pipeline per dollar against $1,307 on Google. 24 of 41 settled LinkedIn campaigns produced no opportunities. `[SEG.platform, ZERO.opportunities]`

## The three experiments to run next

### 1. Google: Webinar vs Demo offer, head to head

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Google, a Webinar offer returns more pipeline per dollar than a Demo offer for the same audience and message.

**Why this test.** Google budget moved to Demo while settled Webinar campaigns return more pipeline per dollar ($1,953 vs $612). The only test favoring Demo is rejected, so this decision has no valid test behind it. `[SEG.platform_objective, MIX.objective, EXP.E013]`

| | |
|---|---|
| Where | Google · Law Firm - Enterprise · US |
| Control | Demo offer, ROI theme, CR001 (Demo, ROI, CR001) |
| Variant | Webinar offer, ROI theme, CR001 (Webinar, ROI, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, cost per opportunity |
| Budget | $1,000 per arm per day for 28 days ($56,000 in total) |
| Expected volume | Demo (current): about 864 qualified leads, 181 opportunities; Webinar: about 1,548 qualified leads, 441 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, after attribution settles. If Webinar pipeline per $ beats Demo and the gap exceeds noise across 100+ qualified leads per arm, propose shifting Google budget back toward Webinar. If Demo matches or beats Webinar, keep the current mix. If the gap is small, extend the read. |
| Evidence | SEG.platform_objective, MIX.objective, SEG.objective |
| Re-test of | E013 |

**What we learn either way.** Whichever offer wins on pipeline per dollar after attribution settles tells us where Google budget should sit in the next launches. If Demo does not win, the current Demo-heavy mix has no support.

### 2. Meta: Webinar vs Demo offer

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Meta, a Webinar offer returns more pipeline per dollar than a Demo offer for the same audience and message.

**Why this test.** On Meta, settled Webinar returns $765 of pipeline per dollar and Demo returns $262. Demo is still the main offer in this week's live campaigns. `[SEG.platform_objective, WEEK.program_status]`

| | |
|---|---|
| Where | Meta · Law Firm - Enterprise · US |
| Control | Demo offer, ROI theme, CR001 (Demo, ROI, CR001) |
| Variant | Webinar offer, ROI theme, CR001 (Webinar, ROI, CR001) |
| The one thing that differs | objective |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, cost per opportunity |
| Budget | $700 per arm per day for 28 days ($39,200 in total) |
| Expected volume | Demo (current): about 302 qualified leads, 48 opportunities; Webinar: about 527 qualified leads, 120 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, after attribution settles. If Webinar beats Demo on pipeline per $ with 100+ qualified leads per arm, move Meta Demo budget toward Webinar. If Demo matches or beats Webinar, keep the current mix. If the gap is small, extend the read. |
| Evidence | SEG.platform_objective, SEG.objective, MIX.objective |

**What we learn either way.** Shows whether the Webinar edge holds on a second platform. A win supports a program-wide offer shift. A loss means the Google result is platform specific.

### 3. Meta: Customer Proof vs AI Productivity (re-test of E009)

**Status: DRAFT, awaiting approval.** Guardrails: ready for human review.

**Hypothesis.** On Meta, Customer Proof messaging returns more pipeline per dollar than AI Productivity messaging for the same audience and offer.

**Why this test.** E009 is a trusted win for Customer Proof on Meta, but settled campaigns point the other way. Customer Proof trails comparable campaigns at 0.75x. `[EXP.E009, SEG.theme]`

| | |
|---|---|
| Where | Meta · In-House - Enterprise · US |
| Control | AI Productivity theme, Carousel CR011, Webinar offer (Webinar, AI Productivity, CR011) |
| Variant | Customer Proof theme, Carousel CR017, Webinar offer (Webinar, Customer Proof, CR017) |
| The one thing that differs | theme |
| Primary metric | pipeline per $ |
| Guardrail metrics | cost per lead, qualified lead rate, cost per opportunity |
| Budget | $500 per arm per day for 28 days ($28,000 in total) |
| Expected volume | AI Productivity: about 376 qualified leads, 86 opportunities; Customer Proof: about 376 qualified leads, 86 opportunities |
| Earliest valid read | Day 42 (runtime plus 14 days for attribution to settle) |
| Decision rule | Read on day 42, after attribution settles. If Customer Proof beats AI Productivity on pipeline per $ with 100+ qualified leads per arm, E009 is confirmed and Customer Proof keeps its share. If it loses, cut Customer Proof share on Meta and treat E009 as not replicated. |
| Evidence | EXP.E009, SEG.theme, SEG.platform_objective |
| Re-test of | E009 |

**What we learn either way.** Confirms or overturns E009 on the outcome metric. The result decides whether Customer Proof keeps its share of Meta spend.

## Creative recommendations

- Lead Law Firm - Enterprise with the ROI message. It is the strongest pairing for that audience, and CR001 (ROI Static, Law Firm) is the best-performing creative against same-platform, same-offer campaigns. `[THEME.by_audience, CREATIVE.performance]`
- Hold new Customer Proof creative until the E009 re-test reads. It is among the weakest pairings for Mid-Market audiences, and CR016 is the worst-performing creative. `[THEME.by_audience, CREATIVE.performance, EXP.E009]`
- Plan a fresh creative for Meta campaigns from week 7 and for LinkedIn campaigns from week 8. Google shows no decay with age, so it needs no age-based refresh. `[FATIGUE.curve]`
- Use CR021 (Workflow Automation, Video, Law Firm), which has never run, as the fresh variant in the next Law Firm format test. `[CREATIVE.gaps]`
- Do not build more Security creative yet. It exists only in Static, and it has no valid test behind it. `[CREATIVE.gaps, EXP.E011]`

## Risks and observations

- Qualified leads, opportunities and pipeline for Jun 17 to Jun 30 are inside the attribution lag window. Every test reads only after attribution settles, and none should be judged early. `[DQ.attribution_lag]`
- We could not test LinkedIn's offer or run a LinkedIn holdout at an affordable size. LinkedIn costs too much per qualified lead to fit the guardrails, so LinkedIn stays a known gap. The data cannot say whether LinkedIn influences deals that last-touch attribution credits elsewhere. `[SEG.platform, ZERO.opportunities, FUNNEL.platform]`
- Segment comparisons are observational. Offer, platform and audience were not randomized, so the Webinar edge shows where to test, not proof of cause. `[SEG.platform_objective, SEG.objective]`
- Nothing is scheduled past Jun 30, so these tests need new launches to run. Every test is staged as a draft and needs human approval. `[WEEK.program_status]`
- Meta has low-cost leads but only 30% qualify, against 63% on Google. Judge Meta on cost per opportunity, not cost per lead. `[FUNNEL.platform]`

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
- Claim check: every number in 23 claims was matched to the evidence it cites.
- Guardrails: 3 experiments passed every rule. The best possible verdict is 'ready for human review'.
- Held back: nothing. No claim or experiment was removed.
- Cost of this run: 162,155 input and 15,958 output tokens, $0.48, 97 seconds.

### Agent steps

- Turn 1: read the creative library
- Turn 1: read SEG.platform_objective, MIX.objective, EXP.E013, DQ.attribution_lag, WEEK.totals, SEG.objective, SEG.platform, FATIGUE.curve, ZERO.opportunities, WEEK.program_status
- Turn 2: 'Google: Webinar vs Demo offer, head to head' blocked: evidence
- Turn 2: 'LinkedIn: Webinar vs Demo offer' blocked: sample_size
- Turn 2: 'Meta: Customer Proof vs AI Productivity (re-test of E009)' cleared for human review
- Turn 3: 'Google: Webinar vs Demo offer, head to head' cleared for human review
- Turn 3: 'Meta: Webinar vs Demo offer' cleared for human review
- Turn 4: brief returned with 2 problem(s) on attempt 1
- Turn 5: brief accepted on attempt 2
