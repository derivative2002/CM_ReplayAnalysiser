"""
Main module for parsing data from Co-op replays

It's a bit messy, and there are many tweaks done to get good data from replays.
I shouldn't have differentiated between "main" and "ally" player here, perhaps only mark him on the end.

"""
import time
import traceback

from SCOFunctions.MLogging import Logger
from SCOFunctions.S2Parser import s2_parse_replay
from SCOFunctions.SC2Dictionaries import (COMasteryUpgrades, HFTS_Units, TUS_Units, UnitAddKillsTo, UnitCompDict, UnitNameDict, UnitsInWaves,
                                          amon_player_ids, prestige_upgrades)
from SCOFunctions.StatsCounter import DroneIdentifier, StatsCounter

do_not_count_kills = {'FuelCellPickupUnit', 'ForceField', 'Scarab'}
duplicating_units = {'HotSRaptor', 'MutatorAmonArtanis', 'HellbatBlackOps', 'LurkerStetmannBurrowed'}
skip_strings = ('placement', 'placeholder', 'dummy', 'cocoon', 'droppod', "colonist hut", "bio-dome", "amon's train", "warp conduit")
revival_types = {
    'KerriganReviveCocoon': 'K5Kerrigan',
    'AlarakReviveBeacon': 'AlarakCoop',
    'ZagaraReviveCocoon': 'ZagaraVoidCoop',
    'DehakaCoopReviveCocoonFootPrint': 'DehakaCoop',
    'NovaReviveBeacon': 'NovaCoop',
    'ZeratulCoopReviveBeacon': 'ZeratulCoop'
}
icon_units = {'MULE', 'Omega Worm', 'Infested Bunker', 'Mecha Infestor', 'Unbound Fanatic'}
dont_count_morphs = {'SCVMengsk', 'TrooperMengsk', 'HellionTank', 'Hellion'}  # Don't count as unit created for these when the unit switches type
self_killing_units = {'FenixCoop', 'FenixDragoon', 'FenixArbiter'}
dont_show_created_lost = {
    "Stetmann's Top Bar", "Zeratul's Top Bar", "Vorazun's Top Bar", "Fenix's Top Bar", "Zagara's Top Bar", "Tychus' Top Bar", "Swann's Top Bar",
    "Stukov's Top Bar", "Raynor's Top Bar", "Nova's Top Bar", "Mengsk's Top Bar", "Kerrigan's Top Bar", "Karax's Top Bar", "Han and Horner's Top Bar",
    "Dehaka's Top Bar", "Artanis' Top Bar", "Abathur's Top Bar", 'Photon Overcharge', 'Super Gary', 'Gary', 'Tychus Findlay', "James 'Sirius' Sykes",
    "Kev 'Rattlesnake' West", 'Nux', 'Crooked Sam', 'Lt. Layna Nikara', "Miles 'Blaze' Lewis", "Rob 'Cannonball' Boswell", "Vega"
}
aoe_units = {'Raven', 'ScienceVessel', 'Viper', 'HybridDominator', 'Infestor', 'HighTemplar', 'Blightbringer', 'TitanMechAssault', 'MutatorAmonNova'}
tychus_outlaws = {
    'TychusCoop',
    'TychusReaper',
    'TychusWarhound',
    'TychusMarauder',
    'TychusHERC',
    'TychusFirebat',
    'TychusGhost',
    'TychusSpectre',
    'TychusMedic',
}
commander_upgrades = {
    "AlarakCommander": "Alarak",
    "ArtanisCommander": "Artanis",
    "FenixCommander": "Fenix",
    "KaraxCommander": "Karax",
    "VorazunCommander": "Vorazun",
    "ZeratulCommander": "Zeratul",
    "HornerCommander": "Han & Horner",
    "MengskCommander": "Mengsk",
    "NovaCommander": "Nova",
    "RaynorCommander": "Raynor",
    "SwannCommander": "Swann",
    "TychusCommander": "Tychus",
    "AbathurCommander": "Abathur",
    "DehakaCommander": "Dehaka",
    "KerriganCommander": "Kerrigan",
    "StukovCommander": "Stukov",
    "ZagaraCommander": "Zagara",
    "StetmannCommander": "Stetmann"
}
commander_no_units = {
    'Nova': ['CoopCasterNova'],
    "Han & Horner": ['HHMagneticMine'],
    "Karax": ["SoACasterKarax"],
    "Artanis": ["SoACasterArtanis"],
    "Mengsk": ["ArtilleryMengsk", "GhostMengsk"]
}
commander_no_units_values = {unit for commander in commander_no_units for unit in commander_no_units[commander]}

units_killed_in_morph = {'HydraliskLurker', 'MutaliskBroodlord', 'RoachVile', 'Mutalisk', 'Devourer', 'GuardianMP', 'Viper', 'SwarmHost', 'Queen'}
primal_combat_predecessors = {
    'DehakaRavasaur': 'DehakaZerglingLevel2',
    'DehakaRoachLevel3': 'DehakaRoachLevel2',
    'DehakaGuardianFightMorph': 'DehakaRoachLevel2',
    'ImpalerDehaka': 'DehakaHydraliskLevel2',
    'DehakaMutaliskLevel3FightMorph': 'DehakaHydraliskLevel2',
    'DehakaPrimalSwarmHost': 'DehakaSwarmHost',
    'DehakaUltraliskLevel3': 'DehakaUltraliskLevel2'
}
dont_include_units = {
    "SuperWarpGate", "VoidRiftUnselectable", "UnbuildableRocksUnit", "TrooperMengskWeaponAAPickup", "TrooperMengskWeaponFlamethrowerPickup",
    "TrooperMengskWeaponImprovedPickup", "PsiDisintegratorPowerLink", "ProtossDockingBayUnit", "PnPHybridVoidRift", "PlatformConnector",
    "MutatorAmonKaraxInvisiblePylon", "KorhalGateControl", "HybridStasisChamberA", "HybridHoldingCellSmallUnit", "HybridHoldingCellUnit",
    "GateControlUnit", "Food1000", "COOPTerrazineTank", "ExpeditionJumpGate", "EnemyPathingBlocker4x4", "InvisibleEscortFlying",
    "DestructibleUmojanLabTestTube", 'AmonHostDeathBeamUnit', 'DamagedMutatorLaserDrill'
}
salvage_units = {
    "PerditionTurretUnderground", "PerditionTurret", "ArtilleryMengsk", "Bunker", "FlamingBetty", "KelMorianGrenadeTurret", "KelMorianMissileTurret",
    "NovaACLaserTurret", "TychusSCVAutoTurret", "BunkerDepotMengsk"
}
UnitAddLossesTo = {
    'TorrasqueChrysalis': 'Ultralisk',
    'SiegeTankWreckage': 'Siege Tank',
    'ThorWreckageSwann': 'Thor',
    'ThorWreckage': 'Thor',
    'DehakaMutaliskReviveEgg': 'Primal Mutalisk'
}

logger = Logger('REPA', Logger.levels.INFO)


def contains_skip_strings(pname):
    """ Checks if any of skip strings is in the pname """
    lowered_name = pname.lower()
    return any(item in lowered_name for item in skip_strings)


def upgrade_is_in_mastery_upgrades(upgrade):
    """ Checks if the upgrade is in mastery upgrades, if yes, returns the Commnader and upgrade index"""
    for co in COMasteryUpgrades:
        if upgrade in COMasteryUpgrades[co]:
            return co, COMasteryUpgrades[co].index(upgrade)
    return False, 0


def prestige_talent_name(upgrade):
    """ Checks if the upgrade is in prestige upgrades. If yes, returns Prestige name"""

    for co in prestige_upgrades:
        if upgrade in prestige_upgrades[co]:
            return prestige_upgrades[co][upgrade]
    return None


