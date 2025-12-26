from scrape import get_all_seasons

def main():
    all_seasons_data = get_all_seasons()
    # all_seasons_data is a tuple containing:
    # (squads_stats, squads_wages, standard_stats, defensive_stats, passing_stats, shooting_stats, goalkeeping_stats)

if __name__ == "__main__":
    main()