import asyncio
import html
import re

from pydantic import BaseModel, Field, model_validator
from requests_html import AsyncHTMLSession
from sqlalchemy import select

from database.models import Song

URL = "https://holychords.pro"
chord_regex = r"^[A-H][b#]?(2|5|6|7|9|11|13|\+|\+2|\+4|\+5|\+6|\+7|\+9|\+11|\+13|6/9|7-5|7-9|7#5|#5|7#9|#9|7+3|7+5|7+9|7b5|7b9|7sus2|7sus4|add2|add4|add6|add9|aug|dim|dim7|m/maj7|m6|m7|m7b5|m9|m11|m13|maj|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4|m7add11|add11|b5|-5|4)*(/[A-H][b#]*)*$"
videlit = (
    r"(1\|)|(2\|)|(3\|)|(4\|)|(5\|)|(6\|)|1:|2:|3:|4:|5:|6:|7:|8:|9:|0:|вступление:|интро:|куплет:|припев:|переход:|реп:|мост:|мостик:|вставка:|речитатив:|бридж:|инструментал:|проигрыш:|запев:|концовка:|окончание:|в конце:|кода:|тэг:|стих:|слово:|декла"
    "мация:|intro:|verse:|chorus:|bridge:|instrumental:|build:|ending:|link:|outro:|interlude:|rap:|spontaneous:|refrain:|tag:|coda:|vamp:|channel:|break:|breakdown:|hook:|turnaround:|turn:|solo:|вступ:|інтро:|приспів:|інструментал:|"
    "інтерлюдія:|брідж:|заспів:|міст:|програш:|соло:|перехід:|повтор:|кінець:|в кінці:|фінал:|кінцівка:|закінчення:|тег:|вірш:|частина:|прыпеў:|прысьпеў:|пройгрыш:|couplet:|pont:|strofă:|refren:|verso:|coro:|puente:|refrão:|parte:|strofa:|zwrotka:|espontáneo:|chords:"
)
chord_pattern = re.compile(chord_regex)
videlit_pattern = re.compile(videlit, re.IGNORECASE)


async def get_songs(search_name: str, db_session) -> list[Song]:
    session = AsyncHTMLSession(loop=asyncio.get_event_loop())
    search_name = "+".join(search_name.split(" "))
    r = await session.get(
        f"{URL}/search?name={search_name}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    songs = [SongAPI(**s) for s in r.json()["musics"]["data"]]
    songs = await save_songs_bulk(songs, db_session)
    return songs


def get_text(text: str = None, chords: bool = False) -> str | None:
    if not text:
        return None
    text = text.split("\n")
    text = text if chords else [i for i in text if not is_chord_line(i)]
    for i, t in enumerate(text):
        if videlit_pattern.search(t.lower()):
            text[i] = f"\n<b>{t}</b>"
    return html.unescape("\n".join(text))


def is_chord_line(line: str):
    tokens = re.sub(r"\s+", " ", line).strip().split(" ")
    allowed_tokens = {"|", "/", "(", ")", "-", "x2", "x3", "x4", "x5", "x6", "•", "NC"}
    for i in tokens:
        if i.strip() and not chord_pattern.match(i) and all(j not in i for j in allowed_tokens):
            return False
    return True


class SongAPI(BaseModel):
    id: int
    name: str
    artist: str
    file: str | None = Field(None)
    text: str | None = Field(None)

    @model_validator(mode="before")
    def isp_name(cls, data: dict):
        data["file"] = f'{URL}{data["file"]}' if data["file"] else ""
        data["artist"] = (
            data["artist"]["isp_name"] if "isp_name" in data["artist"] else data["artist"]
        )
        return data


async def save_songs_bulk(songs: list[SongAPI], db_session) -> list[Song]:
    incoming_ids = [s.id for s in songs]

    stmp = select(Song).where(Song.id.in_(incoming_ids))
    db_songs = (await db_session.scalars(stmp)).all()
    existing_ids = [s.id for s in db_songs if s.id in incoming_ids]

    new_songs = [Song(id=s.id, name=s.name, artist=s.artist, file=s.file, text=s.text) for s in songs if
                 s.id not in existing_ids]

    db_songs.extend(new_songs)

    if new_songs:
        db_session.add_all(new_songs)
        try:
            await db_session.commit()
        except:
            await db_session.rollback()

    return db_songs
