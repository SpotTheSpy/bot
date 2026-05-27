setup-spy-game =
    ⚙️ <b>Game setup</b>

    Use the options below to configure your game before starting. You can set the total number of players, choose the secret word category, and decide how many Spies will be in the game. Make sure everyone agrees on the setup before continuing.
    .button-player-count = Players: { $player_count } 👤
    .button-category = Category: { $category }
    .button-spy-count = Spies: { $spy_count }
    .button-play = 🚀 Play

setup-spy-game-player-count =
    ⚙️ <b>Set player count</b>

    Choose how many players will participate on this device. The phone will be passed around so each player can privately check their role before the game begins.
    .button = { $selected ->
        [true] ✅ { $player_count } 👤
        *[false] { $player_count } 👤
    }

setup-spy-game-category =
    ⚙️ <b>Choose secret word category</b>

    Select the theme for your game’s secret words. Different categorie change how challenging or funny each round can be, so pick one tha suits your group best.
    .button = { $selected ->
        [true] ✅ { $category }
        *[false] { $category }
    }

setup-spy-game-spy-count =
    ⚙️ <b>Set number of Spies</b>

    Choose how many Spies will be hiding among the Citizens. More spies add more chaos to the game, and if you pick random count - the game can get completely crazy. Balance wisely for the best experience.
    .button = { $selected ->
        [true] ✅ { $spy_count }
        *[false] { $spy_count }
    }