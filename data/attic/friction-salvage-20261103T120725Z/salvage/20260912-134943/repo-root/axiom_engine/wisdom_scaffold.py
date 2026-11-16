import json, hashlib, sys, os

WISDOM_DATA = [
    {"id": 1, "text": "A soft answer turneth away wrath.", "source": "Proverbs 15:1"},
    {"id": 2, "text": "As a man thinketh in his heart, so is he.", "source": "Proverbs 23:7"},
    {"id": 3, "text": "Cast thy bread upon the waters: for thou shalt find it after many days.", "source": "Ecclesiastes 11:1"},
    {"id": 4, "text": "Faith is the substance of things hoped for, the evidence of things not seen.", "source": "Hebrews 11:1"},
    {"id": 5, "text": "The tree is known by his fruit.", "source": "Matthew 12:33"},
    {"id": 6, "text": "Whatsoever a man soweth, that shall he also reap.", "source": "Galatians 6:7"},
    {"id": 7, "text": "Iron sharpeneth iron; so a man sharpeneth the countenance of his friend.", "source": "Proverbs 27:17"},
    {"id": 8, "text": "Where no counsel is, the people fall: but in the multitude of counsellors there is safety.", "source": "Proverbs 11:14"},
    {"id": 9, "text": "To every thing there is a season, and a time to every purpose under the heaven.", "source": "Ecclesiastes 3:1"},
    {"id": 10, "text": "Better is a neighbor that is near than a brother far off.", "source": "Proverbs 27:10"},
    {"id": 11, "text": "A merry heart doeth good like a medicine.", "source": "Proverbs 17:22"},
    {"id": 12, "text": "Pride goeth before destruction, and an haughty spirit before a fall.", "source": "Proverbs 16:18"},
    {"id": 13, "text": "He that ruleth his spirit is better than he that taketh a city.", "source": "Proverbs 16:32"},
    {"id": 14, "text": "A good name is rather to be chosen than great riches.", "source": "Proverbs 22:1"},
    {"id": 15, "text": "If a house be divided against itself, that house cannot stand.", "source": "Mark 3:25"},
    {"id": 16, "text": "Love your enemies, bless them that curse you.", "source": "Matthew 5:44"},
    {"id": 17, "text": "Ask, and it shall be given you; seek, and ye shall find.", "source": "Matthew 7:7"},
    {"id": 18, "text": "Therefore all things whatsoever ye would that men should do to you, do ye even so to them.", "source": "Matthew 7:12"},
    {"id": 19, "text": "The truth shall make you free.", "source": "John 8:32"},
    {"id": 20, "text": "Be not overcome of evil, but overcome evil with good.", "source": "Romans 12:21"},
    {"id": 21, "text": "Knowledge puffeth up, but charity edifieth.", "source": "1 Corinthians 8:1"},
    {"id": 22, "text": "For where your treasure is, there will your heart be also.", "source": "Matthew 6:21"},
    {"id": 23, "text": "Let not the sun go down upon your wrath.", "source": "Ephesians 4:26"},
    {"id": 24, "text": "The race is not to the swift, nor the battle to the strong.", "source": "Ecclesiastes 9:11"},
    {"id": 25, "text": "Buy the truth, and sell it not; also wisdom, and instruction, and understanding.", "source": "Proverbs 23:23"}
]

def verify_seed():
    raw_bytes = json.dumps(WISDOM_DATA, sort_keys=True).encode("utf-8")
    m = hashlib.sha256(raw_bytes).hexdigest()
    print(f"Wisdom Seed: 25 records | MERKLE: {m[:12]}...")
    return True

if __name__ == "__main__":
    verify_seed()
