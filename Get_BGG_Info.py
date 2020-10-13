# coding: utf-8

# Caching
# OK: Move cache files to cache sub folder
# OK: Add possibility to choose if cache should be used
# TODO: Cache browse pages
#
# Attributes:
# OK: Add link to game, (NO: remove ID and title URL)
# OK: Resolve "2, " number of players issue
# TODO: Move attribute queries into separate functions
# OK: add game weight
# OK: Add price
# TODO: write to json file (for later analysis)
# TODO: add variable here for number of games
# TODO: add info about needed Google Drive secret file


def main():
    import boardgamegeek

    # Create instance of the BGG class,
    # with the top number of games to be processed
    bgg = boardgamegeek.BGG(1000)

    # Get games and attribute info from browse pages
    l_d_games_browse_pages = bgg.scrape_browse_pages()

    # Get games with additional info from games pages
    l_d_games_games_pages = bgg.get_info_per_game(l_d_games_browse_pages, use_cache=False)

    # Write list of games to Google Sheet
    bgg.bgg2gsheets(l_d_games_games_pages)

    # Write list of games to json file
    #bgg.bgg@json(l_d_games_games_pages)


if __name__ == "__main__":
    import sys

    # Run main function
    sys.exit(main())
