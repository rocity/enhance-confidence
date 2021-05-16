import random
from database import EnhanceDB, Record
from statistics import mean as stat_mean
from statistics import stdev as stat_stdev
import matplotlib.pyplot as plt

import numpy as np
import scipy.stats as st

ONE_MIL = 1000000
CRON_PRICE = 2*ONE_MIL

PRI = 'PRI'
DUO = 'DUO'
TRI = 'TRI'
TET = 'TET'
PEN = 'PEN'

HARDCAP_CHANCE = 0.9
ACCESSORY_FS_INCREASE_PER_FAIL = 1

DEFAULT_FS_MAP = {
    PRI: 25,
    DUO: 40,
    TRI: 50,
    TET: 112,
    PEN: 256
}

ACCESSORY_CHANCES = [
    {
        'level': PRI,
        'base_chance': 0.25,
        'increase_til_softcap': 0.025,
        'increase_til_hardcap': 0.005,
        'softcap': 0.7
    },
    {
        'level': DUO,
        'base_chance': 0.1,
        'increase_til_softcap': 0.01,
        'increase_til_hardcap': 0.002,
        'softcap': 0.5
    },
    {
        'level': TRI,
        'base_chance': 0.075,
        'increase_til_softcap': 0.0075,
        'increase_til_hardcap': 0.0015,
        'softcap': 0.405
    },
    {
        'level': TET,
        'base_chance': 0.025,
        'increase_til_softcap': 0.0025,
        'increase_til_hardcap': 0.0005,
        'softcap': 0.3
    },
    {
        'level': PEN,
        'base_chance': 0.005,
        'increase_til_softcap': 0.0005,
        'increase_til_hardcap': 0.0005,
        'softcap': 0.9
    }
]

def roll():
    return random.uniform(0, 1)

def calculate_accessory_enhance_chance(failstack=0, target=PRI):
    # Formula: (BaseRate x [1 + ( 0.1 x FS)])
    match = next((chance for chance in ACCESSORY_CHANCES if chance['level'] == target), None)

    if not match:
        raise BaseException('Invalid enhancement level target.')

    # Calculate which fs is the softcap
    softcap = match['softcap']
    softcap_minus_base = softcap - match['base_chance']

    needed_fs_til_softcap = softcap_minus_base / match['increase_til_softcap']

    chance_needed_til_hardcap = HARDCAP_CHANCE - softcap
    needed_fs_til_hardcap = chance_needed_til_hardcap / match['increase_til_hardcap']

    if failstack >= (needed_fs_til_softcap + needed_fs_til_hardcap):
        return HARDCAP_CHANCE

    if failstack <= needed_fs_til_softcap:
        return (failstack * match['increase_til_softcap']) + match['base_chance']

    if failstack > needed_fs_til_softcap:
        # return (needed_fs_til_softcap * match['increase_til_softcap']) + match['base_chance']
        remaining_fs_after_softcap = failstack - needed_fs_til_softcap
        return (needed_fs_til_softcap * match['increase_til_softcap']) + match['base_chance'] + (remaining_fs_after_softcap * match['increase_til_hardcap'])

    # wot do here bru
    raise BaseException('Some dumb shit i need to figure out.')

def get_next_level(item):
    current_level = item['level']
    if current_level == None:
        return PRI
    elif current_level == PRI:
        return DUO
    elif current_level == DUO:
        return TRI
    elif current_level == TRI:
        return TET
    elif current_level == TET:
        return PEN
    elif current_level == PEN:
        return None

def get_fs_for_level(target_level, fs_map):
    return fs_map[target_level]

