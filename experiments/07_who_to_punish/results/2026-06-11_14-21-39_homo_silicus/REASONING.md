
## vote1

### player  (rep 0, history=This is the start of the game; there is no history yet., item=low, me=A, persona=You only care about your own pay-off., target_group=LESS than the group average)
- **vote = Yes**
  - I want the rule that permits punishing below‑average contributors because it creates a deterrent against free‑riding, raising overall contributions (and thus my share of the public good) while I can choose not to incur any punishment costs myself.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=avg, me=A, persona=You only care about your own pay-off., target_group=exactly the group average)
- **vote = No**
  - I prefer to block punishment of average contributors because if everyone (including me) contributes the same amount—especially zero—we’d all be vulnerable to costly punishment. Disallowing it protects my payoff.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=high, me=A, persona=You only care about your own pay-off., target_group=MORE than the group average)
- **vote = No**
  - I want others to contribute as much as possible, since each dollar they put in gives me $0.40 without costing me anything. Allowing punishment of high contributors would deter contributions and lower my payoff.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=low, me=B, persona=You only care about the total pay-off of all players., target_group=LESS than the group average)
- **vote = Yes**
  - Allowing punishment can deter low contributions, increasing overall contributions which yield a higher total payoff despite the punishment cost.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=avg, me=B, persona=You only care about the total pay-off of all players., target_group=exactly the group average)
- **vote = No**
  - I chose “No” because allowing punishment of players who merely match the group average creates opportunities for costly punishments that reduce the total payoff (each punishment costs the group $1.25), and there’s no benefit to punishing average contributors for maximizing overall earnings.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=high, me=B, persona=You only care about the total pay-off of all players., target_group=MORE than the group average)
- **vote = No**
  - I want to minimize harmful punishments that lower total welfare, and allowing punishment of high contributors would discourage contributions and waste resources.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=low, me=C, persona=You only care about the total pay-off of all players., target_group=LESS than the group average)
- **vote = Yes**
  - Allowing punishment of below‑average contributors can incentivize higher contributions. Each extra dollar contributed yields $1.60 in total benefits, while a punishment costs the group $1.25 in total. If punishment raises contributions, the net effect on

### player  (rep 0, history=This is the start of the game; there is no history yet., item=avg, me=C, persona=You only care about the total pay-off of all players., target_group=exactly the group average)
- **vote = No**
  - I vote against allowing punishment of players who contributed exactly the group average, since any punishment reduces total pay‑offs and targeting average contributors is unnecessary for improving group welfare.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=high, me=C, persona=You only care about the total pay-off of all players., target_group=MORE than the group average)
- **vote = No**
  - Disallowing punishment of high contributors avoids discouraging cooperation; punishing them would lower total contributions and, combined with the cost of punishing, reduces overall group welfare.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=low, me=D, persona=You only care about your own pay-off., target_group=LESS than the group average)
- **vote = Yes**
  - Allowing punishment deters free‑riding, encouraging higher contributions that raise the total return (0.40 per dollar to each player). This improves my expected earnings compared to the no‑punishment scenario where everyone would likely contribute nothing.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=avg, me=D, persona=You only care about your own pay-off., target_group=exactly the group average)
- **vote = No**
  - I want to keep the option to punish only below‑average free riders. Allowing punishment of those at the average could let me be forced to punish or be punished for contributing a typical amount, which reduces my own payoff.

### player  (rep 0, history=This is the start of the game; there is no history yet., item=high, me=D, persona=You only care about your own pay-off., target_group=MORE than the group average)
- **vote = No**
  - I don’t want to be vulnerable to punishment for contributing above the group average, since that could reduce my earnings without any direct benefit to me.

