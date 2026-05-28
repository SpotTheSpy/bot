play-single-device-spy-game-prepare =
    🤫 <b>Get ready to view your role</b>

    Each player should check their role privately. Hold the phone only when it’s your turn, and make sure no one else can see the screen.

    <b>Player { $player_index }/{ $player_count }</b>
    .button-view-role = 🔍 View role

play-single-device-spy-game-view-role = { $role ->
    [spy]
        🕵️ <b>You are the Spy</b>

        Blend in with the citizens and try to guess the secret word. Listen carefully to their answers and ask smart questions to gather clues without raising suspicion.
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

        There were no spies in this game.
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to play another round?
    [one]
        🎭 <b>Game Over!</b>

        Player <b>{ $spies }</b> was the spy.
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to play another round?
    *[other]
        🎭 <b>Game Over!</b>

        Players <b>{ $spies }</b> were the spies.
        The secret word known to the citizens was: <b>{ $secret_word }</b>.

        Thanks for playing! Want to play another round?
}
    .button-play-again = 🚀 Play again

play-single-device-impostor-game-prepare =
    🤫 <b>Get ready to answer your question</b>

    Each player will receive a question and must answer it privately. Only hold the phone when it’s your turn, and make sure no one else can see the screen.

    <b>Player { $player_index }/{ $player_count }</b>
    .button-view-question = 🔍 View question

play-single-device-impostor-game-view-question =
    <b>Your question:</b> { $question }

    Answer it by typing in the chat. At this stage, you don’t know whether your question is the real one or the impostor version - everything will be revealed after all players submit their answers.

    <b>Your answer:</b> { $answer }
    .empty-answer = <i>Type your answer...</i>
    .button-proceed = 👉 Proceed

play-single-device-impostor-game-discuss =
    👀 <b>Time to reveal the answers!</b>

    Reveal each player’s answer one by one and present them to the group.

    After all answers are shown, discuss them together. Look for inconsistencies, unusual wording, or anything that feels out of place. Try to determine who received a different question based on their answer and your knowledge of the players.

    <b>The real question was:</b> { $question }

    { $answers }
    .answer = <i>Player { $player_index }:</i> <b>{ $answer }</b>
    .answer-empty = ...
    .button-next-answer = ➡️ Next answer
    .button-finish = 🔍 View results

play-single-device-impostor-game-results = { $count ->
    [0]
        🎭 <b>Game Over!</b>

        There were no impostors in this game.

        <b>The question was:</b> { $real_question }

        Thanks for playing! Want to play another round?

    [one]
        🎭 <b>Game Over!</b>

        Player <b>{ $impostors }</b> was an impostor!

        <b>The real question was:</b> { $real_question }
        <b>The impostor's question was:</b> { $impostor_question }

        Thanks for playing! Want to play another round?

    *[other]
        🎭 <b>Game Over!</b>

        Players <b>{ $impostors }</b> were impostors!

        <b>The real question was:</b> { $real_question }
        <b>The impostors' questions were:</b> { $impostor_question }

        Thanks for playing! Want to play another round?
}
    .button-play-again = 🚀 Play again
