% model(ATOM,MODEL) indicates that ATOM holds in MODEL

used(Q) :- query(temporal(Q,T),_).
used(Q) :- used(__negation__(Q)).
used(Q) :- used(__conjunction__(Q,_)).
used(Q) :- used(__conjunction__(_,Q)).
used(Q) :- used(__disjunction__(Q,_)).
used(Q) :- used(__disjunction__(_,Q)).
used(Q) :- used(__next__(Q)).
used(Q) :- used(__previous__(Q)).
used(Q) :- used(__always__(Q)).
used(Q) :- used(__eventually__(Q)).
used(Q) :- used(__until__(Q,_)).
used(Q) :- used(__until__(_,Q)).
used(Q) :- used(__since__(Q,_)).
used(Q) :- used(__since__(_,Q)).

t(T) :- model(time(T), __model__).
holds(F,T) :- used(F), t(T), model(holds(F,T), __model__).
holds(__disjunction__(F,G),T) :- used(__disjunction__(F,G)), t(T), holds(G,T).
holds(__disjunction__(F,G),T) :- used(__disjunction__(F,G)), t(T), holds(F,T).
holds(__conjunction__(F,G),T) :- used(__conjunction__(F,G)), t(T), holds(F,T), holds(G,T).
holds(__negation__(F),T) :- used(__negation__(F)), t(T), not holds(F,T).
holds(__next__(F),T) :- used(__next__(F)), t(T), t(T+1), holds(F,T+1).
holds(__previous__(F),T) :- used(__previous__(F)), t(T), t(T-1), holds(F,T-1).
holds(__always__(F),T) :- used(__always__(F)), t(T), holds(F,I) : t(I), I >= T.
holds(__eventually__(F),T) :- used(__eventually__(F)), t(T), t(I), holds(F,I), I >= T.
holds(__until__(F,G),T) :- used(__until__(F,G)), t(T), t(T'), T <= T', holds(G,T'), holds(F,I): t(I), T <= I, I < T'.
holds(__since__(F,G),T) :- used(__since__(F,G)), t(T), t(T'), T >= T', holds(G,T'), holds(F,I): t(I), T' < I, I <= T.
