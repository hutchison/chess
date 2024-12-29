#set page(
  paper: "a4",
  margin: (x: 1.8cm, y: 1.5cm),
)

#set text(
  font: "Minion Pro",
  size: 10pt,
)

#import "@preview/board-n-pieces:0.5.0": board, starting-position, fen

#let last-move-square-mark = {
  square(
    fill: rgb("#0091c7a0"),
  )
}

= Taktiktraining

Was ist der beste Zug?

Folgende Fragen können bei der Suche helfen:

- Gibt es eine erzwungene Mattsequenz? Überprüfe die schachgebenden Züge. \
  Überprüfe Züge, die dem König die Fluchtfelder nehmen.
- Kannst du ein Matt androhen, was zu Materialgewinn führt?
- Gibt es ungedeckte Figuren?
- Kann ein Springer gabeln?
- Gibt es überladene Figuren?
- Gibt es eine Fesselung (Pin), die man ausnutzen kann?

#pagebreak()

#align(center, [
  #board(
    fen("r4b1r/pppqk1p1/3p1nQ1/3Pp1Bp/2P3bP/5NP1/PP1N1P2/2KR3R b - - 2 14"),
    display-numbers: true,
    marked-squares: "e1 c1",
    marked-white-square-background: last-move-square-mark,
    marked-black-square-background: last-move-square-mark,
  )
])
