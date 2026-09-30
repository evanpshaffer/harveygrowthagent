# Growth Agent: analysis report

Reporting week **2026-06-24 to 2026-06-30**, compared with 2026-06-17 to 2026-06-23. Data source: `sample_csv` (synthetic sample data, not Harvey performance).

Every line ends with the id of the evidence item it came from. Numbers are computed by code, not written by a model. This report is the input to the Weekly Experimentation Brief, not the brief itself.

## 1. What happened last week

- In the week of Jun 24 to Jun 30, 9 campaigns spent $17,013 (-53% vs the prior week's $36,140 across 14 campaigns), producing 11,713 clicks (-64%) and 86 conversions (-67%). `[WEEK.totals]`
- Spend moved -$19,126 week over week. 8 campaigns that ended or wound down account for -$19,000 of it (99%); the 6 campaigns live all 14 days moved -$126; 0 campaigns launched. `[WEEK.spend_bridge]`
- For the 6 campaigns live through both weeks, spend was -1%, CTR moved from 2.18% to 1.97% (-10%) and conversions went from 60 to 57. `[WEEK.same_store]`
- Google: $7,453 across 5 campaigns, CTR 3.33%, 48 conversions; LinkedIn: $6,113 across 2 campaigns, CTR 0.84%, conversions not reported in the daily feed; Meta: $3,447 across 2 campaigns, CTR 1.72%, 38 conversions. `[WEEK.by_platform]`
- 6 campaigns were still live on Jun 30 and 0 are scheduled to run past it. Weekly spend is $17,013, down 91% from the peak week of Mar 04 ($194,291, 50 campaigns). The 9 campaigns live this week were 7 Demo, 1 Content Download, 1 Webinar. `[WEEK.program_status]`

What cannot be said yet: Everything from Jun 17 to Jun 30 is inside the attribution lag window (source flag). Measured against each campaign's own prior 28 days, conversions in the window are 96% of what their clicks would normally produce, but qualified leads are only 27% of what their conversions would normally produce (10 of 10 comparable campaigns are below their own baseline). Lead capture is current; qualification and everything after it is not. 14 campaigns carry the immature flag in the summary. `[DQ.attribution_lag]`

### Campaigns live in the week

| Campaign | Platform | Offer | Theme | Audience | Days live | Spend | CTR | vs own baseline | Age (days) | Past fatigue point |
|---|---|---|---|---|---|---|---|---|---|---|
| C001 | Google | Demo | Security | Law Firm - Mid-Market | 7 | $1,485 | 3.02% | -0% | 55 | no |
| C016 | Google | Content Download | Customer Proof | In-House - Mid-Market | 1 | $262 | 3.27% | -3% | 58 | no |
| C022 | Google | Demo | Speed | In-House - Enterprise | 2 | $2,627 | 3.73% | -1% | 51 | no |
| C038 | LinkedIn | Demo | Speed | Law Firm - Enterprise | 7 | $1,990 | 1.02% | -10% | 47 | no |
| C043 | Google | Demo | ROI | Law Firm - Enterprise | 1 | $336 | 3.46% | -3% | 56 | no |
| C048 | Meta | Webinar | Speed | Law Firm - Mid-Market | 7 | $1,562 | 1.76% | -3% | 47 | yes |
| C067 | Google | Demo | Customer Proof | Law Firm - Enterprise | 7 | $2,744 | 3.11% | -5% | 47 | no |
| C119 | LinkedIn | Demo | Customer Proof | In-House - Mid-Market | 7 | $4,123 | 0.76% | -24% | 60 | yes |
| C123 | Meta | Demo | Speed | In-House - Enterprise | 7 | $1,885 | 1.69% | -6% | 47 | yes |

## 2. Why it looks this way

- Efficiency benchmarks use 114 campaigns with settled attribution ($2,816,960 of spend, 19,053 opportunities), blended $635 of pipeline per dollar and $148 per opportunity. 14 campaigns flagged immature are excluded. `[BENCH.overall]`
- By objective, Webinar returns $1,135 of pipeline per dollar (1.42x comparable campaigns) on 41% of spend, while Demo returns $246 (0.46x) on 49% of spend. Webinar is above benchmark in 3 of 3 platform cells with enough spend; Demo is below in 3 of 3. `[SEG.objective]`
- Google Webinar went from 55% to 5% of platform spend; Google Demo went from 42% to 92% of platform spend (last 8 weeks versus everything earlier). `[MIX.objective]`
- By platform, Google returns $1,307 of pipeline per dollar (1.86x comparable campaigns) on 31% of spend, while LinkedIn returns $25 (0.06x) on 31% of spend. Google is above benchmark in 3 of 3 objective cells with enough spend; LinkedIn is below in 3 of 3. `[SEG.platform]`
- Google: $11 per lead, 63% qualify, 26% of those become opportunities, $71 per opportunity; LinkedIn: $98 per lead, 44% qualify, 6% of those become opportunities, $3,555 per opportunity; Meta: $10 per lead, 30% qualify, 20% of those become opportunities, $164 per opportunity. `[FUNNEL.platform]`
- 24 settled campaigns produced no opportunities on $385,683 of spend: LinkedIn 24 of 41 ($385,683). By offer: 18 Demo, 3 Content Download, 3 Webinar. `[ZERO.opportunities]`
- By theme, ROI returns $902 of pipeline per dollar (1.29x comparable campaigns) on 20% of spend, while Security returns $550 (0.65x) on 6% of spend. ROI is above benchmark in 6 of 6 platform x objective cells with enough spend; Security is below in 4 of 4. `[SEG.theme]`
- By audience, Law Firm - Enterprise returns $1,193 of pipeline per dollar (1.23x comparable campaigns) on 26% of spend, while In-House - Mid-Market returns $357 (0.70x) on 28% of spend. Law Firm - Enterprise is above benchmark in 5 of 5 platform x objective cells with enough spend; In-House - Mid-Market is below in 6 of 7. `[SEG.audience]`
- No region stands out once platform x objective is held constant: like-for-like indexes run from 0.93x (DACH) to 1.10x (UK). The raw spread of 0.52x to 1.18x comes from which platforms and offers each region was given. `[SEG.region]`
- Google CTR shows no decay with age; LinkedIn CTR holds for 7 weeks, then slips to 87% of its launch level in week 8 and 71% by week 10; Meta CTR holds for 6 weeks, then slips to 95% of its launch level in week 7 and 79% by week 9. `[FATIGUE.curve]`
- Strongest pairings against comparable campaigns: ROI for In-House - Enterprise (1.58x), ROI for Law Firm - Enterprise (1.52x), AI Productivity for Law Firm - Enterprise (1.15x). Weakest: Workflow Automation for Law Firm - Mid-Market (0.69x), Customer Proof for Law Firm - Mid-Market (0.67x), Customer Proof for In-House - Mid-Market (0.64x). `[THEME.by_audience]`

### Pipeline per dollar by platform and offer (settled campaigns)

| Platform | Content Download | Demo | Webinar |
|---|---|---|---|
| Google | $1,216 (1% of spend) | $612 (14% of spend) | $1,953 (16% of spend) |
| LinkedIn | $102 (4% of spend) | $5 (23% of spend) | $61 (5% of spend) |
| Meta | $671 (5% of spend) | $262 (12% of spend) | $765 (21% of spend) |

## 3. What the experiment log can and cannot support

- Of 18 logged experiments, 6 are trusted, 9 are directional and 3 are rejected for short runtime or small sample. 2 logged wins or losses are overturned (E012, E013). Campaign data disagrees with E003, E004, E009, E013; for a valid test that is a reason to re-confirm, not to overturn. `[EXP.summary]`

| Test | Platform | Hypothesis | Logged | Days | Sample | Metric | Agent rating | Campaign data |
|---|---|---|---|---|---|---|---|---|
| E001 | Meta | ROI vs productivity messaging | Win +18% (High) | 28 | 410 | Qualified pipeline per $ | **trusted** | agrees |
| E002 | Meta | Video vs static for In-House | Win +14% (High) | 35 | 360 | Opportunity rate | **directional** | agrees |
| E003 | LinkedIn | Webinar vs content download | Win +22% (Medium) | 42 | 180 | ARR per $ | **directional** | disagrees |
| E004 | Meta | Talk to Sales vs Book Demo | Neutral +2% (High) | 31 | 520 | Demo conversion rate | **directional** | disagrees |
| E005 | Meta | Stock photo vs product UI | Loss -16% (High) | 24 | 300 | Qualified lead rate | **trusted** | not observable |
| E006 | Meta | Speed messaging vs ROI | Loss -11% (Medium) | 21 | 210 | Pipeline per $ | **directional** | agrees |
| E007 | Meta | Broad legal vs role-targeted | Loss -9% (Medium) | 18 | 160 | Qualified lead rate | **directional** | not observable |
| E008 | Meta | Carousel vs static | Neutral +3% (Medium) | 20 | 145 | Opportunity rate | **directional** | agrees |
| E009 | Meta | Customer proof vs productivity | Win +12% (High) | 30 | 330 | Pipeline per $ | **trusted** | disagrees |
| E010 | Google | Max conversions vs target CPA | Win +8% (Medium) | 26 | 240 | Qualified pipeline per $ | **directional** | not observable |
| E011 | Google | Security messaging vs workflow | Inconclusive +9% (Low) | 3 | 18 | CTR | **rejected** | no claim |
| E012 | Meta | Video vs static for Meta | Win +21% (Low) | 4 | 24 | CTR | **rejected** | unclear |
| E013 | Google | Demo vs webinar | Win +15% (Low) | 5 | 31 | Lead conversion rate | **rejected** | disagrees |
| E014 | Google | ROI vs productivity messaging - repeat | Win +17% (High) | 29 | 390 | Qualified pipeline per $ | **trusted** | agrees |
| E015 | LinkedIn | Register vs Save Your Seat | Neutral +1% (High) | 27 | 270 | Registration rate | **directional** | agrees |
| E016 | Google | Customer logo wall vs quote card | Win +19% (High) | 34 | 310 | Opportunity rate | **trusted** | not observable |
| E017 | LinkedIn | CFO targeting vs legal leaders | Loss -23% (High) | 40 | 290 | Qualified pipeline per $ | **trusted** | not observable |
| E018 | Meta | Automation vs AI productivity | Win +10% (Medium) | 25 | 205 | Pipeline per $ | **directional** | unclear |

## 4. Ranked signals: where a test would pay off

Signals are inputs to experiment design, not experiments. Ranked by strength of evidence, then size.

**1. Google budget moved from Webinar to Demo** (strong) `[SIG.01]`
In the last 8 weeks Google Webinar fell from 55% to 5% of platform spend while Demo rose from 42% to 92%. In settled campaigns Google Webinar returns 3.2x the pipeline per dollar of Google Demo. The only test favoring Demo (E013) is rejected as a false winner.
- Test angle: Head-to-head Webinar vs Demo on Google, same audience and theme, read on pipeline per dollar after attribution settles.
- Caution: The mix shift is a fact. Why it happened is not in the data.
- Evidence: MIX.objective, SEG.platform_objective, SEG.objective, EXP.E013

**2. E013 is logged as a win but is not a valid read** (strong) `[SIG.02]`
E013 (Demo vs webinar, Google) is logged as Win +15% but is not a valid read: ran 5 days (minimum 14); sample of 31 (minimum 100); primary metric 'Lead conversion rate' is a proxy, not a business outcome; logged confidence is Low. Campaign data disagrees: Demo returns 0.31x the pipeline per dollar of Webinar in settled campaigns on Google (18 vs 15 campaigns).
- Test angle: Re-run 'Demo vs webinar' at full length and sample on an outcome metric before acting on it.
- Caution: Until re-run, this result should be removed from the team's list of learnings.
- Evidence: EXP.E013, EXP.summary

**3. Google beats comparable campaigns** (strong) `[SIG.03]`
Google (platform) returns 1.86x the pipeline of comparable campaigns, above benchmark in all 3 cells with enough spend. It takes 31% of settled spend and 37% of the last 8 weeks' spend. Like for like, that is pipeline worth 29% of the program total gained (modeled).
- Test angle: Controlled test that scales Google against the current mix, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.platform, SEG.platform_objective

**4. Demo trails comparable campaigns** (strong) `[SIG.04]`
Demo (objective) returns 0.46x the pipeline of comparable campaigns, below benchmark in all 3 cells with enough spend. It takes 49% of settled spend and 61% of the last 8 weeks' spend. Like for like, that is pipeline worth 23% of the program total not realized (modeled).
- Test angle: Controlled test that moves budget away from Demo toward the stronger alternative, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.objective, SEG.platform_objective

**5. Webinar beats comparable campaigns** (strong) `[SIG.05]`
Webinar (objective) returns 1.42x the pipeline of comparable campaigns, above benchmark in all 3 cells with enough spend. It takes 41% of settled spend and 22% of the last 8 weeks' spend. Like for like, that is pipeline worth 22% of the program total gained (modeled).
- Test angle: Controlled test that scales Webinar against the current mix, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.objective, SEG.platform_objective, EXP.E003

**6. LinkedIn trails comparable campaigns** (strong) `[SIG.06]`
LinkedIn (platform) returns 0.06x the pipeline of comparable campaigns, below benchmark in all 3 cells with enough spend. It takes 31% of settled spend and 23% of the last 8 weeks' spend. Like for like, that is pipeline worth 19% of the program total not realized (modeled).
- Test angle: Controlled test that moves budget away from LinkedIn toward the stronger alternative, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.platform, SEG.platform_objective

**7. 24 of 41 LinkedIn campaigns produced no opportunities** (strong) `[SIG.07]`
24 of 41 settled LinkedIn campaigns produced zero opportunities on $385,683 of spend.
- Test angle: Holdout test of LinkedIn's real contribution before cutting it, since last-touch attribution can hide influence on enterprise deals.
- Caution: Do not read this as 'turn the channel off'. Read it as 'prove what it contributes'.
- Evidence: ZERO.opportunities, SEG.platform, SEG.platform_objective

**8. Law Firm - Enterprise beats comparable campaigns** (strong) `[SIG.08]`
Law Firm - Enterprise (audience) returns 1.23x the pipeline of comparable campaigns, above benchmark in all 5 cells with enough spend. It takes 26% of settled spend and 13% of the last 8 weeks' spend. Like for like, that is pipeline worth 9% of the program total gained (modeled).
- Test angle: Controlled test that scales Law Firm - Enterprise against the current mix, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.audience, SEG.platform_objective

**9. ROI beats comparable campaigns** (strong) `[SIG.09]`
ROI (theme) returns 1.29x the pipeline of comparable campaigns, above benchmark in all 6 cells with enough spend. It takes 20% of settled spend and 15% of the last 8 weeks' spend. Like for like, that is pipeline worth 6% of the program total gained (modeled).
- Test angle: Controlled test that scales ROI against the current mix, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.theme, SEG.platform_objective, EXP.E001, EXP.E006, EXP.E014

**10. Security trails comparable campaigns** (strong) `[SIG.10]`
Security (theme) returns 0.65x the pipeline of comparable campaigns, below benchmark in all 4 cells with enough spend. It takes 6% of settled spend and 3% of the last 8 weeks' spend. Like for like, that is pipeline worth 3% of the program total not realized (modeled).
- Test angle: Controlled test that moves budget away from Security toward the stronger alternative, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.theme, SEG.platform_objective

**11. Customer Proof trails comparable campaigns** (strong) `[SIG.11]`
Customer Proof (theme) returns 0.75x the pipeline of comparable campaigns, below benchmark in all 4 cells with enough spend. It takes 9% of settled spend and 24% of the last 8 weeks' spend. Like for like, that is pipeline worth 2% of the program total not realized (modeled).
- Test angle: Controlled test that moves budget away from Customer Proof toward the stronger alternative, measured on pipeline per dollar.
- Caution: Observational gap. Confirms where to test, not the size of the win.
- Evidence: SEG.theme, SEG.platform_objective, EXP.E009

**12. Meta creative wears out after week 6** (strong) `[SIG.12]`
Meta CTR holds for 6 weeks of a campaign's life and is at 79% of launch level by week 9. 21 campaigns ran past that point, putting $190,139 (17% of Meta spend) behind tired creative.
- Test angle: Rotate in a fresh creative at day 42 versus letting the original run, on Meta.
- Caution: Fatigue is measured on CTR. Whether it carries through to pipeline is untested.
- Evidence: FATIGUE.curve, DQ.creative_age

**13. LinkedIn creative wears out after week 7** (strong) `[SIG.13]`
LinkedIn CTR holds for 7 weeks of a campaign's life and is at 71% of launch level by week 10. 18 campaigns ran past that point, putting $94,289 (10% of LinkedIn spend) behind tired creative.
- Test angle: Rotate in a fresh creative at day 49 versus letting the original run, on LinkedIn.
- Caution: Fatigue is measured on CTR. Whether it carries through to pipeline is untested.
- Evidence: FATIGUE.curve, DQ.creative_age

**14. Learnings the team is relying on that are not confirmed** (moderate) `[SIG.14]`
8 experiments are usable only as direction (E002, E003, E004, E006, E007, E009, E010, E018). Settled campaign data points the other way on E003, E004, E009.
- Test angle: A confirmation test for whichever of these the next quarter's plan depends on most.
- Caution: Disagreement with observational data is a reason to re-test, not proof the experiment was wrong.
- Evidence: EXP.E002, EXP.E003, EXP.E004, EXP.E006, EXP.E007, EXP.E009, EXP.E010, EXP.E018

**15. E012 is logged as a win but is not a valid read** (moderate) `[SIG.15]`
E012 (Video vs static for Meta, Meta) is logged as Win +21% but is not a valid read: ran 4 days (minimum 14); sample of 24 (minimum 100); primary metric 'CTR' is a proxy, not a business outcome; logged confidence is Low. Same question as E002.
- Test angle: Re-run 'Video vs static for Meta' at full length and sample on an outcome metric before acting on it.
- Caution: Until re-run, this result should be removed from the team's list of learnings.
- Evidence: EXP.E012, EXP.summary

**16. Meta buys cheap leads that do not qualify** (moderate) `[SIG.16]`
Meta has the lowest cost per lead ($10) but only 30% of its leads qualify, against 63% on Google. 42 of its campaigns carry the source's 'High volume / low quality' flag.
- Test angle: Tighter targeting or a qualifying step on Meta, judged on cost per opportunity rather than cost per lead.
- Caution: A lower lead volume is the expected and acceptable cost of this test.
- Evidence: FUNNEL.platform, DQ.source_flags, EXP.E007

**17. Security has never had a valid test** (moderate) `[SIG.17]`
Security has 7 settled campaigns on 6% of spend and 0 valid experiments (E011 rejected). Its campaigns return 0.65x comparable campaigns, and it exists only in Static format.
- Test angle: A small, properly powered read on Security before deciding whether to invest in more creative for it.
- Caution: Current evidence says Security underperforms. This is an exploration bet, not a scaling bet.
- Evidence: SEG.theme, CREATIVE.gaps, EXP.E011

**18. CR021 has never run** (context) `[SIG.18]`
CR021 (Workflow Automation, Video, Law Firm) is active in the library with zero campaigns.
- Test angle: Use CR021 as the fresh variant in a rotation or format test for Law Firm audiences.
- Evidence: CREATIVE.gaps, THEME.by_audience

**19. No campaigns are scheduled past the reporting week** (context) `[SIG.19]`
6 campaigns were still live on Jun 30 and 0 are scheduled to run past it. Weekly spend is $17,013, down 91% from the peak week of Mar 04 ($194,291, 50 campaigns). The 9 campaigns live this week were 7 Demo, 1 Content Download, 1 Webinar.
- Test angle: Treat the next launches as the experiment slate. Every new campaign can carry a test cell at no extra cost.
- Evidence: WEEK.program_status, WEEK.spend_bridge

## 5. Creative

- 1 active creative has never run: CR021 (Workflow Automation, Video, Law Firm). Format gaps: Security for In-House has no Carousel or Video; Security for Law Firm has no Carousel or Video. `[CREATIVE.gaps]`
- Against campaigns on the same platform and offer, CR001 (ROI Static, Law Firm) performs best at 1.45x and CR016 (Customer Proof Static, In-House) worst at 0.40x. `[CREATIVE.performance]`

## 6. Data quality: what is wrong and how it is handled

- **Daily and summary files disagree on outcomes.** Spend, impressions and clicks reconcile exactly between the daily and summary tables, but the daily table carries only 16% of conversions, 13% of qualified leads, 4% of opportunities and 3.5% of pipeline. `[DQ.reconciliation]`
  - Handling: lifetime efficiency (pipeline per dollar, cost per opportunity) comes from the campaign summary only.
  - Handling: the daily table is used for delivery trends and for comparing a campaign with itself over time.
  - Handling: outcome levels from the two tables are never combined in one calculation.
  - Assumption A1: the summary is the CRM-reconciled record; daily outcomes are a partial same-day view.
- **Some campaigns have no daily outcome data at all.** 20 campaigns show zero conversions in the daily table while the summary credits them with 2,403 (20 on LinkedIn), and 73 campaigns with opportunities in the summary show none in the daily table. `[DQ.daily_outcome_gaps]`
  - Handling: a zero in the daily outcome columns is treated as 'not reported', never as 'no result'.
- **Daily rows with missing CRM pipeline and ARR.** 45 of 5,691 daily rows (0.8%) across 38 campaigns have no pipeline or ARR value, covering $26,453 of spend and 6 opportunities. `[DQ.missing_crm]`
  - Handling: missing values stay missing. They are excluded from pipeline rates and never filled with zero.
- **Inconsistent audience labels.** 12 of 128 campaigns use a non-standard audience label (Enterprise Legal, IH MM, LF ENT, Law Firm MM). The agent's alias map resolves 128 of 128 campaigns to the same label as the source's cleaned field. `[DQ.audience_labels]`
  - Handling: all analysis groups on the canonical label. An unknown label is surfaced, not guessed.
- **Recent downstream data is incomplete.** Everything from Jun 17 to Jun 30 is inside the attribution lag window (source flag). Measured against each campaign's own prior 28 days, conversions in the window are 96% of what their clicks would normally produce, but qualified leads are only 27% of what their conversions would normally produce (10 of 10 comparable campaigns are below their own baseline). Lead capture is current; qualification and everything after it is not. 14 campaigns carry the immature flag in the summary. `[DQ.attribution_lag]`
  - Handling: for the reporting week only spend, impressions, clicks and conversions are treated as final.
  - Handling: qualified leads, opportunities and pipeline for the window are shown as provisional and never used to judge performance.
  - Handling: campaigns flagged immature are excluded from efficiency benchmarks.
- **Campaign-to-experiment links are unreliable.** Of 60 campaigns linked to an experiment, 42 point to an experiment that ran on a different platform and 30 did not overlap the experiment's dates. `[DQ.experiment_links]`
  - Handling: linked_experiment_id is not used to attribute campaign results to an experiment.
- **creative_age_days measures campaign age, not creative exposure.** creative_age_days equals days since campaign launch in 100% of rows and tops out at 70 days, yet 30 creatives ran in more than one campaign and the most reused have been in market for up to 172 days. `[DQ.creative_age]`
  - Handling: fatigue is measured within a campaign. True audience exposure to a reused creative is longer than the field suggests.
- **Campaign format does not always match the creative library.** 45 campaigns report a format that differs from their creative's library format. 43 are Google campaigns, where the field holds the ad type (RSA, Responsive Display) rather than the creative format. 2 are genuine mismatches on other platforms (C081, C095). `[DQ.creative_format]`
  - Handling: format comparisons exclude Google.
- **Flags carried in the source data.** Campaign-level flags in the summary: High volume / low quality (42), Attribution immature (14), Under-tested theme (8). `[DQ.source_flags]`

## 7. Assumptions

- **A1.** The campaign summary is the CRM-reconciled record of lifetime outcomes. The daily table is a partial, same-day view of outcomes. *Why:* Spend and clicks match exactly across the two tables but daily outcomes are a small fraction of summary outcomes. *If wrong:* If the daily table is the truth, every efficiency number in the brief is overstated and the first job is fixing the summary.
- **A2.** 'Last week' is the 7 days ending on the latest date in the data, compared with the 7 days before. *Why:* It is what a live weekly run would see. Full 7-day windows absorb the weekday pattern. *If wrong:* The window is defined in one function (build_windows). Nothing else changes.
- **A3.** Anything the source flags as immature is excluded from performance judgments and efficiency benchmarks. *Why:* Qualified leads inside the window are about a quarter complete when measured against each campaign's own history. *If wrong:* If the lag is longer than the flag suggests, recent campaigns will look worse than they are for longer.
- **A4.** Pipeline per dollar is the primary success metric, supported by cost per opportunity and ARR per dollar. CTR, CPC and cost per lead are diagnostics only. *Why:* The brief asks for qualified pipeline, opportunities and revenue over click metrics. *If wrong:* Change outcome_metrics in config. Rankings are recomputed.
- **A5.** In the experiment log the first-named arm is the variant, so 'Win' on 'A vs B' means A beat B. *Why:* Every note in the log that names a winner is consistent with this reading. *If wrong:* The direction of each learning flips. Trust tiers do not change.
- **A6.** Absolute dollar magnitudes are synthetic. Ratios between segments are the signal. *Why:* The data dictionary says the data is synthetic, and pipeline per dollar is implausibly high in absolute terms. *If wrong:* No change to rankings.
- **A7.** An experiment needs at least 14 days and a sample of 100 to count as a read; a new test needs at least 28 days. *Why:* Two weekly cycles is the floor for any read, and pipeline outcomes need longer than lead outcomes. *If wrong:* These are defaults in config for the marketing lead to set.
- **A8.** No proposed test may exceed the highest daily budget the team has already run, or a fixed total budget ceiling. *Why:* The agent should never ask for more exposure than the team has already chosen to take. *If wrong:* Raise the ceilings in config. Approval is still required for every launch.
