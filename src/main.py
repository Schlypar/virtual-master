import asyncio
import aiohttp
from dotenv import load_dotenv
import os
from os.path import join, dirname


from game.core.interface import Interface#, InterfaceMock
from game.core.constants import *
from game.core.prompts import *
from game.core.manager import AgentManager
from game.base_agent import new_agent

from game.characters import MCharacter, PCharacter, Stats
from game.scene import Scene, SceneChanger, SceneJudge
from game.game import Game, Plot, Storyteller
from game.director import Director
from game.story import *


async def main():
    async with aiohttp.ClientSession() as session:
        interface = Interface(session)

        bartender = new_agent(
            "bartender",
            BARTENDER,
            BARTENDER_INTENTION,
            BARTENDER_FEELINGS,
            interface
        )

        bartender_character = MCharacter(
            name="Bartender",
            stats=Stats(
                {
                    "Strength": 8,
                    "Dexterity": 10,
                    "Constitution": 12,
                    "Intelligence": 13,
                    "Wisdom": 16,
                    "Charisma": 14
                }
            ),
            background="""
            A man in his late fifties, with a permanent slope to his shoulders as if bearing the weight of every secret he's ever heard. His hair is thinning and grey, his eyes are the color of a winter puddle, and his hands are calloused from a lifetime of cleaning tankards and wiping down tables. He moves with a slow, economical efficiency, never wasting a motion.
            To most, he is a fixture, like a stool or the bar itself. He is polite but distant, his responses limited to grunts, nods, and the occasional, non-committal "Aye." He serves drinks, collects coins, and cleans up the mess. He hears everything but seems to register nothing. Customers project their own thoughts onto his blank slate, assuming he's simple, uninterested, or just too tired to care. This is his greatest defense.
            Now, after thirty years, his mind is a living ledger of the city's soul. He knows:
                Which guards are on the take and who they answer to.
                Which merchants are smuggling what, and in which shipments.
                The secret loves and hatreds that fuel the petty nobility.
                The real story behind last month's "suicide" in the canal.
                The safe routes through the sewers, and which gangs control them.
            """,
            aspects=[],
            agent=bartender,
        )

        traveler = new_agent(
            "traveler",
            TRAVELER,
            TRAVELER_INTENTION,
            TRAVELER_FEELINGS,
            interface
        )

        traveler_character = MCharacter(
            name="Traveler",
            stats=Stats(
                {
                    "Strength": 14,
                    "Dexterity": 16,
                    "Constitution": 13,
                    "Intelligence": 10,
                    "Wisdom": 12,
                    "Charisma": 8
                }
            ),
            background="""
            A man in his early thirties with the weathered look of someone who has spent more nights under stars than a roof. His movements are economical and deliberate, with a predator's awareness of his surroundings. Dark, watchful eyes miss nothing from beneath a fringe of unkempt hair, and a network of faint scars crisscrosses his hands and forearms. He carries himself with the quiet tension of a man who expects trouble at every turn.
            To most, he seems distant and unapproachable. He prefers the corners of rooms, positions with clear sightlines, and never sits with his back to a door. His speech is sparse and functional, his trust earned in miles rather than words. This asocial nature isn't born of malice, but of survival - years spent in the Cave hideout with bandit gang taught him that closeness often ends in betrayal or loss.
            
            The Cave wasn't just a hideout; it was a fortress of desperation. He knows:
                How to move silently through wilderness and read trails that others miss.
                The hidden paths and forgotten game trails that circumvent main roads.
                Where bandits typically lay ambushes and how to spot them hours in advance.
                How to fight dirty and efficiently with knife, cudgel, or bare hands.
                The unspoken codes and signals used by outlaw bands across the region.
                Which innkeepers ask no questions and which magistrates can be bribed.
                People who kidnapped daughter of local burgermeister
            
            Every friendly gesture is measured, every offer of help scrutinized. He helps others not for camaraderie, but because it's the only way he knows to quiet the memories of what he once was.
            """,
            aspects=[],
            agent=traveler,
        )

        player = PCharacter(
            name="Player",
            stats=Stats({
                "Strength": 10,
                 "Dexterity": 12,
                "Constitution": 11,
                "Intelligence": 16,
                "Wisdom": 15,
                "Charisma": 13
            }),
            background="""
            A man in his late thirties, with the weary eyes of someone who has seen too much truth for one lifetime. His clothes, once fine, are now worn but meticulously kept, a ghost of a former station. He moves with a deliberate calm, but his eyes are constantly active, observing, assessing, and filing away every detail in the room. He is here not for drink, but for answers.
            You were once a trusted investigator for the City Watch, known for your sharp mind and unwavering integrity. That was before you dug too deep into the wrong case and found corruption leading to the highest levels of the city guard. Framed for taking a bribe, you were publicly stripped of your badge and thrown into a cell. You escaped, but your name is now mud, and your former colleagues would rather see you silenced permanently than see you prove your innocence.
            The kidnapping of the Burgermeister's daughter is your only chance. Solving it would expose the rot you discovered and clear your name. But you can't operate openly. You need someone who knows the city's underbelly without being part of it
            """,
            aspects=[],
            ai=interface,
        )

        plot = Plot(
            story="",
            scenes=[
                Scene(
                    plot=tavern_scene,
                    player=player,
                    master_characters=[
                        bartender_character, traveler_character
                    ],
                    general_npc=None,
                    director=Director(
                        plot=tavern_scene,
                        ai=interface
                    ),
                    scene_judje=SceneJudge(ai=interface),
                    scene_changer=SceneChanger(plot=tavern_scene, ai=interface)
                )
            ]

        )

        game = Game(
            plot=plot,
            player=player,
            storyteller=Storyteller(ai=interface)
        )

        try:
            await game.runGame()
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    asyncio.run(main())
