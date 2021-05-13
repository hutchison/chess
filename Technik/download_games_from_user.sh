TOKEN=$(cat lichess_secret_token.txt)
USER=$1

curl "https://lichess.org/api/games/user/${USER}?clocks=true" \
	-H "Authorization: Bearer $TOKEN" \
	-o "${USER}_games.pgn"
