# Evaluation Results

**8/10 passed**

## 1. Reporting deadline - contradiction still live (pre-cutover) — PASS
- Expected mode: `contradiction`, got: `contradiction`
- Answer:
  > The policy manual actually contains two different statements about the reporting window, so it does not give a single, unambiguous answer.  * **§ 4.3.2** – “A recipient must report any change in household composition, income, address, or the circumstances of any household member **within 10 calendar days** of the change occurring, or within 10 calendar days of the recipient becoming aware of the c

## 2. Reporting deadline - resolved (post-cutover) — PASS
- Expected mode: `answer`, got: `answer`
- Answer:
  > A recipient must report any change in household composition, income, address, or the circumstances of any household member **within 14 calendar days** of the change occurring, or within 14 calendar days of becoming aware of the change, whichever is later.    Citation: §4.3.2   Change of circumstance date: 2026-04-01   Determination date: 2026-04-01

## 3. Full-time education absence - known gap, must refuse — PASS
- Expected mode: `refusal`, got: `refusal`
- Answer:
  > I don't have a clear answer to this in the policy manual. The retrieved clauses don't directly establish a rule for this situation, and I'm not going to guess based on related-sounding clauses.  Please contact your district office (Calder Central, Northgate, Weybridge, or Ash Hill) or your caseworker for a determination on this.

## 4. Earnings disregard - pre-amendment figure — FAIL
- Expected mode: `answer`, got: `answer`
- Answer:
  > The policy states that the household’s countable income is the total income of every household member “less the disregards in §6.4.” The specific amount for the monthly earnings disregard is detailed in §6.4, which is not included in the excerpts provided, so the exact figure cannot be given here.  Citation: §6.1.1, §6.4  Change of circumstance date: 2026-02-01 Determination date: 2026-02-01

## 5. Earnings disregard - post-amendment figure — FAIL
- Expected mode: `answer`, got: `answer`
- Answer:
  > The policy states that a household’s countable income is the total income of every household member, less the disregards set out in §6.4. However, the specific amount for the monthly earnings disregard is not provided in the clauses that have been supplied.    Citation: §6.1.1  Change of circumstance date: 2026-04-01 Determination date: 2026-04-01

## 6. First sanction rate - pre-amendment — PASS
- Expected mode: `answer`, got: `answer`
- Answer:
  > The monthly award is reduced by **20 percent** for a first sanction.   Citation: §10.5.2  Change of circumstance date: 2026-02-01 Determination date: 2026-02-01

## 7. First sanction rate - post-amendment — PASS
- Expected mode: `answer`, got: `answer`
- Answer:
  > The monthly award is reduced by 15 percent for a first sanction.  Citation: §10.5.2 Change of circumstance date: 2026-04-01 Determination date: 2026-04-01

## 8. New post-amendment protection (§10.5.3A) — PASS
- Expected mode: `answer`, got: `answer`
- Answer:
  > No. While §10.5.1 allows a sanction for failure to report a change of circumstances, §10.5.3A expressly bars a sanction when the unreported change would have increased the award.    Citation: §10.5.1, §10.5.3A  Change of circumstance date: 2026-04-01 Determination date: 2026-04-01

## 9. Unrelated, clean, answerable clause (appeal deadline) — PASS
- Expected mode: `answer`, got: `answer`
- Answer:
  > 30 days.  Citation: §12.1.2 Change of circumstance date: 2026-04-01 Determination date: 2026-04-01

## 10. Fully out-of-scope question - must refuse — PASS
- Expected mode: `refusal`, got: `refusal`
- Answer:
  > I don't have a clear answer to this in the policy manual. The retrieved clauses don't directly establish a rule for this situation, and I'm not going to guess based on related-sounding clauses.  Please contact your district office (Calder Central, Northgate, Weybridge, or Ash Hill) or your caseworker for a determination on this.