def enhance_to_target(target=PEN, fs_map=DEFAULT_FS_MAP):
    used_bases = 0
    attempt_stats = {
        PRI: {'success': 0, 'fail': 0, 'attempts': 0},
        DUO: {'success': 0, 'fail': 0, 'attempts': 0},
        TRI: {'success': 0, 'fail': 0, 'attempts': 0},
        TET: {'success': 0, 'fail': 0, 'attempts': 0},
        PEN: {'success': 0, 'fail': 0, 'attempts': 0},
    }
    item = {
        'level': None,
    }
    while item['level'] != target:
        next_level = get_next_level(item)
        if next_level:
            if item['level']:
                used_bases = used_bases + 1
            else:
                used_bases = used_bases + 2

            chance = calculate_accessory_enhance_chance(failstack=get_fs_for_level(next_level, fs_map), target=next_level)
            rolled_chance = roll()

            if rolled_chance <= chance:
                # Enhance succeeded
                item['level'] = next_level
                attempt_stats[next_level]['success'] = attempt_stats[next_level]['success'] + 1
            else:
                # Failed, item broke. Return to level zero
                item['level'] = None
                attempt_stats[next_level]['fail'] = attempt_stats[next_level]['fail'] + 1
        else:
            print('Finished enhancing.')
            break

    clean_data = {
        'used_bases': used_bases,
        'pri_attempts': attempt_stats[PRI]['success'] + attempt_stats[PRI]['fail'],
        'pri_success': attempt_stats[PRI]['success'],
        'pri_fail': attempt_stats[PRI]['fail'],

        'duo_attempts': attempt_stats[DUO]['success'] + attempt_stats[DUO]['fail'],
        'duo_success': attempt_stats[DUO]['success'],
        'duo_fail': attempt_stats[DUO]['fail'],

        'tri_attempts': attempt_stats[TRI]['success'] + attempt_stats[TRI]['fail'],
        'tri_success': attempt_stats[TRI]['success'],
        'tri_fail': attempt_stats[TRI]['fail'],

        'tet_attempts': attempt_stats[TET]['success'] + attempt_stats[TET]['fail'],
        'tet_success': attempt_stats[TET]['success'],
        'tet_fail': attempt_stats[TET]['fail'],

        'pen_attempts': attempt_stats[PEN]['success'] + attempt_stats[PEN]['fail'],
        'pen_success': attempt_stats[PEN]['success'],
        'pen_fail': attempt_stats[PEN]['fail'],
    }
    # print('Used Bases: {}'.format(used_bases))
    # print('Attempt Stats', attempt_stats)
    record = Record(**clean_data)
    return record


class Runner:
    db_instance = None
    target_level = PEN

    def __init__(self, db_instance, target_level):
        self.db_instance = db_instance
        self.target_level = target_level

    def simulate(self, num):
        print('Simulating {} runs in reaching {} accessory...'.format(num, self.target_level))
        for x in range(0, num):
            record = enhance_to_target(self.target_level)
            self.db_instance.save_object(record)
        print('Sim done.')

    def analyze(self):
        print('Analyzing data from the db...')
        records = self.db_instance.get_records()
        data = [record.used_bases for record in records]

        sixty_eight = st.t.interval(alpha=0.68, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))
        ninety_five = st.t.interval(alpha=0.95, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))

        report_str = """
        Lowest number of bases used: {}\n
        Highest number of bases used: {}\n
        Average number of bases used: {}\n
        68percent chance to get {} within {} bases\n
        95percent chance to get {} within {} bases\n
        """.format(
            min(data),
            max(data),
            stat_mean(data),
            self.target_level, sixty_eight,
            self.target_level, ninety_five,
        )

        mean = stat_mean(data)
        sd = stat_stdev(data)
        arr = np.array(sorted(data))

        plt.plot(arr, st.norm.pdf(arr, mean, sd))
        # plt.hist(arr, 100)
        plt.title('Normal Distribution plot\n of number of base accessories used to reach {}.\n({} simulation runs)'.format(self.target_level, len(data)))
        plt.annotate(report_str, (0, 0))
        plt.show()

        print(report_str)
        print('Analysis done.')

if __name__ == '__main__':
    db = EnhanceDB()
    db.start()

    runner = Runner(db_instance=db, target_level=TET)
    # runner.simulate(100)
    runner.analyze()
