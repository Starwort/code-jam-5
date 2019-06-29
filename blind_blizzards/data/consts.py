import enum
from discord import Colour

### GENERAL ###


# team logo
EMBED_THUMBNAIL = "https://i.imgur.com/xaqlfLO.png"

# colour for 'magic embeds'; that is, embeds appearing to have no
# coloured sidebar
MAGIC_EMBED_COLOUR = Colour(0x36393E)


### cogs.interactive / data.interactive ###
class AlignmentField(enum.Enum):
    # for standard alignment, X = lawful/chaotic
    X = 0
    # Y = good/evil
    Y = 1
    # If an answer does not shift one's alignment
    NONE = None


OPTION_EMOJI = ["🇦", "🇧", "🇨", "🇩", "🇪"]
EMOJI_TO_INT = {emoji: index for index, emoji in enumerate(OPTION_EMOJI)}
# 5 options
CANCEL = "❌"
