setup-spy-game =
    ⚙️ <b>Game setup</b>

    Use the options below to configure your game before starting.

    You can choose the number of players, select a secret word category, and decide how many spies will be in the game. Make sure everyone agrees on the setup before continuing.
    .button-player-count = Players: { $player_count } 👤
    .button-category = Category: { $category }
    .button-spy-count = Spies: { $spy_count }
    .button-play = 🚀 Play

setup-spy-game-player-count =
    👤 <b>Choose player count</b>

    Choose how many players will participate on this device. The phone will be passed around so each player can privately check their role before the game begins.
    .button = { $selected ->
        [true] ✅ { $player_count } 👤
        *[false] { $player_count } 👤
    }

setup-spy-game-category =
    🎨 <b>Choose secret word category</b>

    Select the theme for your game’s secret words. Different categories change how challenging or funny each round can be, so pick one that suits your group best.
    .button = { $selected ->
        [true] ✅ { $category }
        *[false] { $category }
    }

setup-spy-game-spy-count =
    🕵️ <b>Choose number of spies</b>

    Choose how many spies will be hiding among the citizens. More spies add more chaos to the game, and if you choose a random number of spies, the game can get completely crazy. Balance wisely for the best experience.
    .button = { $selected ->
        [true] ✅ { $spy_count }
        *[false] { $spy_count }
    }

setup-impostor-game =
    ⚙️ <b>Game setup</b>

    Use the options below to configure your game before starting.

    You can choose the total number of players and select how many impostors will be in the game. Make sure everyone agrees on the setup before continuing.
    .button-player-count = Players: { $player_count } 👤
    .button-impostor-count = Impostors: { $impostor_count }
    .button-play = 🚀 Play

setup-impostor-game-player-count =
    👤 <b>Choose player count</b>

    Choose how many players will participate on this device. The phone will be passed around so each player can privately answer their question before the game begins.
    .button = { $selected ->
        [true] ✅ { $player_count } 👤
        *[false] { $player_count } 👤
    }

setup-impostor-game-impostor-count =
    🎭 <b>Choose number of impostors</b>

    Select how many impostors will be hiding among the citizens. More impostors add more chaos to the game, and if you choose a random number of impostors, the game can get completely crazy. Balance wisely for the best experience.
    .button = { $selected ->
        [true] ✅ { $impostor_count }
        *[false] { $impostor_count }
    }