def switch_names(pdict):
    """ Changes names to that in unit dictionary, sums duplicates"""
    temp_dict = {}

    for key in pdict:
        added = False
        if key in dont_include_units:
            continue

        # For locusts, broodlings, interceptors, add kills to the main unit. Don't add unit created/lost
        if key in UnitAddKillsTo:
            name = UnitAddKillsTo[key]
            added = True
            if name in temp_dict:
                temp_dict[name][2] += pdict[key][2]
            else:
                temp_dict[name] = [0, 0, pdict[key][2], 0]

        # For wreckages, cocoon
        if key in UnitAddLossesTo:
            name = UnitAddLossesTo[key]
            added = True
            if name in temp_dict:
                temp_dict[name][1] += pdict[key][1]
            else:
                temp_dict[name] = [0, pdict[key][1], 0, 0]

        if not added:
            # Translate names & sum up those with the same names
            name = UnitNameDict.get(key, key)
            if name in temp_dict:
                for a in range(len(temp_dict[name])):
                    temp_dict[name][a] += pdict[key][a]
            else:
                temp_dict[name] = list()
                for a in range(len(pdict[key])):
                    temp_dict[name].append(pdict[key][a])

    return temp_dict


def get_enemy_comp(identified_waves):
    """ Takes indentified waves and tries to match them with known enemy AI comps.
        Waves are identified as events where 6+ units were created at the same second. """

    # Each AI gets points for each matching wave
    results = dict()
    for AI in UnitCompDict:
        results[AI] = 0

    # Lets go through our waves, compare them to known AI unit waves
    for iden_wave in identified_waves:
        types = set(identified_waves[iden_wave])
        if len(types) == 0:
            continue

        logger.debug(f'{"-"*40}\nChecking this wave type: {types}\n')
        for AI in UnitCompDict:
            for idx, wave in enumerate(UnitCompDict[AI]):
                # Don't include Medivac, it's removed from wave units as well
                wave.difference_update({'Medivac'})

                # Identical wave
                if types == wave:
                    logger.debug(f'"{AI}" wave {idx+1} is the same: {wave}')
                    results[AI] += 1 * len(wave)
                    continue

                # In case of alternate units or some noise
                if types.issubset(wave) and len(wave) - len(types) == 1:
                    logger.debug(f'"{AI}" wave {idx+1} is a close subset: {types} | {wave}')
                    results[AI] += 0.25 * len(wave)

    results = {k: v for k, v in sorted(results.items(), key=lambda x: x[1], reverse=True) if v != 0}
    logger.debug(f'{"-"*40}\nAnd results are: {results}')

    # Return the comp with the most points
    if len(results) > 0:
        logger.debug(f'Most likely AI: "{list(results.keys())[0]}" with {100*list(results.values())[0]/sum(results.values()):.1f}% points\n\n')
        return list(results.keys())[0]
    return 'Unidentified AI'


def unitid(event, killer=False, creator=False):
    """ Returns and unique integer as unit id.
    `killer`=True for killer unique id, otherwise normal unit.
    Assuming index is less than 100000 (usually it's < 1000)
     """
    try:
        if killer:
            index = event['m_killerUnitTagIndex']
            recycleindex = event['m_killerUnitTagRecycle']
        elif creator:
            index = event['m_creatorUnitTagIndex']
            recycleindex = event['m_creatorUnitTagRecycle']
        else:
            index = event['m_unitTagIndex']
            recycleindex = event['m_unitTagRecycle']

        if index is None or recycleindex is None:
            return None

        return recycleindex * 100000 + index
    except Exception:
        return None


def parse_replay_file(filepath):
    """ Parses a replay with S2parser"""
    replay = None
    for attempt in range(3):
        try:
            replay = s2_parse_replay(filepath, return_events=True)
            break
        except Exception:  # You can get an error here if SC2 didn't finish writing into the file. Very rare.
            if attempt == 2:
                raise Exception(f'Parsing error! ({filepath})')
            time.sleep(0.3)

    return replay


