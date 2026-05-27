play-single-device-spy-game-prepare =
    🤫 <b>Get ready to view your role</b>

    Each player must check their role privately. Only hold the phone when it’s your turn, and make sure no one else can see the screen.

    <b>Player { $player_index }/{ $player_count }</b>
    .button-view-role = 🔍 View role

play-single-device-spy-game-view-role = { $role ->
    [spy]
        🕵️‍♂️ <b>You are the Spy</b>

        Blend in with the Citizens and try to guess the secret word. Listen carefully to their answers and ask smart questions to collect clues without raising suspicion.
    *[citizen]
        👨 <b>You are a Citizen</b>

        Your mission is to identify the Spy without revealing the secret word. Ask clever questions and pay attention to answers to spot suspicious behavior.

        Secret word: <b>{ $secret_word }</b>
}
    .button-proceed = 👉 Proceed

play-single-device-spy-game-discuss =
    👀 <b>Discussion time!</b>

    Now, everyone can talk and share suspicions. Citizens should look for slips that reveal the Spy, while the Spy must stay calm, answer carefully, and try to avoid suspicion.

    This is your chance to question, mislead, and decide who you trust.
    .button-finish = 🔍 View results

play-single-device-spy-game-results = { $count ->
    [0]
        🎭 <b>Game Over!</b>

        There were no spies in this game!
        The secret word known to the Citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
    [one]
        🎭 <b>Game Over!</b>

        Player <b>{ $spies }</b> was the Spy!
        The secret word known to the Citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
    *[other]
        🎭 <b>Game Over!</b>

        Players <b>{ $spies }</b> were the spies!
        The secret word known to the Citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
}
    .button-play-again = 🚀 Play again