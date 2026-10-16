"""Z4: draw the seeded spot-check sample (keys only, no prior answers) to work/spot_in.txt."""
import random

import zone_config as Z
from zone_common import zone_keys

keys = random.Random(Z.SPOT_SEED).sample(zone_keys(), Z.SPOT_SIZE)
(Z.WORK / "spot_in.txt").write_text("".join(f"{c} | {p}\n" for c, p in keys), encoding="utf-8")
print(len(keys), "sampled, seed", Z.SPOT_SEED)
