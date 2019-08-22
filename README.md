Basically a playground to mess around with stats and numbers.

opr_calc calculates opr pretty similarly to the blue alliance. Instead of an event-by-event basis, you can calculate for any bunch of matches, so you can calculate global opr for the entire district.

rpr_calc is very similar to opr_calc, but it calculates what I call rpr. As opr is a metric to approximate alliance score, rpr is a metric to approximate additional ranking points. In the case of the 2019 game, this would be for filling a rocket or something.

predict.py has the code for match prediction. I tested it on the 2019pnw district, and it got 70% accuracy for match prediction. It can also predict all the matches for an event, and also use rpr to predict final rankings at the end of qualifiers. In the case of 2019pncmp, 6 of the 8 predicted to be in the top 8 were correct. The rankings are evaluated using the earth movers distance cost function, where a lower cost is better. The cost is printed when running predict.py.

gen_data is pretty much obsolete.

alliance_selection tries to predict alliance selections but it's super super broken right now, so don't even touch it.