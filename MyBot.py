#!/usr/bin/python
"""
Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging


def ship_status():
        logging.info("\n\nShip " + str(ship.id)
                     + "\n" + "    health: " + str(ship.health)
                     + "\n" + "    " + str(ship.docking_status)
                     + "\n" + "    planet: " + str(ship.planet)
                     + "\n\n")

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("loopcore")
# Then we print our start message to the logs
logging.info("Starting loopcore bot!")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            ship_status()
            continue

        # Sort planets by distance, unsure how to use it though
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        nearest_planet = None
        for distance in sorted(entities_by_distance):
            nearest_planet = next((nearest_entity for nearest_entity in entities_by_distance[distance] if
                                   isinstance(nearest_entity, hlt.entity.Planet)), None)
            if nearest_planet:
                break

        # For each planet in the game (only non-destroyed planets are included)
        # Change this to each planet in the list of nearest planets
        for planet in game_map.all_planets():
            # If the planet is owned
            if planet.is_owned():
                # Skip this planet
                # We should attack the planet or the ships around the planet at some point

                continue

            # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
            else:
                # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
                # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
                # We run this navigate command each turn until we arrive to get the latest move.
                # Here we move at half our maximum speed to better control the ships
                # In order to execute faster we also choose to ignore ship collision calculations during navigation.
                # This will mean that you have a higher probability of crashing into ships, but it also means you will
                # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
                # wish to turn that option off.
                navigate_command = ship.navigate(
                    ship.closest_point_to(planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED/1.5),
                    ignore_ships=True)

                # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
                # or we are trapped (or we reached our destination!), navigate_command will return null;
                # don't fret though, we can run the command again the next turn)
                if navigate_command:
                    command_queue.append(navigate_command)
            break

        ship_status()
    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    logging.info("--"*50)
    # TURN END
# GAME END