## p1_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=1, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 0**
  - I contribute nothing because contributing reduces my own payoff (cost $1 per $ contributed but only returns $0.40 to me). Since punishment only targets those who contribute less than the group average, and the likely average will be 0 if everyone is selfish, I won’t be punished for contributing 0. Hence 0 maximizes my payoff in period 1.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=1, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contribute the full $10 so that everyone’s contribution equals the group average, avoiding any punishable players and maximizing total group payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=1, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contribute the full $10 to maximize the total social payoff (each $ added raises total payoff by $0.6) and to avoid being below the group average, which would make me punishable and reduce total earnings.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=1, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contribute the full $10 to avoid being below the group average (which would make me punishable) and because a full contribution maximizes the total fund payoff, giving me the highest possible payoff in this period.

## p1_punish

### player  (rep 0, avg=7.5, contributions=[10, 10, 10, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - I choose not to punish because each dollar of punishment reduces total welfare by $1.25, so the socially optimal choice is to impose no punishment.

### player  (rep 0, avg=7.5, contributions=[10, 10, 10, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - I avoid punishing because each $1 I reduce from another player costs me $0.25, decreasing the total payoff by $1.25 overall. Since my objective is to maximize the sum of everyone’s earnings, the optimal choice is not to punish at all.

### player  (rep 0, avg=7.5, contributions=[10, 10, 10, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, my_contribution=10, persona=You only care about your own pay-off., target=A, target_contribution=0)
- **punish = 0**
  - Because punishing A costs me $0.25 for each $1 I reduce their earnings, while it gives me no direct benefit, the best selfish choice is not to punish at all. Hence I reduce A's earnings by $0.

## p2_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=2, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = None**

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=2, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contribute the full $10 to maximize the group’s total earnings (each $ yields $1.60 total) and to avoid being a punishable low‑contributor, which would reduce overall welfare.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=2, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - Choosing the maximum contribution ensures the fund yields the highest total return (each dollar adds $1.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=2, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = None**

## p2_punish

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, my_contribution=0, persona=You only care about your own pay-off., target=D, target_contribution=0)
- **punish = 0**
  - <!-- I choose not to punish because it only costs me $0.25 per $1 reduction in D's earnings and gives me no direct benefit in this period. -->

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - No punishment increases total welfare because each $1 of punishment cuts the target’s payoff by $1 and also costs the punisher $0.25, decreasing the sum of all players’ earnings by $1.25. Hence the payoff‑maximizing choice is to punish $0.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, my_contribution=10, persona=You only care about the total pay-off of all players., target=D, target_contribution=0)
- **punish = 0**
  - Because punishing costs $0.25 for each $1 it reduces a player’s earnings, it always lowers the total sum of pay‑offs (you lose 0.25 and the punished player loses 1). With no additional information about future effects, the welfare‑maximizing choice is not to punish at all.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - I choose not to punish because each dollar of punishment reduces the target’s earnings by $1 but costs me $0.25, lowering the total payoff by $1.25 per dollar—so any punishment would decrease the overall sum.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, my_contribution=10, persona=You only care about the total pay-off of all players., target=D, target_contribution=0)
- **punish = 0**
  - The punishment would lower D’s earnings by $1 while costing me $0.25, decreasing total welfare by $1.25 per punished dollar. Since I aim to maximize total payoff, I should not punish.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, my_contribution=0, persona=You only care about your own pay-off., target=A, target_contribution=0)
- **punish = 0**
  - I chose not to punish because each dollar of punishment costs me $0.25 while only reducing the other player's earnings, which does not increase my own payoff. Since my payoff is $10 (kept) + $8 (public‑goods return) minus any punishment cost, the optimal choice for maximizing my own earnings is to impose $0 reduction.

## p3_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=3, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = None**

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=3, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contribute the full $10 because each contributed dollar yields a net gain of $0.60 to total group welfare (return $1.60, cost $1). Punishment only reduces total payoff, so I avoid it and maximize the sum of all players’ earnings by contributing everything.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=3, persona=You only care about the total pay-off of all players., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 10**
  - I contributed the maximum because contributing raises total group payoff (each dollar yields $1.60 total returns) and no one will be below the average, so no punishment occurs.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=3, persona=You only care about your own pay-off., rule=Voted rules — may a player be punished for contributing... LESS than the group a...)
