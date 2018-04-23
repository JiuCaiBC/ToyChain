BLOCK_TIME = 16  # generate 1 block every 2 sec
STANDARD_TARGET = int(int('f' * 64, 16) / BLOCK_TIME)  # derived from default network hash power of 1h/s
DIFF_UPDATE_PERIOD = 6


def get_target(block_chain):
    if len(block_chain) <= DIFF_UPDATE_PERIOD:
        difficulty = 1
    else:
        prev_block_period_idx = block_chain[::DIFF_UPDATE_PERIOD][-2].index
        blocks = block_chain[prev_block_period_idx:prev_block_period_idx + DIFF_UPDATE_PERIOD]

        recent_avg_block_time = \
            (blocks[-1].timestamp - blocks[-DIFF_UPDATE_PERIOD].timestamp) / DIFF_UPDATE_PERIOD
        difficulty = max(BLOCK_TIME / recent_avg_block_time, 1)  # min. difficulty limited @ 1

    target = int(STANDARD_TARGET / difficulty)
    return target


def get_longest_chain(block_chains):
    result = None
    for chain in [c for c in block_chains if validate_chain(c)]:
        if not result or len(chain) > len(result):
            result = chain
    return result


def validate_chain(block_chain):
    return True
