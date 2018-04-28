BLOCK_TIME = 8  # generate 1 block every 2 sec
STANDARD_TARGET = int(int('f' * 64, 16) / BLOCK_TIME)  # derived from default network hash power of 1h/s
DIFF_UPDATE_PERIOD = 6


def get_difficulty(block_chain):
    if len(block_chain) < DIFF_UPDATE_PERIOD:
        difficulty = 1
    else:
        block_chunks = [
            block_chain[i:i + DIFF_UPDATE_PERIOD]
            for i in range(0, len(block_chain), DIFF_UPDATE_PERIOD)
        ]
        chunk = block_chunks[-1] if len(block_chain) % DIFF_UPDATE_PERIOD == 0 else block_chunks[-2]

        diffs = set([block.difficulty for block in chunk])
        assert len(diffs) == 1

        recent_avg_block_time = \
            (chunk[-1].timestamp - chunk[-DIFF_UPDATE_PERIOD].timestamp) / DIFF_UPDATE_PERIOD
        # min. difficulty limited @ 1
        difficulty = list(diffs)[0] * BLOCK_TIME / recent_avg_block_time
    return max(difficulty, 1)


def get_longest_chain(block_chains):
    result = None
    for chain in [c for c in block_chains if validate_chain(c)]:
        if not result or len(chain) > len(result):
            result = chain
    return result


def validate_chain(block_chain):
    return True
