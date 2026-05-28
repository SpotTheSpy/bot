play-single-device-spy-game-prepare =
    🤫 <b>Get ready to view your role</b>

    Each player must check their role privately. Only hold the phone when it’s your turn, and make sure no one else can see the screen.

    <b>Player { $player_index }/{ $player_count }</b>
    .button-view-role = 🔍 View role

play-single-device-spy-game-view-role = { $role ->
    [spy]
        🕵️‍♂️ <b>You are the Spy</b>

        Blend in with the citizens and try to guess the secret word. Listen carefully to their answers and ask smart questions to collect clues without raising suspicion.
    *[citizen]
        👨 <b>You are a Citizen</b>

        Your mission is to identify the Spy without revealing the secret word. Ask clever questions and pay attention to answers to spot suspicious behavior.

        Secret word: <b>{ $secret_word }</b>
}
    .button-proceed = 👉 Proceed

play-single-device-spy-game-discuss =
    👀 <b>Discussion time!</b>

    Now, everyone can talk and share suspicions. Citizens should look for slips that reveal the spy, while the spy must stay calm, answer carefully, and try to avoid suspicion.

    This is your chance to question, mislead, and decide who you trust.
    .button-finish = 🔍 View results

play-single-device-spy-game-results = { $count ->
    [0]
        🎭 <b>Game Over!</b>

        There were no spies in this game!
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
    [one]
        🎭 <b>Game Over!</b>

        Player <b>{ $spies }</b> was the spy!
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
    *[other]
        🎭 <b>Game Over!</b>

        Players <b>{ $spies }</b> were the spies!
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to go another round?
}
    .button-play-again = 🚀 Play again

play-single-device-impostor-game-prepare =
    🤫 <b>Get ready to answer your question</b>

    Each player must view and answer their question privately. Only hold the phone when it’s your turn, and make sure no one else can see the screen.

    <b>Player { $player_index }/{ $player_count }</b>
    .button-view-question = 🔍 View question

play-single-device-impostor-game-view-question =
    <b>Your question:</b> { $question }

    You need to answer it by typing in chat. You also dont know yet whether you are an impostor or not - the real question is going to be revealed after everyone gives their answer.

    <b>Your answer:</b> { $answer }
    .empty-answer = <i>Type in chat...</i>
    .button-proceed = 👉 Proceed

play-single-device-impostor-game-discuss =
    👀 <b>Time to view the answers!</b>

    You may now reveal every player answers one by one, and present them to the group.

    Then, once every answer is revealed - discuss, talk and share suspicions. Citizens should look for slips and inconsistencies that reveal the impostor, while the impostor must stay calm, answer carefully, and try to avoid suspicion.

    <b>The real question was:</b> { $question }

    { $answers }
    .answer = <i>Player { $player_index }:</i> <b>{ $answer }</b>
    .answer-empty = ...
    .button-next-answer = ➡️ Next answer
    .button-finish = 🔍 View results

play-single-device-impostor-game-results = { $count ->
    [0]
        🎭 <b>Game Over!</b>

        There were no impostors in this game!

        <b>The question was:</b> { $real_question }

        Thanks for playing! Want to go another round?
    [one]
        🎭 <b>Game Over!</b>

        Player <b>{ $impostors }</b> was the impostor!

        <b>The real question was:</b> { $real_question }
        <b>The question impostor had was:</b> { $impostor_question }

        Thanks for playing! Want to go another round?
    *[other]
        🎭 <b>Game Over!</b>

        Players <b>{ $impostors }</b> were the impostors!

        <b>The real question was:</b> { $real_question }
        <b>The question impostor had was:</b> { $impostor_question }

        Thanks for playing! Want to go another round?
}
    .button-play-again = 🚀 Play again