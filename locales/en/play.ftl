play-single-device-spy-game-prepare = Prepare

    Player: { $player_index }/{ $player_count }
    .button-view-role = View role

play-single-device-spy-game-view-role = { $role ->
    [spy] You are a spy
   *[citizen] You are a citizen. Word: { $secret_word }
}
    .button-proceed = Proceed

play-single-device-spy-game-discuss = Discuss
    .button-finish = Finish

play-single-device-spy-game-results = { $count ->
    [0]
        Results

        No one was the spy!

        Word: { $secret_word }
    [one]
        Results

        Player { $spies } was the spy!

        Word: { $secret_word }
   *[other]
        Results

        Players { $spies } were the spies!

        Word: { $secret_word }
}
    .button-play-again = Play Again