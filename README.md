# Challenge 24 Solver
Challenge 24 is an arithmetic game I played a lot in school. Given
4 numbers (typically integers in [0, 9], but not necessarily), come up
with an artihmetic expression that uses each number exactly once
and equals 24.
* E.g.: If the numbers were `1, 2, 3, 4` then you could do
`1 * 2 * 3 * 4 = 24`

Clearly with only four numbers, it's easy enough to enumerate all
possible expressions and see which ones evaluate to 24.

That's where this started, but once I did that I started playing
with ways to get more clever and tested it against more than 4 numbers
(spoiler, it blows up very quickly).

## Web interface
Most of my time was spent on perfecting `24.py`, but I figured
what's the point of having these fun toys without anyone to
share them with? So I made a simple web interface
at http://24.broccoli-rob.me (plug: also checkout <http://broccoli-rob.me> for a good time)