def analyse_parsed_replay(filepath, replay, main_player_handles=None, print_killby: bool = True):
    """
    This whole function is a bit messy. It originated in a very different form.
    I should be broken into more functions. Players shouldn't be hardcoded to
    "main" and "ally" but instead a single datastructure. Which player shows on
    top should be decided in javascript and not here.

    """

    if replay is None:
        return {}

    # Data structure is {unitType : [#created, #died, #kills, #killfraction]}
    unit_type_dict_main = {}
    unit_type_dict_ally = {}
    unit_type_dict_amon = {}

    # Find Amon players
    amon_players = set()
    amon_players.add(3)
    amon_players.add(4)

    # Add a list of amon players written for each map
    for m in amon_player_ids:
        if m in replay['map_name'] or ('[MM] Lnl' in replay['map_name'] and m == 'Lock & Load'):
            amon_players = amon_players.union(amon_player_ids[m])
            break

    # Find player names and numbers
    main_player = 1
    main_player_found = False

    if main_player_handles is not None and len(main_player_handles) > 0:  # Check if you can find the main player
        for player in replay['players']:
            if player['pid'] in {1, 2} and not main_player_found and player.get('handle') in main_player_handles:
                main_player = player['pid']
                main_player_found = True
                break

    # Ally
    ally_player = 1 if main_player == 2 else 2

    # Start saving data
    replay_report_dict = dict()
    replay_report_dict['file'] = filepath
    replay_report_dict['replaydata'] = True
    replay_report_dict['map_name'] = replay['map_name']
    replay_report_dict['extension'] = replay['extension']
    replay_report_dict['B+'] = replay['brutal_plus']
    replay_report_dict['result'] = replay['result']
    replay_report_dict['main'] = replay['players'][main_player].get('name', 'None')
    replay_report_dict['ally'] = replay['players'][ally_player].get('name', 'None')
    replay_report_dict['mainAPM'] = replay['players'][main_player].get('apm', 0)
    replay_report_dict['allyAPM'] = replay['players'][ally_player].get('apm', 0)
    replay_report_dict['positions'] = {'main': main_player, 'ally': ally_player}
    replay_report_dict['mainIcons'] = dict()
    replay_report_dict['allyIcons'] = dict()

    # Difficulty
    diff_1 = replay['difficulty'][0]
    diff_2 = replay['difficulty'][1]
    if diff_1 == diff_2:
        replay_report_dict['difficulty'] = diff_1
    elif main_player == 1:
        replay_report_dict['difficulty'] = f'{diff_1}/{diff_2}'
    else:
        replay_report_dict['difficulty'] = f'{diff_2}/{diff_1}'

    logger.debug(f'Report dict: {replay_report_dict}')

    # Events
    unit_dict = {}  # Data structure is {unit_id : [UnitType, Owner]}; used to track all units
    DT_HT_Ignore = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0]  # Ignore certain amount of DT/HT deaths after archon is initialized. DT_HT_Ignore[player]
    killcounts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    START_TIME = replay['start_time']
    END_TIME = replay['end_time']
    commander_fallback = dict()
    outlaw_order = []
    wave_units = {'second': 0, 'units': []}
    identified_waves = dict()
    mastery_fallback = {1: [0, 0, 0, 0, 0, 0], 2: [0, 0, 0, 0, 0, 0]}
    killbot_feed = [0, 0, 0]
    custom_kill_count = dict()
    UsedMutatorSpiderMines = set()
    PrestigeTalents = [None, None, None]
    bonus_timings = list()
    ResearchVesselLandedTiming = None
    LastBiomassPosition = [0, 0, 0]
    AbathurKillLocusts = set()
    MutatorDehakaDragUnitIDs = set()
    MWBonusInitialTiming = [0, 0]
    murvar_spawns = set()
    glevig_spawns = set()
    broodlord_broodlings = set()
    user_leave_times = dict()
    mind_controlled_units = set()
    zagaras_dummy_zerglings = set()
    unit_killed_by = dict()
    ally_kills_counted_toward_main = 0  # Number of kills counted from ally toward main because the ally left
    VespeneDroneIdentifier = DroneIdentifier(replay['players'][main_player].get('commander', None),
                                             replay['players'][ally_player].get('commander', None))
    mainStatsCounter = StatsCounter(masteries=replay['players'][main_player].get('masteries', (0, 0, 0, 0, 0, 0)),
                                    filepath=filepath,
                                    unit_dict=unit_type_dict_main,
                                    commander=replay['players'][main_player].get('commander', None),
                                    drone_counter=VespeneDroneIdentifier)
    allyStatsCounter = StatsCounter(masteries=replay['players'][ally_player].get('masteries', (0, 0, 0, 0, 0, 0)),
                                    filepath=filepath,
                                    unit_dict=unit_type_dict_ally,
                                    commander=replay['players'][ally_player].get('commander', ''),
                                    drone_counter=VespeneDroneIdentifier)

    def is_broodlord_broodling(unit_type, unit_id):
        return unit_type in {'Broodling', 'BroodlingStetmann'} and unit_id in broodlord_broodlings

    if '[MM]' in filepath:
        mainStatsCounter.enable_updates = True
        allyStatsCounter.enable_updates = True

    last_aoe_unit_killed = [0] * 17
    for player in range(1, 16):
        last_aoe_unit_killed[player] = [None, 0] if player in amon_players else None

    for event in replay['events']:
        # Save when user leaves
        if event['_event'] == 'NNet.Game.SGameUserLeaveEvent':
            user = event['_userid']['m_userId'] + 1
            user_leave_times[user] = event['_gameloop'] / 16

        # Skip events after the game ended
        if event['_gameloop'] / 16 > END_TIME:
            continue

        # Counting vespene drones
        VespeneDroneIdentifier.event(event)

        # Save player stats for graphs
        if event['_event'] == 'NNet.Replay.Tracker.SPlayerStatsEvent':
            player = event['m_playerId']

            if player == main_player:
                mainStatsCounter.add_stats(kills=killcounts[player],
                                           supply_used=event['m_stats']['m_scoreValueFoodUsed'] / 4096,
                                           collection_rate=sum((event['m_stats']['m_scoreValueMineralsCollectionRate'],
                                                                event['m_stats']['m_scoreValueVespeneCollectionRate'])))

            elif player == ally_player:
                allyStatsCounter.add_stats(kills=killcounts[player],
                                           supply_used=event['m_stats']['m_scoreValueFoodUsed'] / 4096,
                                           collection_rate=sum((event['m_stats']['m_scoreValueMineralsCollectionRate'],
                                                                event['m_stats']['m_scoreValueVespeneCollectionRate'])))

        if event['_event'] == 'NNet.Replay.Tracker.SUpgradeEvent' and event['m_playerId'] in [1, 2]:
            _upg_name = event['m_upgradeTypeName'].decode()
            _upg_pid = event['m_playerId']

            # Tychus upgrades for army value
            if _upg_pid == main_player:
                mainStatsCounter.upgrade_event(_upg_name)
            elif _upg_pid == ally_player:
                allyStatsCounter.upgrade_event(_upg_name)

            # Commander fallback (used for arcade maps)
            if _upg_name in commander_upgrades:
                commander_fallback[_upg_pid] = commander_upgrades[_upg_name]
                VespeneDroneIdentifier.update_commanders(_upg_pid, commander_upgrades[_upg_name])
                if _upg_pid == main_player:
                    mainStatsCounter.update_commander(commander_upgrades[_upg_name])
                elif _upg_pid == ally_player:
                    allyStatsCounter.update_commander(commander_upgrades[_upg_name])

            # Mastery upgrade fallback (used for arcade maps)
            mas_commander, mas_index = upgrade_is_in_mastery_upgrades(_upg_name)
            if mas_commander:
                logger.debug(f'Player {_upg_pid} (com: {mas_commander}) got upgrade {_upg_name} (idx: {mas_index}) (count: {event["m_count"]})')
                mastery_fallback[_upg_pid][mas_index] = event['m_count']

                if _upg_pid == main_player:
                    mainStatsCounter.update_mastery(mas_index, event['m_count'])
                elif _upg_pid == ally_player:
                    allyStatsCounter.update_mastery(mas_index, event['m_count'])

            # Prestige talents
            _prestige = prestige_talent_name(_upg_name)
            if _prestige is not None:
                PrestigeTalents[_upg_pid] = _prestige

                if _upg_pid == main_player:
                    mainStatsCounter.update_prestige(_prestige)
                elif _upg_pid == ally_player:
                    allyStatsCounter.update_prestige(_prestige)

        if event['_event'] in ('NNet.Replay.Tracker.SUnitBornEvent', 'NNet.Replay.Tracker.SUnitInitEvent'):
            _unit_type = event['m_unitTypeName'].decode()
            _ability_name = event.get('m_creatorAbilityName', None)
            _ability_name = _ability_name.decode() if _ability_name is not None else None
            unit_id = unitid(event)
            _control_pid = event['m_controlPlayerId']
            unit_dict[unit_id] = [_unit_type, _control_pid]

            # Track Murvar's spawns
            if _unit_type in {'DehakaLocust', 'DehakaCreeperFlying', 'DehakaLocustFlying', 'DehakaCreeper'}:
                if event['m_creatorAbilityName'] is not None and event['m_creatorAbilityName'].decode() == 'CoopMurvarSpawnCreepers':
                    murvar_spawns.add(unit_id)

            # Track Glevig's spawns
            if _unit_type in {'CoopDehakaGlevigEggZergling', 'CoopDehakaGlevigEggRoach', 'CoopDehakaGlevigEggHydralisk'}:
                glevig_spawns.add(unit_id)

            # Kerrigan's and Stetmann's Broodlings
            if _unit_type in {'Broodling', 'BroodlingStetmann'} and unitid(event, creator=True) is not None:
                creator = unit_dict[unitid(event, creator=True)][0]
                if creator in {'BroodlingEscort', 'BroodlingEscortStetmann'}:
                    broodlord_broodlings.add(unit_id)

            # Certain hero units don't die, instead lets track their revival beacons/cocoons. Let's assume they will finish reviving.
            if _unit_type in revival_types and _control_pid in [1, 2] and event['_gameloop'] / 16 > START_TIME + 1:
                if _control_pid == main_player:
                    unit_type_dict_main[revival_types[_unit_type]][1] += 1
                    unit_type_dict_main[revival_types[_unit_type]][0] += 1
                if _control_pid == ally_player:
                    unit_type_dict_ally[revival_types[_unit_type]][1] += 1
                    unit_type_dict_ally[revival_types[_unit_type]][0] += 1

            # Primal combat fix. For every morph we are substracting two losses from the base unit type
            if _unit_type in primal_combat_predecessors:
                logger.debug(f'{_unit_type} substracting from {primal_combat_predecessors[_unit_type]}\n')
                if main_player == _control_pid:
                    unit_type_dict_main[primal_combat_predecessors[_unit_type]][1] -= 2
                if ally_player == _control_pid:
                    unit_type_dict_ally[primal_combat_predecessors[_unit_type]][1] -= 2

            if not (unit_id in glevig_spawns or unit_id in murvar_spawns or is_broodlord_broodling(_unit_type, unit_id)):
                # Save stats for units created
                if main_player == _control_pid:
                    mainStatsCounter.unit_created_event(_unit_type, event)
                    if _unit_type in unit_type_dict_main:
                        unit_type_dict_main[_unit_type][0] += 1
                    else:
                        unit_type_dict_main[_unit_type] = [1, 0, 0, 0]

                elif ally_player == _control_pid:
                    allyStatsCounter.unit_created_event(_unit_type, event)
                    if _unit_type in unit_type_dict_ally:
                        unit_type_dict_ally[_unit_type][0] += 1
                    else:
                        unit_type_dict_ally[_unit_type] = [1, 0, 0, 0]

                elif _control_pid in amon_players:
                    if _ability_name == 'MutatorAmonDehakaDrag':
                        MutatorDehakaDragUnitIDs.add(unitid(event))
                    elif _unit_type in unit_type_dict_amon:
                        unit_type_dict_amon[_unit_type][0] += 1
                    else:
                        unit_type_dict_amon[_unit_type] = [1, 0, 0, 0]

            # Outlaw order
            if _unit_type in tychus_outlaws and _control_pid in [1, 2] and not (_unit_type in outlaw_order):
                outlaw_order.append(_unit_type)

            # Identifying waves
            if _control_pid in [3, 4, 5, 6] and event['_gameloop'] / 16 > START_TIME + 60 and _unit_type in UnitsInWaves:
                if wave_units['second'] == event['_gameloop'] / 16:
                    wave_units['units'].append(_unit_type)
                else:
                    wave_units['second'] = event['_gameloop'] / 16
                    wave_units['units'] = [_unit_type]

                if len(wave_units['units']) > 5:
                    identified_waves[event['_gameloop'] / 16] = wave_units['units']

            # Abathur biomass for identifying locust
            if _unit_type == 'BiomassPickup':
                LastBiomassPosition = [event['m_x'], event['m_y'], event['_gameloop']]

            if _unit_type == 'Locust' and [event['m_x'], event['m_y'], event['_gameloop']] == LastBiomassPosition:
                AbathurKillLocusts.add(unitid(event))

        # In future ignore some Dark/High Templar deaths caused by Archon merge
        if event['_event'] == 'NNet.Replay.Tracker.SUnitInitEvent' and event['m_unitTypeName'].decode() == "Archon":
            DT_HT_Ignore[event['m_controlPlayerId']] += 2

        if event['_event'] == 'NNet.Replay.Tracker.SUnitTypeChangeEvent' and unitid(event) in unit_dict:
            _old_unit_type = unit_dict[unitid(event)][0]
            _control_pid = unit_dict[unitid(event)][1]
            _unit_type = event['m_unitTypeName'].decode()

            # Void Launch bonus objective. If it lands and soon-ish after takes off, the bonus is complete.
            if _control_pid == 7 and _unit_type == 'ResearchVesselLanded':
                ResearchVesselLandedTiming = event['_gameloop']

            if _control_pid == 7 and _unit_type == 'ResearchVessel' and ResearchVesselLandedTiming is not None and (ResearchVesselLandedTiming + 1500
                                                                                                                    > event['_gameloop']):
                bonus_timings.append(event['_gameloop'] / 16 - START_TIME)
                ResearchVesselLandedTiming = None

            # Scythe of Amon bonus objective. If it changes to WarpPrismPhasing, the bonus is completed.
            if 'Scythe of Amon' in replay['map_name'] and _control_pid == 11 and _unit_type == 'WarpPrismPhasing':
                bonus_timings.append(event['_gameloop'] / 16 - START_TIME)

            # Strange. Some units morph to egg, then the morph is created, then the egg morphs back and the unit is killed
            if _unit_type in units_killed_in_morph:
                continue

            # Update unit_dict
            unit_dict[unitid(event)][0] = _unit_type

            if main_player == _control_pid:
                mainStatsCounter.unit_change_event(_unit_type, _old_unit_type)
            elif ally_player == _control_pid:
                allyStatsCounter.unit_change_event(_unit_type, _old_unit_type)

            # Add to created units
            if _unit_type in UnitNameDict and _old_unit_type in UnitNameDict:

                # When banelings finish morph for zagara, it creates new zergling and kills it  (WTF)
                if _old_unit_type == 'BanelingCocoon' and _unit_type == 'HotSSwarmling':
                    zagaras_dummy_zerglings.add(unitid(event))
                    continue

                # Don't add into created units if it's just a morph
                # Don't count wreckages morhping back
                # Don't count certain unit spawns (Murvar, Glevig, Broodlings from Broodlords)
                # Don't count mengsk trooper and labourer as new unit created when they morph
                if (UnitNameDict[_unit_type] != UnitNameDict[_old_unit_type] and not _old_unit_type in UnitAddLossesTo
                        and not (unit_id in glevig_spawns or unit_id in murvar_spawns or is_broodlord_broodling(_unit_type, unit_id))
                        and not _unit_type in dont_count_morphs):

                    # Increase unit type created for controlling player
                    if main_player == _control_pid:
                        if _unit_type in unit_type_dict_main:
                            unit_type_dict_main[_unit_type][0] += 1
                        else:
                            unit_type_dict_main[_unit_type] = [1, 0, 0, 0]

                    elif ally_player == _control_pid:
                        if _unit_type in unit_type_dict_ally:
                            unit_type_dict_ally[_unit_type][0] += 1
                        else:
                            unit_type_dict_ally[_unit_type] = [1, 0, 0, 0]

                    elif _control_pid in amon_players:
                        if _unit_type in unit_type_dict_amon:
                            unit_type_dict_amon[_unit_type][0] += 1
                        else:
                            unit_type_dict_amon[_unit_type] = [1, 0, 0, 0]
                else:
                    if main_player == _control_pid and not (_unit_type in unit_type_dict_main):
                        unit_type_dict_main[_unit_type] = [0, 0, 0, 0]

                    if ally_player == _control_pid and not (_unit_type in unit_type_dict_ally):
                        unit_type_dict_ally[_unit_type] = [0, 0, 0, 0]

                    if _control_pid in amon_players and not (_unit_type in unit_type_dict_amon):
                        unit_type_dict_amon[_unit_type] = [0, 0, 0, 0]

        # Update ownership
        if event['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent' and unitid(event) in unit_dict:

            # Mind-controlled units
            _losing_player = unit_dict[unitid(event)][1]

            if event['m_controlPlayerId'] == main_player and _losing_player in amon_players:
                mind_controlled_units.add(unitid(event))
                if not 'mc' in replay_report_dict['mainIcons']:
                    replay_report_dict['mainIcons']['mc'] = 1
                else:
                    replay_report_dict['mainIcons']['mc'] += 1
            elif event['m_controlPlayerId'] == ally_player and _losing_player in amon_players:
                mind_controlled_units.add(unitid(event))
                if not 'mc' in replay_report_dict['allyIcons']:
                    replay_report_dict['allyIcons']['mc'] = 1
                else:
                    replay_report_dict['allyIcons']['mc'] += 1

            # Update ownership
            unit_dict[unitid(event)][1] = event['m_controlPlayerId']

            # Malwarfare bonus objective. First save when the bonus started
            if 'Malwarfare' in replay['map_name']:
                _time = event['_gameloop'] / 16 - START_TIME
                if event['m_controlPlayerId'] == 9:
                    MWBonusInitialTiming[0] = _time
                elif event['m_controlPlayerId'] == 10:
                    MWBonusInitialTiming[1] = _time
                elif event['m_controlPlayerId'] == 6:
                    # Second objective, 245.9375 means it was ignored
                    if MWBonusInitialTiming[1] and _time - MWBonusInitialTiming[1] != 245.9375:
                        bonus_timings.append(_time)
                    # First objective
                    if MWBonusInitialTiming[0] and not MWBonusInitialTiming[1] and _time - MWBonusInitialTiming[0] != 245.9375:
                        bonus_timings.append(_time)

        # Update some kill stats
        if event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent':
            try:
                _killed_unit_type = unit_dict[unitid(event)][0]
                _losing_player = unit_dict[unitid(event)][1]
                _killing_player = event['m_killerPlayerId']

                # Count kills for players
                if _killing_player is not None and not _killed_unit_type in do_not_count_kills:
                    if _killing_player in (1, 2) and not _losing_player in amon_players:
                        pass
                    elif _killing_player in amon_players and not _losing_player in (1, 2):
                        pass
                    # Count ally kills to the main player if ally quits early
                    elif _killing_player == ally_player and user_leave_times.get(ally_player, END_TIME) < END_TIME * 0.5:
                        killcounts[main_player] += 1
                        ally_kills_counted_toward_main += 1
                    else:
                        killcounts[_killing_player] += 1

                # Get last_aoe_unit_killed (used when player units die without a killing unit, it was likely some enemy caster casting persistent AoE spell)
                if _killed_unit_type in aoe_units and _killing_player in [1, 2] and _losing_player in amon_players and unitid(event) is not None:
                    last_aoe_unit_killed[_losing_player] = [_killed_unit_type, event['_gameloop'] / 16]

            except Exception:
                logger.error(traceback.format_exc())

        # More kill stats
        if event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent' and unitid(event) in unit_dict:
            try:
                _killing_unit_id = unitid(event, killer=True)
                _killing_player = event['m_killerPlayerId']
                unit_id = unitid(event)
                _killed_unit_type = unit_dict[unit_id][0]
                _losing_player = int(unit_dict[unit_id][1])
                _commander = commander_fallback.get(_killing_player, None)

                # Get killing unit
                if _killing_unit_id in unit_dict and unitid(event) is not None:  # We have a killing unit
                    _killing_unit_type = unit_dict[_killing_unit_id][0]
                elif _commander is not None:
                    """
                    For no-unit, check if we default to some commander no-unit like airstrike, or use 'NoUnit'
                    But lets use this only rarely. Units killed in transports count for this as well.
                    Other not counted sources: Dusk Wings lifting off, CoD explosion, ...
                    """
                    _killing_unit_type = 'NoUnit'
                    backup_units = commander_no_units.get(_commander, [])
                    d = unit_type_dict_main if _killing_player == main_player else unit_type_dict_ally

                    for backup_unit in backup_units:
                        if backup_unit in d:
                            _killing_unit_type = backup_unit
                            break
                else:
                    _killing_unit_type = 'NoUnit'

                # Killbot feed
                if _killing_unit_type in ('MutatorKillBot', 'MutatorDeathBot', 'MutatorMurderBot') and _losing_player in [1, 2]:
                    killbot_feed[_losing_player] += 1

                # Abathur locusts
                if _killing_unit_type == 'Locust' and _commander == 'Abathur' and not _killing_unit_id in AbathurKillLocusts:
                    if _killing_player == main_player and "SwarmHost" in unit_type_dict_main:
                        _killing_unit_type = 'SwarmHost'
                    if _killing_player == ally_player and "SwarmHost" in unit_type_dict_ally:
                        _killing_unit_type = 'SwarmHost'

                # Glevig's spawns
                elif _killing_unit_type in {'DehakaZerglingLevel2', 'DehakaRoachLevel2', 'DehakaHydraliskLevel2'
                                            } and _killing_unit_id in glevig_spawns:
                    _killing_unit_type = 'Glevig'

                # Murvars's spawns
                elif _killing_unit_type in {'DehakaLocust', 'DehakaCreeperFlying', 'DehakaLocustFlying', 'DehakaCreeper'
                                            } and _killing_unit_id in murvar_spawns:
                    _killing_unit_type = 'Murvar'

                # Kerrigan's and Stetmann's Broodlings
                elif is_broodlord_broodling(_killing_unit_type, _killing_unit_id):
                    if _killing_unit_type == 'Broodling':
                        _killing_unit_type = 'BroodLord'
                    elif _killing_unit_type == 'BroodlingStetmann':
                        _killing_unit_type = 'BroodLordStetmann'

                # Custom kill count
                if _killing_player in [1, 2] and _losing_player in amon_players:
                    if _killed_unit_type in HFTS_Units:
                        if not 'hfts' in custom_kill_count:
                            custom_kill_count['hfts'] = {1: 0, 2: 0}
                        custom_kill_count['hfts'][_killing_player] += 1

                    if _killed_unit_type in TUS_Units:
                        if not 'tus' in custom_kill_count:
                            custom_kill_count['tus'] = {1: 0, 2: 0}
                        custom_kill_count['tus'][_killing_player] += 1

                    if _killed_unit_type == "ProtossFrigate":
                        if not 'shuttles' in custom_kill_count:
                            custom_kill_count['shuttles'] = {1: 0, 2: 0}
                        custom_kill_count['shuttles'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorPropagator':
                        if not 'propagators' in custom_kill_count:
                            custom_kill_count['propagators'] = {1: 0, 2: 0}
                        custom_kill_count['propagators'][_killing_player] += 1

                    elif _killed_unit_type in {'MutatorSpiderMine', 'MutatorSpiderMineBurrowed', 'WidowMineBurrowed', 'WidowMine'}:
                        if not 'minesweeper' in custom_kill_count:
                            custom_kill_count['minesweeper'] = {1: 0, 2: 0}
                        custom_kill_count['minesweeper'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorVoidRift':
                        if not 'voidrifts' in custom_kill_count:
                            custom_kill_count['voidrifts'] = {1: 0, 2: 0}
                        custom_kill_count['voidrifts'][_killing_player] += 1

                    elif _killed_unit_type in {'MutatorTurkey', 'MutatorTurking', 'MutatorInfestedTurkey'}:
                        if not 'turkey' in custom_kill_count:
                            custom_kill_count['turkey'] = {1: 0, 2: 0}
                        custom_kill_count['turkey'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorVoidReanimator':
                        if not 'voidreanimators' in custom_kill_count:
                            custom_kill_count['voidreanimators'] = {1: 0, 2: 0}
                        custom_kill_count['voidreanimators'][_killing_player] += 1

                    elif _killed_unit_type in {'InfestableBiodome', 'JarbanInfestibleColonistHut', 'InfestedMercHaven', 'InfestableHut'}:
                        if not 'deadofnight' in custom_kill_count:
                            custom_kill_count['deadofnight'] = {1: 0, 2: 0}
                        custom_kill_count['deadofnight'][_killing_player] += 1

                    elif _killed_unit_type in {
                            'MutatorMissileSplitterChild', 'MutatorMissileNuke', 'MutatorMissileSplitter', 'MutatorMissileStandard',
                            'MutatorMissilePointDefense'
                    }:
                        if not 'missilecommand' in custom_kill_count:
                            custom_kill_count['missilecommand'] = {1: 0, 2: 0}
                        custom_kill_count['missilecommand'][_killing_player] += 1

                # If an enemy mutator spider mine kills something, counts a kill for the first player who lost a unit to it
                if _losing_player in [1, 2] and _killing_player in amon_players:
                    if _killing_unit_type == 'MutatorSpiderMine' and not _killing_unit_id in UsedMutatorSpiderMines:
                        UsedMutatorSpiderMines.add(_killing_unit_id)  # Count each mutator spider mine only once
                        if not 'minesweeper' in custom_kill_count:
                            custom_kill_count['minesweeper'] = {1: 0, 2: 0}
                        custom_kill_count['minesweeper'][_losing_player] += 1
                """Fix kills for some enemy area-of-effect units that kills player units after they are dead.
                   This is the best guess, if one of aoe_units died recently, it was likely that one. """
                if _killing_unit_type == 'NoUnit' and _killing_unit_id is None and _killing_player in amon_players and _losing_player != _killing_player:
                    if event['_gameloop'] / 16 - last_aoe_unit_killed[_killing_player][1] < 9 and last_aoe_unit_killed[_killing_player][0] is not None:
                        unit_type_dict_amon[last_aoe_unit_killed[_killing_player][0]][2] += 1
                        logger.debug(
                            f'{last_aoe_unit_killed[_killing_player][0]}({_killing_player}) killed {_killed_unit_type} | {event["_gameloop"]/16}s')

                # Update unit kill stats
                if ((_killing_unit_id in unit_dict) or _killing_unit_type in commander_no_units_values) and (
                        _killing_unit_id != unitid(event)) and _losing_player != _killing_player and _killed_unit_type not in do_not_count_kills:
                    if main_player == _killing_player and _losing_player in amon_players:
                        if _killing_unit_type in unit_type_dict_main:
                            unit_type_dict_main[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_main[_killing_unit_type] = [0, 0, 1, 0]

                    if ally_player == _killing_player and _losing_player in amon_players:
                        if _killing_unit_type in unit_type_dict_ally:
                            unit_type_dict_ally[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_ally[_killing_unit_type] = [0, 0, 1, 0]

                    if _killing_player in amon_players and _losing_player in (1, 2):
                        if _killing_unit_type in unit_type_dict_amon:
                            unit_type_dict_amon[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_amon[_killing_unit_type] = [0, 0, 1, 0]

                # Update unit death stats
                # Don't count self kills like Fenix switching suits
                if _killed_unit_type in self_killing_units and _killing_player is None:
                    if main_player == _losing_player:
                        unit_type_dict_main[_killed_unit_type][0] -= 1
                    if ally_player == _losing_player:
                        unit_type_dict_ally[_killed_unit_type][0] -= 1
                    continue

                # Fix for units like Raptorlings that are counted each time they jump (as death and birth)
                if event[
                        '_gameloop'] / 16 > 0 and _killed_unit_type in duplicating_units and _killed_unit_type == _killing_unit_type and _losing_player == _killing_player:
                    if main_player == _losing_player:
                        unit_type_dict_main[_killed_unit_type][0] -= 1
                        continue
                    if ally_player == _losing_player:
                        unit_type_dict_ally[_killed_unit_type][0] -= 1
                        continue
                    if _killing_player in amon_players:
                        unit_type_dict_amon[_killed_unit_type][0] -= 1
                        continue

                # In case of death caused by Archon merge, ignore these kills
                if _killed_unit_type in ('HighTemplar', 'DarkTemplar') and DT_HT_Ignore[_losing_player] > 0:
                    DT_HT_Ignore[_losing_player] -= 1
                    continue
                """
                Bonus objectives
                Mostly kills here. Sometimes checking killing player to prevent despawns from counting.
                In case of trains, killing player is almost always None, and so I'm checking the position of the train.

                """
                if ('Void Thrashing' in replay['map_name'] and _killed_unit_type in {'ArchAngelCoopFighter','ArchAngelCoopAssault'} and _losing_player == 5) or \
                   ('Dead of Night' in replay['map_name'] and 'ACVirophage' == _killed_unit_type and _losing_player == 7 and _killing_player in {1,2}) or \
                   (('Lock & Load' in replay['map_name'] or '[MM] LnL' in replay['map_name']) and 'XelNagaConstruct' == _killed_unit_type and _losing_player == 3) or \
                   ('Chain of Ascension' in replay['map_name'] and 'SlaynElemental' == _killed_unit_type and _losing_player == 10 and _killing_player in {1,2}) or \
                   ('Rifts to Korhal' in replay['map_name'] and 'ACPirateCapitalShip' == _killed_unit_type and _losing_player == 8 and _killing_player in {1,2}) or \
                   ('Cradle of Death' in replay['map_name'] and 'LogisticsHeadquarters' == _killed_unit_type and _losing_player == 3) or \
                   ('Part and Parcel' in replay['map_name'] and _killed_unit_type in {'Caboose','TarsonisEngine'}
                        and not round(event['_gameloop']/16 - START_TIME,0) in bonus_timings
                        and len(bonus_timings) < 2
                        and _losing_player == 8
                        and not (event['m_x'] == 169
                        and event['m_y'] == 99)
                        and not (event['m_x'] == 38
                        and event['m_y'] == 178)) or \
                   ('Oblivion Express' in replay['map_name'] and 'TarsonisEngineFast' == _killed_unit_type and _losing_player == 7 and event['m_x'] < 196) or \
                   ('Mist Opportunities' in replay['map_name'] and 'COOPTerrazineTank' == _killed_unit_type and _losing_player == 3 and _killing_player in {1,2}) or \
                   ('The Vermillion Problem' in replay['map_name'] and _killed_unit_type in {'RedstoneSalamander','RedstoneSalamanderBurrowed'} and _losing_player == 9 and _killing_player in {1,2}) or \
                   ('Miner Evacuation' in replay['map_name'] and _killed_unit_type == 'Blightbringer' and  _losing_player == 5 and _killing_player in {1,2}) or \
                   ('Miner Evacuation' in replay['map_name'] and _killed_unit_type == 'NovaEradicator' and  _losing_player == 9 and unit_type_dict_amon[_killed_unit_type][1] == 1 and _killing_player in {1,2}) or \
                   ('Temple of the Past' in replay['map_name'] and _killed_unit_type == 'ZenithStone' and _losing_player == 8):

                    # Time offset for Cradle of Death as the explosion is delayed
                    if 'Cradle of Death' in replay['map_name']:
                        bonus_timings.append(round(event['_gameloop'] / 16 - START_TIME - 8, 0))
                    else:
                        bonus_timings.append(round(event['_gameloop'] / 16 - START_TIME, 0))

                # Don't save salvaged units
                if _killed_unit_type in salvage_units and _losing_player == _killing_player:
                    if _losing_player == main_player:
                        mainStatsCounter.salvaged_units.append(_killed_unit_type)
                    elif _losing_player == ally_player:
                        allyStatsCounter.salvaged_units.append(_killed_unit_type)

                # Don't include salvage and spawns
                if (_killed_unit_type in salvage_units and _losing_player == _killing_player) \
                    or unit_id in glevig_spawns \
                    or unit_id in murvar_spawns \
                    or is_broodlord_broodling(_killed_unit_type, unit_id):
                    continue

                # Don't add losses to dummy zerglings killed when banelings are finished
                if unit_id in zagaras_dummy_zerglings and event['m_killerPlayerId'] is None:
                    continue

                # Don't count base Roaches morphing into Brutalisks (unlike RoachVile, these count as dead when morphing)
                # RavagerAbathur are killed as well
                if _killed_unit_type in {'Roach','RavagerAbathur','RoachVileBurrowed','RoachBurrowed','SwarmHostBurrowed','QueenBurrowed'} \
                    and commander_fallback.get(_losing_player) == 'Abathur' \
                    and event['m_killerPlayerId'] is None:
                    continue

                # Don't count Drone losses without killing player
                if _killed_unit_type == 'Drone' and event.get('m_killerPlayerId') is None:
                    continue

                # Add losses
                if main_player == _losing_player and event['_gameloop'] / 16 > 0 and event[
                        '_gameloop'] / 16 > START_TIME + 1:  # Don't count deaths on game init
                    if _killed_unit_type in unit_type_dict_main:
                        unit_type_dict_main[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_main[_killed_unit_type] = [0, 1, 0, 0]

                    # Saving what killed what
                    if _killed_unit_type not in unit_killed_by:
                        unit_killed_by[_killed_unit_type] = [_killing_unit_type]
                    else:
                        unit_killed_by[_killed_unit_type].append(_killing_unit_type)

                    if unit_id in mind_controlled_units:
                        mainStatsCounter.mindcontrolled_unit_dies(_killed_unit_type)

                if ally_player == _losing_player and event['_gameloop'] / 16 > 0 and event['_gameloop'] / 16 > START_TIME + 1:
                    if _killed_unit_type in unit_type_dict_ally:
                        unit_type_dict_ally[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_ally[_killed_unit_type] = [0, 1, 0, 0]

                    if unit_id in mind_controlled_units:
                        allyStatsCounter.mindcontrolled_unit_dies(_killed_unit_type)

                if _losing_player in amon_players and event['_gameloop'] / 16 > 0 and event['_gameloop'] / 16 > START_TIME + 1 and not unitid(
                        event) in MutatorDehakaDragUnitIDs:
                    if _killed_unit_type in unit_type_dict_amon:
                        unit_type_dict_amon[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_amon[_killed_unit_type] = [0, 1, 0, 0]

            except Exception:
                logger.error(traceback.format_exc())

    # Save data about what killed trakced units in the log
    for unit in unit_killed_by:
        if unit_type_dict_main[unit][2] > 0 and print_killby:
            d = {u: unit_killed_by[unit].count(u) for u in unit_killed_by[unit]}
            d = {k: v for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)}
            logger.info(f"What killed {unit}? {d}")

    # Save more data to final dictionary
    replay_report_dict['player_stats'] = {
        1: mainStatsCounter.get_stats(replay_report_dict['main']),
        2: allyStatsCounter.get_stats(replay_report_dict['ally'])
    }
    replay_report_dict['bonus'] = tuple(time.strftime('%M:%S', time.gmtime(i)) for i in bonus_timings)
    replay_report_dict['comp'] = get_enemy_comp(identified_waves)
    replay_report_dict['length'] = replay['accurate_length'] / 1.4
    del replay['events']
    replay_report_dict['parser'] = replay
    replay_report_dict['mutators'] = replay['mutators']
    replay_report_dict['weekly'] = replay['weekly']

    # Update messages with player leave times
    messages = list(replay_report_dict['parser']['messages'])
    for player in user_leave_times:
        if player in {1, 2}:
            messages.append({'player': player, 'text': f"*has left the game*", 'time': user_leave_times[player]})
    messages = sorted(messages, key=lambda x: x['time'])
    replay_report_dict['parser']['messages'] = tuple(messages)

    # from pprint import pprint
    # pprint(unit_type_dict_main)
    # pprint(unit_type_dict_ally)

    # Main player
    replay_report_dict['mainCommander'] = replay['players'][main_player].get('commander', '')
    replay_report_dict['mainCommanderLevel'] = replay['players'][main_player].get('commander_level', 0)
    replay_report_dict['mainMasteries'] = replay['players'][main_player].get('masteries', (0, 0, 0, 0, 0, 0))
    replay_report_dict['mainkills'] = killcounts[main_player]
    replay_report_dict['mainPrestige'] = PrestigeTalents[main_player]
    if replay_report_dict['mainPrestige'] is None:
        replay_report_dict['mainPrestige'] = replay['players'][main_player].get('prestige_name', '')

    # Ally player
    replay_report_dict['allyCommander'] = replay['players'][ally_player].get('commander', '')
    replay_report_dict['allyCommanderLevel'] = replay['players'][ally_player].get('commander_level', 0)
    replay_report_dict['allyMasteries'] = replay['players'][ally_player].get('masteries', (0, 0, 0, 0, 0, 0))
    replay_report_dict['allykills'] = killcounts[ally_player]
    replay_report_dict['allyPrestige'] = PrestigeTalents[ally_player]
    if replay_report_dict['allyPrestige'] is None:
        replay_report_dict['allyPrestige'] = replay['players'][ally_player].get('prestige_name', '')

    # Fallback
    if replay_report_dict['mainCommander'] == '':
        replay_report_dict['mainCommander'] = commander_fallback.get(main_player, "")

    if replay_report_dict['allyCommander'] == '':
        replay_report_dict['allyCommander'] = commander_fallback.get(ally_player, "")

    # MM mastery fallback
    if '[MM]' in filepath:
        replay_report_dict['mainMasteries'] = tuple(mastery_fallback[main_player])
        replay_report_dict['allyMasteries'] = tuple(mastery_fallback[ally_player])

        # Assume commander level of 15
        replay_report_dict['mainCommanderLevel'] = 15
        replay_report_dict['allyCommanderLevel'] = 15

    # Icons: Tychus' Outlaws
    if replay_report_dict.get('mainCommander', None) == 'Tychus':
        replay_report_dict['mainIcons']['outlaws'] = outlaw_order
    elif replay_report_dict.get('allyCommander', None) == 'Tychus':
        replay_report_dict['allyIcons']['outlaws'] = outlaw_order

    # Icons: Kills
    # First decide between hfts and tus
    if 'tus' in custom_kill_count and 'hfts' in custom_kill_count:
        custom_kill_count['tus'][1] += custom_kill_count['hfts'][1]
        custom_kill_count['tus'][2] += custom_kill_count['hfts'][2]
        del custom_kill_count['hfts']

    for item in {'hfts', 'tus', 'propagators', 'voidrifts', 'turkey', 'voidreanimators', 'deadofnight', 'minesweeper', 'missilecommand', 'shuttles'}:
        if item in custom_kill_count:
            # Skip if it's not a Dead of Night map
            if item == 'deadofnight' and 'Dead of Night' not in replay['map_name']:
                continue

            # Skip if just mines died, not a mutation
            if item == 'minesweeper' and 'MutatorSpiderMine' not in unit_type_dict_amon:
                continue

            replay_report_dict['mainIcons'][item] = custom_kill_count[item][main_player]
            replay_report_dict['allyIcons'][item] = custom_kill_count[item][ally_player]

    # Don't post if no commander, likely non-coop replay
    if replay_report_dict['mainCommander'] == '':
        logger.error('Not a Co-op replay')

    def fill_unit_kills_and_icons(player, pdict):
        """ Fills units into output dictionary, fill created/list units into icons """

        unitkey = 'mainUnits' if player == main_player else 'allyUnits'
        iconkey = 'mainIcons' if player == main_player else 'allyIcons'
        replay_report_dict[unitkey] = dict()

        # Go through raw dictionary with raw unit names
        for unit in pdict:
            if unit in {'AbathurLocust', 'Locust', 'LocustMP', 'DehakaCreeperFlying', 'DehakaLocust'}:
                replay_report_dict[iconkey]['locust'] = replay_report_dict[iconkey].get('locust', 0) + pdict[unit][0]
            elif unit in {
                    'BroodlingEscortStetmann', 'BroodlingEscort', 'Broodling', 'KerriganInfestBroodling', 'StukovInfestBroodling', 'BroodlingStetmann'
            }:
                replay_report_dict[iconkey]['broodling'] = replay_report_dict[iconkey].get('broodling', 0) + pdict[unit][0]

        # Delete broodling/locust if the number isn't significant
        for unit in ('broodling', 'locust'):
            if 0 < replay_report_dict[iconkey].get(unit, 0) < 200:
                del replay_report_dict[iconkey][unit]

        # Switch names, sort, etc.
        new_dict = switch_names(pdict)
        sorted_dict = {
            k: v
            for k, v in sorted(new_dict.items(), reverse=True, key=lambda item: item[1][0])
        }  # Sorts by number of create (0), lost (1), kills (2), K/D (3)
        sorted_dict = {k: v for k, v in sorted(sorted_dict.items(), reverse=True, key=lambda item: item[1][2])}

        # Go through new dictionary
        for unit in sorted_dict:
            replay_report_dict[unitkey][unit] = sorted_dict[unit]

            # Calculating kill fractions. In case of ally leaving, we want to adjust killcounts[player] with kills counted towards the main.
            if ally_kills_counted_toward_main > 0 and unitkey == 'allyUnits' and (killcounts[player] + ally_kills_counted_toward_main) > 0:
                replay_report_dict[unitkey][unit][3] = round(
                    replay_report_dict[unitkey][unit][2] / (killcounts[player] + ally_kills_counted_toward_main), 2)
            elif ally_kills_counted_toward_main > 0 and unitkey == 'mainUnits' and (killcounts[player] - ally_kills_counted_toward_main) > 0:
                replay_report_dict[unitkey][unit][3] = round(
                    replay_report_dict[unitkey][unit][2] / (killcounts[player] - ally_kills_counted_toward_main), 2)
            elif killcounts[player] > 0:
                replay_report_dict[unitkey][unit][3] = round(replay_report_dict[unitkey][unit][2] / killcounts[player], 2)
            else:
                replay_report_dict[unitkey][unit][3] = 0

            # Copy created & lost stats from Dehaka
            if unit == 'Zweihaka' and 'Dehaka' in sorted_dict:
                replay_report_dict[unitkey][unit][0] = sorted_dict['Dehaka'][0]
                replay_report_dict[unitkey][unit][1] = sorted_dict['Dehaka'][1]

            if unit in dont_show_created_lost:
                replay_report_dict[unitkey][unit][0] = '-'
                replay_report_dict[unitkey][unit][1] = '-'

            # Icons: Created units
            if unit in icon_units:
                replay_report_dict[iconkey][unit] = sorted_dict[unit][0]

        # Icons: Artifacts and used projections
        Zeratul_artifacts_collected = 0
        for unit in pdict:
            if unit in ('ZeratulArtifactPickup1', 'ZeratulArtifactPickup2', 'ZeratulArtifactPickup3', 'ZeratulArtifactPickupUnlimited'):
                Zeratul_artifacts_collected += pdict[unit][1]

            if unit in ['ZeratulKhaydarinMonolithProjection', 'ZeratulPhotonCannonProjection']:
                if 'ShadeProjection' in replay_report_dict[iconkey]:
                    replay_report_dict[iconkey]['ShadeProjection'] += pdict[unit][0]
                else:
                    replay_report_dict[iconkey]['ShadeProjection'] = pdict[unit][0]

        if Zeratul_artifacts_collected > 0:
            replay_report_dict[iconkey]['Artifact'] = Zeratul_artifacts_collected

        # Tuple
        for unit in replay_report_dict[unitkey]:
            replay_report_dict[unitkey][unit] = tuple(replay_report_dict[unitkey][unit])

    fill_unit_kills_and_icons(main_player, unit_type_dict_main)
    fill_unit_kills_and_icons(ally_player, unit_type_dict_ally)

    # Icons: Killbots
    if killbot_feed[main_player] > 0:
        replay_report_dict['mainIcons']['killbots'] = killbot_feed[main_player]
    if killbot_feed[ally_player] > 0:
        replay_report_dict['allyIcons']['killbots'] = killbot_feed[ally_player]

    # Amon kills
    sorted_amon = switch_names(unit_type_dict_amon)
    sorted_amon = {k: v for k, v in sorted(sorted_amon.items(), reverse=True, key=lambda item: item[1][0])}
    sorted_amon = {k: v for k, v in sorted(sorted_amon.items(), reverse=True, key=lambda item: item[1][2])}

    # Get total amount of kills from Amon
    total_amon_kills = 0
    for player in amon_players:
        total_amon_kills += killcounts[player]
    total_amon_kills = total_amon_kills if total_amon_kills != 0 else 1

    # Calculate Amon unit percentages and fill data
    replay_report_dict['amon_units'] = dict()

    for unit in sorted_amon:
        if not contains_skip_strings(unit):
            replay_report_dict['amon_units'][unit] = sorted_amon[unit]
            replay_report_dict['amon_units'][unit][3] = round(replay_report_dict['amon_units'][unit][2] / total_amon_kills, 2)

    # Tuple
    for unit in replay_report_dict['amon_units']:
        replay_report_dict['amon_units'][unit] = tuple(replay_report_dict['amon_units'][unit])

    return replay_report_dict


def extract_difficulty(data):
    """从回放数据中提取游戏难度 (1-5)"""
    # 移植自 real_data_server.py
    if 'difficulty' in data:
        diff = data['difficulty']
        if isinstance(diff, tuple) and len(diff) > 0:
            diff_name = diff[0]
            difficulty_map = {'Casual': 1, 'Normal': 2, 'Hard': 3, 'Brutal': 4, 'Brutal+': 5}
            return difficulty_map.get(diff_name, 4)
        elif isinstance(diff, str):
            difficulty_map = {'Casual': 1, 'Normal': 2, 'Hard': 3, 'Brutal': 4, 'Brutal+': 5}
            return difficulty_map.get(diff, 4)
    
    # 检查是否有Brutal+信息
    if data.get('B+'):
        return 5
    
    # 在 analyse_parsed_replay 中 'difficulty' 字段可能已经是 'Brutal'
    if data.get('difficulty') == 'Brutal':
        return 4
    if data.get('difficulty') == 'Hard':
        return 3
    if data.get('difficulty') == 'Normal':
        return 2
    if data.get('difficulty') == 'Casual':
        return 1

    return 4  # 默认Brutal


def calculate_resource_efficiency(player_data):
    """计算资源效率"""
    # 简化计算：基于APM和游戏结果 (移植自 real_data_server.py)
    base_score = 50
    if player_data.get('result') == 'Win':
        base_score += 20
    apm = player_data.get('apm', 100)
    return min(100, base_score + (apm / 10))


def calculate_unit_control_score(player_data):
    """计算单位控制评分"""
    # 基于APM和击杀数 (移植自 real_data_server.py)
    apm = player_data.get('apm', 100)
    kills = player_data.get('kills', 0)
    return min(100, (apm / 2) + (kills / 10))


def calculate_sync_score(replay_data):
    """计算协同作战评分"""
    # 简化：基于游戏结果和时长 (移植自 real_data_server.py)
    base_score = 50
    if replay_data.get('result') == 'Victory':
        base_score += 30
    # 游戏时长越接近20分钟，协同分越高
    game_length = replay_data.get('length', 1200)
    if 900 <= game_length <= 1500:  # 15-25分钟
        base_score += 20
    return min(100, base_score)


def extract_game_factors(replay_data, game_id):
    """从回放数据中提取游戏因子 (移植自 real_data_server.py)"""
    factors = {
        'game_id': game_id,
        'map_factors': {
            'map_name': replay_data.get('map_name', 'Unknown'),
            'map_size': 'medium',
            'enemy_composition': replay_data.get('comp', 'Mixed'),
            'objective_type': 'standard'
        },
        'performance_factors': {},
        'combat_factors': {
            'total_kills': 0,
            'kill_death_ratio': 0,
            'damage_dealt': 0,
            'damage_taken': 0
        },
        'cooperation_factors': {
            'sync_score': 0,
            'resource_sharing': 0,
            'combined_attacks': 0
        },
        'difficulty_factors': {
            'base_difficulty': extract_difficulty(replay_data),
            'mutators': replay_data.get('mutators', []),
            'adjusted_difficulty': extract_difficulty(replay_data)
        },
        'time_factors': {
            'game_length': replay_data.get('length', 0),
            'early_game_score': 0,
            'mid_game_score': 0,
            'late_game_score': 0
        }
    }

    # 提取玩家数据
    players_data = []
    # main player
    players_data.append({
        'name': replay_data.get('main'),
        'commander': replay_data.get('mainCommander'),
        'apm': replay_data.get('mainAPM'),
        'kills': replay_data.get('mainkills'),
        'result': 'Win' if replay_data.get('result') == 'Victory' else 'Loss'
    })
    # ally player
    players_data.append({
        'name': replay_data.get('ally'),
        'commander': replay_data.get('allyCommander'),
        'apm': replay_data.get('allyAPM'),
        'kills': replay_data.get('allykills'),
        'result': 'Win' if replay_data.get('result') == 'Victory' else 'Loss'
    })

    for i, player in enumerate(players_data):
        player_key = f'player{i+1}'
        factors['performance_factors'][player_key] = {
            'name': player.get('name', f'Player{i+1}'),
            'commander': player.get('commander', 'Unknown'),
            'apm': player.get('apm', 0),
            'resource_efficiency': calculate_resource_efficiency(player),
            'unit_control_score': calculate_unit_control_score(player)
        }
        
        # 累加战斗因子
        factors['combat_factors']['total_kills'] += player.get('kills', 0)

    # 计算协作分数
    factors['cooperation_factors']['sync_score'] = calculate_sync_score(replay_data)
    
    return factors


def parse_and_analyse_replay(filepath, main_player_handles=None):
    """ Analyses the replay and returns the analysis"""
    logger.info(f'Analysing: {filepath}')
    replay = None

    # Load the replay
    try:
        replay = parse_replay_file(filepath)
    except Exception:
        logger.error(f'Parsing error ({filepath})\n{traceback.format_exc()}')
        return {}

    return analyse_parsed_replay(filepath, replay, main_player_handles)