- **contribution = 0**
  - I choose not to contribute any amount. In the previous rounds, other players never punished low contributors, so I can keep my $10 while still receiving the $0.40 per dollar they put in the fund, maximizing

## p3_punish

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, my_contribution=0, persona=You only care about your own pay-off., target=D, target_contribution=0)
- **punish = 0**
  - I don’t gain any benefit from reducing D’s earnings, and each dollar of reduction costs me $0.25, so the best payoff‑maximizing choice is to spend nothing on punishment.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - Because each $1 of punishment cuts the target’s earnings by $1 but also costs me $0.25, it lowers the sum of all players’ payoffs by $1.25. To maximize total welfare, I should not punish at all.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, my_contribution=10, persona=You only care about the total pay-off of all players., target=D, target_contribution=0)
- **punish = 0**
  - We avoid punishment because each dollar of reduction costs us $0.25 while decreasing the target’s earnings by $1, resulting in a net loss of $1.25 to total group payoff. Hence, the welfare‑maximizing choice is not to punish.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, my_contribution=10, persona=You only care about the total pay-off of all players., target=A, target_contribution=0)
- **punish = 0**
  - Because punishing reduces the target's earnings by $1 while costing you $0.25, any punishment lowers total welfare. Since I care only about the group's total payoff, the optimal choice is not to punish at all.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, my_contribution=10, persona=You only care about the total pay-off of all players., target=D, target_contribution=0)
- **punish = 0**
  - Because punishing reduces the punished player's earnings by $1 while costing the punisher $0.25, the total welfare drops by $1.25 for each dollar of punishment.

### player  (rep 0, avg=5.0, contributions=[10, 10, 0, 0], history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, my_contribution=0, persona=You only care about your own pay-off., target=A, target_contribution=0)
- **punish = 0**
  - I’m not willing to incur any cost ( $0.25 per $

## vote2

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=low, me=A, persona=You only care about your own pay-off., target_group=LESS than the group average)
- **vote = No**
  - I want to avoid being punishable for free‑riding, since allowing punishment of those below the average would let others reduce my earnings at a cost to them. This protects my own payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=avg, me=A, persona=You only care about your own pay-off., target_group=exactly the group average)
- **vote = No**
  - I want to limit the situations in which I can be punished. Allowing punishment of players who contributed exactly the group average would let others target me (e.g., if everyone contributes $0, I'd be exactly average and could be punished), which could reduce my payoff. So I vote against allowing it.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=high, me=A, persona=You only care about your own pay-off., target_group=MORE than the group average)
- **vote = No**
  - I want to keep the high contributors safe from punishment so they’ll keep giving large amounts, which maximizes my own earnings as a free rider.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=low, me=B, persona=You only care about the total pay-off of all players., target_group=LESS than the group average)
- **vote = No**
  - I vote against allowing punishment for below‑average contributions because any punishment reduces total group earnings (cost $0.25 to the punisher and $1 to the target, a net loss of $1.25). Disallowing it eliminates this welfare loss.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=avg, me=B, persona=You only care about the total pay-off of all players., target_group=exactly the group average)
- **vote = No**
  - I vote against allowing punishment for players who contributed exactly the group average because punishment reduces total group earnings (punisher loses $0.25, target loses $1, net -$1.25). Allowing more cases for punishment would likely increase its use and lower the overall payoff, which I want to maximize.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=high, me=B, persona=You only care about the total pay-off of all players., target_group=MORE than the group average)
- **vote = No**
  - I chose “No” because allowing punishment of players who contributed more than the average would let group members target cooperators, reducing contributions and overall earnings. Since punishing always lowers total payoff (cost $0.25 + $1 loss), disallowing this rule avoids harmful sanctions and helps maintain higher group contributions.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=low, me=C, persona=You only care about the total pay-off of all players., target_group=LESS than the group average)
