setup-spy-game = Setup
    .button-player-count = Player count: { $player_count }
    .button-category = Category: { $category }
    .button-spy-count = Spy count: { $spy_count }
    .button-play = Play

setup-spy-game-player-count = Setup player count
    .button = { $selected ->
        [true] + { $player_count }
       *[false] { $player_count }
    }

setup-spy-game-category = Setup category
    .button = { $selected ->
        [true] + { $category }
       *[false] { $category }
    }

setup-spy-game-spy-count = Setup spy count
    .button = { $selected ->
        [true] + { $spy_count }
       *[false] { $spy_count }
    }