- **vote = Yes**
  - Allowing punishment of below‑average contributors lets us deter free‑riding; the extra contributions (each $ contributes $1.60 total) outweigh the $0.75 loss per punishment, increasing the group’s total payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=avg, me=C, persona=You only care about the total pay-off of all players., target_group=exactly the group average)
- **vote = No**
  - I chose “No” because allowing punishment (even for those who contributed exactly the average) would enable socially costly punishment actions that reduce total group earnings. Limiting punishment options maximizes the sum of all players’ pay‑offs.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=high, me=C, persona=You only care about the total pay-off of all players., target_group=MORE than the group average)
- **vote = No**
  - I voted against allowing punishment of players who contributed more than the average because punishment reduces total group earnings, and penalizing generous contributors would discourage contributions, lowering overall pay‑off.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=low, me=D, persona=You only care about your own pay-off., target_group=LESS than the group average)
- **vote = No**
  - I want to avoid being punished for free‑riding (contributing less than the average), so I vote to disallow punishing players who contribute less than the group average.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=avg, me=D, persona=You only care about your own pay-off., target_group=exactly the group average)
- **vote = None**

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., item=high, me=D, persona=You only care about your own pay-off., target_group=MORE than the group average)
- **vote = None**

## p4_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=4, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - I contribute nothing because each dollar I put in costs me $1 and only returns $0.40 to me, a net loss of $0.60, and no punishment is possible, so free‑riding maximizes my payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=4, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I chose the highest possible contribution because each dollar contributed raises total group payoff by $0.60, so to maximize the sum of all players’ earnings I should contribute the full $10.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=4, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I contribute the full $10 because each dollar put into the public fund returns $1.60 to the group, yielding a net social gain of $0.60 per dollar. Since I only care about total welfare, contributing maximally increases the group's total payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=4, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - Choosing 0 maximizes my payoff given the others' contributions (two players give 10, one gives 0). Contributing less raises my earnings because each dollar I keep yields $1 versus only $0.40 returned from the public good. Hence I free‑ride.

## p5_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=5, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - I contribute nothing because with a marginal return of $0.40 per $1 contributed, any positive contribution reduces my own earnings, and there’s no punishment or incentive mechanism to make my contribution influence future payouts. The dominant self‑interest strategy is to free‑ride.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=5, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I contribute the full $10 because each dollar put into the fund returns $0.40 to each of the four players, generating $1.60 total benefit, which is higher than the $0 benefit of keeping it (only $1 to me). Maximizing total payoff means contributing everything.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=5, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I contribute the full $10 because each dollar added to the public good returns $0.40 to each of the four players, yielding a total social benefit of $1.60 per dollar—greater than the $1 kept by not contributing. Maximizing total group payoff means everyone should contribute the maximum.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=5, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - I contribute nothing because contributing reduces my own payoff (each dollar contributed costs me $0.60 net) and punishment is disabled, so the selfish best response is to keep the full $10.

## p6_contrib

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=A, period=6, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - I contribute nothing because without any punishment the payoff function is 10 + 0.40·(others’ contributions) – 0.60·x, so any positive contribution lowers my own earnings. Free‑riding maximizes my payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=B, period=6, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I contribute the full $10 because the total group payoff rises with total contributions (total payoff = 40 + 0.6 × C). Contributing maximizes the sum of all players’ earnings, and no punishment or coordination mechanisms are available to change others’ behavior.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=C, period=6, persona=You only care about the total pay-off of all players., rule=The group voted to allow NO punishment at all.)
- **contribution = 10**
  - I keep contributing the full $10 because total welfare is 40 + 0.6 × (total contributions). The more we collectively contribute, the higher the sum of pay‑offs, and contributing less would only reduce the group’s total payoff.

### player  (rep 0, history=History so far: Vote 1 outcome: Voted rules — may a player be punished for contr..., me=D, period=6, persona=You only care about your own pay-off., rule=The group voted to allow NO punishment at all.)
- **contribution = 0**
  - I contribute nothing because without any punishment the individual payoff from contributing is negative (I lose $1 but only gain $0.40 back), so $0 maximizes my earnings.
